import socket
import signal
import sys
import logging
import common.utils as utils
from common.serverProtocol import ServerProtocol

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self.client_id = 0
        self.clients_dictionary = {}

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")

        self._running = False
        for client_id in list(self.clients_dictionary.keys()):
            self.clients_dictionary[client_id].close()
            del self.clients_dictionary[client_id]
            
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            try:
                client_connection = self.__accept_new_connection()
                if client_connection:
                    self.clients_dictionary[self.client_id] = client_connection
                    self.__handle_client_connection(self.client_id)
                    self.client_id += 1
            except OSError as e:
                pass


    def __handle_client_connection(self, client_id):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        client_connection = self.clients_dictionary[client_id]
        try:

            name, surname, DNI, date_of_birth, num = client_connection.recv_bet_info()
            
            bet = utils.Bet("1", name, surname, str(DNI), date_of_birth, str(num))
            utils.store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {DNI} | numero:{num}')
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_connection.close()
            del self.clients_dictionary[client_id]

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
