from lib.Connection import Connection
from lib.Segment import Segment

class Server():
  def __init__(self):
    self.ip = 'localhost'
    self.port = 12345
    self.clients_addresses = []
    self.connection = Connection(self.ip, self.port, True)

  def listen_clients(self):
    try:
        while True:
            # Listen for incoming segments
            received_segment, client_address, verif = self.connection.listen()
            print(f"Received segment from {client_address}")
            print(received_segment)
            if verif and received_segment.get_flags() == 4: #TODO: set the correct flag validation
              if client_address not in self.clients_addresses:
                  # Add listened client address to a list
                  self.clients_addresses.append(client_address)
                  print(f"Received request from {client_address[0]}:{client_address[1]}")

                  more_input = input("Listen more input? (y/n)").lower()
                  if(more_input == "n"):
                    break
              else:
                 print(f"Already received client request from {client_address[0]}:{client_address[1]}")

    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        # Close the socket when done
        self.connection.close_socket()

  def three_way_handshake(self):
     
    # Server handshake, sending SYN-ACK to client
    syk_ack_req = Segment()
    syk_ack_req.set_flags(["SYK", "ACK"])
    #TODO: get client address
    # self.connection.send(syk_ack_req, client_address)

    # Server handshake, receiving ACK from client
    received_segment, client_address, verif = self.connection.listen()
    if not verif:
      print("Checksum Failed. Abort Handshake")
      exit(1)
    
    if(received_segment.get_flags() == 2): #TODO: set the correct flag validation
       print("Handshake successfull")

if __name__ == "__main__":
   main = Server()
   main.listen_clients()