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
    
    def recv_size_of_bets_batch(self):
        return self.recv_bytes(4)

    def send_success_message(self):
        self.socket.sendall(b'\x01')

    def parse_bet_info(self, buffer, offset):
        
        name_size = buffer[offset]
        offset += 1
        name = buffer[offset:offset+name_size].decode('utf-8')
        offset += name_size

        surname_size = buffer[offset]
        offset += 1
        surname = buffer[offset:offset+surname_size].decode('utf-8')
        offset += surname_size

        DNI = int.from_bytes(buffer[offset:offset+4], byteorder='big')
        offset += 4

        dob_size = buffer[offset]
        offset += 1
        date_of_birth = buffer[offset:offset+dob_size].decode('utf-8')
        offset += dob_size

        num = int.from_bytes(buffer[offset:offset+4], byteorder='big')
        offset += 4

        return (name, surname, DNI, date_of_birth, num), offset


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
