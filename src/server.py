from lib.Connection import Connection
from lib.Segment import Segment
from lib.Constants import SYN_FLAG, ACK_FLAG

class Server():
  def __init__(self):
    self.ip = 'localhost'
    self.port = 12345
    self.clients = []
    self.connection = Connection(self.ip, self.port, True)
    self.segment = Segment()

  def listen_clients(self):
    try:
        while True:
            # Listen for incoming segments
            received_segment, client_address, verif = self.connection.listen()
            if verif and received_segment.get_flags() == SYN_FLAG:
              print(f"Received SYN from {client_address} : ")
              print(received_segment)
              print()

              if client_address not in self.clients:
                  # Add listened client address to a list
                  self.clients.append((client_address, received_segment))
                  print(f"Received request from {client_address[0]}:{client_address[1]}")

                  more_input = input("Listen more clients? (y/n) : ").lower()
                  print()

                  if(more_input == "n"):
                    break
              else:
                 print(f"Already received client request from {client_address[0]}:{client_address[1]}")
            else:
              print("Invalid flag")

    except KeyboardInterrupt:
        print("Server is shutting down.")

  def three_way_handshake(self, received_segment: Segment, client_address): 
    # Server handshake, sending SYN-ACK to client
    syk_ack_req = Segment()
    syk_ack_req.set_flags(["SYN", "ACK"])

    # Setting SYN-ACK header
    header = received_segment.get_header()
    temp_header_seq = 0
    temp_header_ack = header["seq"] + 1

    syk_ack_req.set_header(temp_header_seq, temp_header_ack)

    self.connection.send(syk_ack_req, client_address)

    # Server handshake, receiving ACK from client
    received_segment, client_address, verif = self.connection.listen()
    print(f"Received ACK from {client_address} : ")
    print(received_segment)
    print()
    if not verif:
      print("Checksum Failed. Abort Handshake")
      exit(1)
    
    if(received_segment.get_flags() == ACK_FLAG):
      print("Handshake successfull")

  def start(self):
    for i in self.clients:
      self.three_way_handshake(i[1], i[0])

  def shutdown(self):
    self.connection.close_socket()

if __name__ == "__main__":
   main = Server()
   main.listen_clients()
   main.start()
   main.shutdown()