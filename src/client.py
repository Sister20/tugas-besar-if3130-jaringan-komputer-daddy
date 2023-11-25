from lib.Connection import Connection
from lib.Segment import Segment
from lib.Constants import SYN_FLAG, ACK_FLAG

class Client():
  def __init__(self):
    self.ip = 'localhost'
    self.server_port = 12345
    self.client_port = 54321
    self.connection = Connection('localhost', self.client_port, False)
    self.segment = Segment()
  
  def three_way_handshake(self):
    # Client initialize handshake, sending SYN to server
    # syn_req = Segment()
    self.segment.set_flags(["SYN"])
    self.segment.set_header(0, 0)
    print("Sending SYN from client\n")
    self.connection.send(self.segment, (self.ip, self.server_port))
    try:
      while True:
        received_segment, client_address, verif = self.connection.listen()

        if not verif:
          print("Checksum Failed. Abort Handshake")
          exit(1)
        
        # Client received SYN & ACK from server
        if(received_segment.get_flags() == (SYN_FLAG + ACK_FLAG)):
          print(f"Received SYN-ACK from {client_address} : ")
          print(received_segment)
          print()

          # ack_req = Segment()
          self.segment.set_flags(["ACK"])

          # Setting ACK header
          header = received_segment.get_header()
          temp_header_seq = 1
          temp_header_ack = header["seq"] + 1
          self.segment.set_header(temp_header_seq, temp_header_ack)

          # Send SYN-ACK to server
          self.connection.send(self.segment, (self.ip, self.server_port))
          print("Sending ACK from client")
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