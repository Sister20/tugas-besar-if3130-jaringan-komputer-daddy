from lib.Connection import Connection
from lib.Segment import Segment

class Client():
  def __init__(self):
    self.ip = 'localhost'
    self.server_port = 12345
    self.client_port = 54321
    self.connection = Connection('localhost', self.client_port, False)
  
  def three_way_handshake(self):
    # Client initialize handshake, sending SYN to server
    syn_req = Segment()
    syn_req.set_flags(["SYN"])
    print(syn_req)
    self.connection.send(syn_req, (self.ip, self.server_port))
    try:
      while True:
        received_segment, client_address, verif = self.connection.listen()
        print(f"Received segment from {client_address}")

        if not verif:
          print("Checksum Failed. Abort Handshake")
          exit(1)
        
        # Client received SYN & ACK from server
        if(received_segment.get_flags() == 5): #TODO: set the correct flag validation
          ack_req = Segment()
          ack_req.set_flags(["ACK"])
          print(ack_req)
          self.connection.send(ack_req, (self.ip, self.server_port))
          print("Handshake with successfull")
          break
        else:
          print("Handshake with failed")
          break

    except KeyboardInterrupt:
      print("Client is closing")

    finally:
      self.connection.close_socket()

if __name__ == "__main__":
  main = Client()
  main.three_way_handshake()