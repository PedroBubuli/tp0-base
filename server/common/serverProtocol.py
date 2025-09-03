import socket

class ServerProtocol:

    def __init__(self, socket: socket.socket):
        self.socket = socket
    
    def recv_all(self, length):
        data = b''
        while len(data) < length:
            more = self.socket.recv(length - len(data))
            if not more:
                return None
            data += more
        return data

    def recv_bytes(self, bytes_to_recv):
        buffer = self.recv_all(bytes_to_recv)
        if buffer is None:
            return None
        return int.from_bytes(buffer, byteorder='big')
    
    def recv_string(self):
        string_size = self.recv_bytes(1)
        if string_size is None:
            return None

        string = self.recv_all(string_size)
        if string is None:
            return None
        return string.decode('utf-8')

    def recv_agency_id(self):
        return self.recv_bytes(1)
    
    def recv_number_of_bets(self):
        return self.recv_bytes(1)

    def send_success_message(self):
        self.socket.sendall(b'\x01')

    def recv_bet_info(self):

        name = self.recv_string()
        if name is None:
            raise OSError("Error receiving name")
        
        surname = self.recv_string()
        if surname is None:
            raise OSError("Error receiving surname")
        
        DNI = self.recv_bytes(4)
        if DNI is None:
            raise OSError("Error receiving DNI")
        
        date_of_birth = self.recv_string()
        if date_of_birth is None:
            raise OSError("Error receiving date_of_birth")
        
        num = self.recv_bytes(4)
        if num is None:
            raise OSError("Error receiving num")
        
        return name, surname, DNI, date_of_birth, num

    def send_winners(self, winners):
        self.send_number(len(winners))
        for document in winners:
            self.send_number(int(document))
        return

    def send_number(self, number):
        number_bytes = number.to_bytes(4, byteorder='big')
        self.socket.sendall(number_bytes)
        return

    def close (self):
        if self.socket is not None:
            self.socket.close()
