import socket
import signal
import sys
import logging
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
        # self.agencies_waiting = []
        # self.clients_agency_id = {} # ya no va a hacer falta creo
        self.barrier = None
        self.threads = []

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")

        for client_id in list(self.clients_dictionary.keys()):
            self.clients_dictionary[client_id].close()
            del self.clients_dictionary[client_id]
            
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        #joinear threads
        for thread in self.threads:
            thread.join()

    def run(self, agencies_count):
        self.barrier = threading.Barrier(agencies_count)
        while True:
            try:
                # if self.client_id >= agencies_count:
                
                # self.choose_winner(agencies_count)
                # logging.info(f"action: sorteo | result: success")
                monitor = UtilsMonitor()

                client_connection = self.__accept_new_connection()
                if client_connection:
                    self.client_id += 1
                    self.clients_dictionary[self.client_id] = client_connection
                    thread = Thread(target=self.__handle_client_connection, args=(self.client_id, client_connection, monitor))
                    thread.start()
                    self.threads.append(thread)
            except OSError as e:
                pass

    # def choose_winner(self, agencies_count):
    #     winners = {}
    #     for i in range(agencies_count):
    #         winners[i+1] = []
    #         logging.info(f"action: prepare_winners_list | result: success | agency_id: {i+1}")
    #     for bet in utils.load_bets():
    #         if utils.has_won(bet):
    #             winners[bet.agency].append(bet.document)
    #     for client_id in self.agencies_waiting:
    #         agency_id = self.clients_agency_id[client_id]
        #     try:
        #         client_connection = self.clients_dictionary[client_id]
        #         client_connection.send_winners(winners[agency_id])
        #     except (socket.error, KeyError) as e:
        #         logging.error(f"action: send_winners | result: fail | error: {e}")
        #     logging.info(f"action: send_winners | result: success | agency_id: {agency_id}")
        #     client_connection.close()
        #     del self.clients_dictionary[client_id]
        # self.agencies_waiting = []



    def __handle_client_connection(self, client_id, client_connection, monitor: UtilsMonitor):

        # client_connection = self.clients_dictionary[client_id]
        agency = 0

        while True:  
            agency_id = client_connection.recv_agency_id()
            if agency_id is None:
                logging.error("action: receive_agency_id | result: fail | error: agency_id_not_received")
                client_connection.close()
                del self.clients_dictionary[client_id]
                return
            
            if agency_id == 0:
                logging.info("action: agency_waiting__for_winners | result: success")
                # self.agencies_waiting.append(client_id) # esto no se si hace falta
                
                #aca pongo la barrier
                self.barrier.wait()
                # si ya estan todas las agencias esperando, sorteo
                winners = monitor.load_winners(agency)
                client_connection.send_winners(winners)
                break
            
            # self.clients_agency_id[client_id] = agency_id
            agency = agency_id
            
            number_of_bets = client_connection.recv_number_of_bets()
            if number_of_bets is None:
                logging.error("action: receive_number_of_bets | result: fail | error: number_of_bets_not_received")
                client_connection.close()
                del self.clients_dictionary[client_id]
                return
                  
            bets_received = 0
            try:
                for i in range(number_of_bets):
                    name, surname, DNI, date_of_birth, num = client_connection.recv_bet_info()
                    
                    bet = utils.Bet(str(agency_id), name, surname, str(DNI), date_of_birth, str(num))
                    monitor.store_bet([bet])
                    bets_received += 1
            except OSError as e:
                logging.info(f'action: apuesta_recibida | result: fail | cantidad: {number_of_bets}')
            finally:
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
