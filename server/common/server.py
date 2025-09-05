import socket
import signal
import sys
import logging
import errno
import common.utils as utils
from common.serverProtocol import ServerProtocol
import threading
from threading import Thread
from common.utilsMonitor import UtilsMonitor

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.client_id = 0
        self.clients_dictionary = {}
        self.barrier = None
        self.threads = []
        
        #atributos nuevos para fix el shutdown con el signal handler
        self._shutting_down = False
        self._accept_lock = threading.Lock()
        ######################################

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        

    def _signal_handler(self, sig, frame):

        #con este lock me aseguro que no se acepte ninguna conexion nueva/cree un thread mientras se esta cerrando el server
        with self._accept_lock:
            logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")
            self._shutting_down = True
            for client_id in list(self.clients_dictionary.keys()):
                self.clients_dictionary[client_id].close()
                del self.clients_dictionary[client_id]

            #agrego esto para destrabar los threads que puedan estar en la barrier
            if hasattr(self, 'barrier'):
                self.barrier.abort()
                
            self._server_socket.shutdown(socket.SHUT_RDWR)
            self._server_socket.close()
            for thread in self.threads:
                thread.join()

    def run(self, agencies_count):
        self.barrier = threading.Barrier(agencies_count)
        monitor = UtilsMonitor()
        while not self._shutting_down:
            try:
                with self._accept_lock:
                    if self._shutting_down:
                        break
                    client_connection = self.__accept_new_connection()
                    if client_connection:
                        self.client_id += 1
                        self.clients_dictionary[self.client_id] = client_connection
                        thread = Thread(target=self.__handle_client_connection, args=(self.client_id, client_connection, monitor))
                        thread.start()
                        self.threads.append(thread)
            except OSError as e:
                if self._shutting_down:
                    break
                if e.errno in (errno.EINTR, errno.EAGAIN):
                    continue
                
                #error critico, dejo de aceptar conexiones
                logging.error(f"action: accept_connections | result: fail | error: {e}")
                break


    def __handle_client_connection(self, client_id, client_connection, monitor: UtilsMonitor):

        agency = 0

        while True:  
            agency_id = client_connection.recv_agency_id()
            if agency_id is None:
                logging.error("action: receive_agency_id | result: fail | error: agency_id_not_received")
                client_connection.close()
                del self.clients_dictionary[client_id]
                return
            
            # si es 0, la agencia esta lista y espera a las demas
            if agency_id == 0:
                logging.info("action: agency_waiting__for_winners | result: success")
                
                #agrego este try catch por si el servidor se apaga mientras esta en la barrier alguno de los hilos
                try:
                    self.barrier.wait()
                except threading.BrokenBarrierError:
                    logging.info("action: barrier_broken | result: success")
                    return
                logging.info("action: all_agencies_ready | result: success")
                # si ya estan todas las agencias esperando, sorteo
                winners = monitor.load_winners(agency)
                client_connection.send_winners(winners)
                break
            
            agency = agency_id
            
            size_of_batch = client_connection.recv_size_of_bets_batch()
            if size_of_batch is None:
                logging.error("action: receive_batch_size | result: fail | error: number_of_bets_not_received")
                client_connection.close()
                del self.clients_dictionary[client_id]
                return
            
            batch_data = client_connection.recv_all(size_of_batch)
            if batch_data is None:
                logging.error("action: receive_bet_info | result: fail | error: bet_info_not_received")
                client_connection.close()
                del self.clients_dictionary[client_id]
                return
            
            offset = 0
            bets_received = 0
            #loop para procesar el batch, teniendo en cuenta el offset del procesamiento anterior
            while offset < len(batch_data):
                bet_info, offset = client_connection.parse_bet_info(batch_data, offset)
                name, surname, DNI, date_of_birth, num = bet_info

                bet = utils.Bet(str(agency_id), name, surname, str(DNI), date_of_birth, str(num))
                monitor.store_bet([bet])
                bets_received += 1

            logging.info(f'action: apuesta_recibida | result: success | cantidad: {bets_received}')
            client_connection.send_success_message()


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            client_connection = ServerProtocol(c)
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return client_connection
        except OSError:
            return None
