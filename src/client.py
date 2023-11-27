from lib.Connection import Connection
from lib.Segment import Segment
from lib.Constants import SYN_FLAG, ACK_FLAG, FIN_FLAG
from socket import timeout as socket_timeout
from lib.Parser import Parser

class Client():
  def __init__(self):
    self.parser = Parser(server=False)
    self.ip = 'localhost'
    self.server_port = self.parser.get_args()["broadcast_port"]
    self.client_port = self.parser.get_args()["client_port"]
    self.connection = Connection('localhost', self.client_port, False)
    self.filepath = self.parser.get_args()["output_file"]
    self.file = self.create_file()
    
  def create_file(self):
    try:
        file = open(f"{self.filepath}", "wb")
        return file
    except FileNotFoundError:
        print(f"[!] {self.pathfile_output} doesn't exists. Exiting...")
        exit(1)
  
  def three_way_handshake(self):
    # Client initialize handshake, sending SYN to server
    segment = Segment()
    segment.set_flags(["SYN"])
    segment.set_header(0, 0)
    print("Sending SYN from client\n")
    self.connection.send(segment, (self.ip, self.server_port))
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
          segment.set_flags(["ACK"])

          # Setting ACK header
          header = received_segment.get_header()
          temp_header_seq = 1
          temp_header_ack = header["seq"] + 1
          segment.set_header(temp_header_seq, temp_header_ack)

          # Send SYN-ACK to server
          self.connection.send(segment, (self.ip, self.server_port))
          print("Sending ACK from client")
          break
        else:
          print("Handshake with failed")
          break
    except KeyboardInterrupt:
      print("Client is closing")
      
  def sendACK(self, server_addr, ackNumber):
      response = Segment()
      response.set_flags(["ACK"])
      header_sequence = ackNumber - 1
      header_ack = ackNumber
      response.set_header(header_sequence,header_ack)
      self.connection.send(response, server_addr)
      
  def listen_file(self):
    metadata_segment_number = 2
    metadata_segment_received = False
    Rn = 3
    received_segment, server_address = None, None
    while True:
      try:
        received_segment, server_address, verif = self.connection.listen()
        
        if server_address[1] == self.server_port:
          
          if(verif and received_segment.get_header()["seq"] == metadata_segment_number and metadata_segment_received == False):
            payload = received_segment.get_payload()
            metadata_segment = payload.decode().split(",")
            print(f"[!] Received Filename: {metadata_segment[0]}, File Extension: {metadata_segment[1]}, File Size: {metadata_segment[2]}, Filepath: {metadata_segment[3]} from [Server {server_address[0]}:{server_address[1]}]")
            metadata_segment_received = True
            self.sendACK(server_address, metadata_segment_number)
            continue
          
          elif (verif and received_segment.get_header()["seq"] == Rn):
            payload = received_segment.get_payload()
            self.file.write(payload)
            print(
                f"[!] Received Segment {Rn} from [Server {server_address[0]}:{server_address[1]}]"
            )
            print(
                f"[!] Sending ACK {Rn + 1} to [Server {server_address[0]}:{server_address[1]}] "
            )
            Rn += 1
            self.sendACK(server_address, Rn)
            continue
          elif (received_segment.get_flags() == FIN_FLAG):
            print(f"[!] Received FIN from [Server {server_address[0]}:{server_address[1]}]")
            break
          elif received_segment.get_header()["seq"] < Rn:
            print(f"[!] Received Segment {received_segment.get_header()['seq']} from [Server {server_address[0]}:{server_address[1]}] [Duplicate Segment]")
          elif received_segment.get_header()["seq"] > Rn:
            print(f"[!] Received Segment {received_segment.get_header()['seq']} from [Server {server_address[0]}:{server_address[1]}] [Segment Out-Of-Order]")
          else:
            print(f"[!] Received Segment {received_segment.get_header()['seq']} from [Server {server_address[0]}:{server_address[1]}]  [File Error]")
        else:
          print(f"[!] Received Segment {received_segment.get_header()['seq']} from [Server {server_address[0]}:{server_address[1]}] [Wrong server]")
        self.sendACK(server_address, Rn) #request to resending prev segment to server
      except socket_timeout:
        print(
            f"[!] [Timeout] timeout error, request resending segment to  [Server {server_address[0]}:{server_address[1]}]"
        )
        self.sendACK(server_address, Rn) #request to resending prev segment to server
    
    # sent FIN-ACK and wait for ACK Flag then close connection
    print(f"[!] [Server {server_address[0]}:{server_address[1]}] Sending FIN-ACK")
    #Send FIN ACK Flag
    FinAckSegment = Segment()
    FinAckSegment.set_header(Rn,Rn)
    FinAckSegment.set_flags(["FIN","ACK"])
    self.connection.send(FinAckSegment, server_address)
    ack_flag = False
    while not ack_flag:
      try:
        received_segment,server_address,verif = self.connection.listen()
        
        if received_segment.get_flags() == ACK_FLAG:
          print(f"[!] Received ACK. Closing connection from [Server {server_address[0]}:{server_address[1]}]")
          ack_flag = True
      except socket_timeout:
        print(
            f"[!] [Timeout] timeout error, resending FIN ACK to [Server {server_address[0]}:{server_address[1]}] "
        )
        self.connection.send(FinAckSegment, server_address)
    # Finish
    print(f"[!] Data received successfuly from [Server {server_address[0]}:{server_address[1]}]")
    print(f"[!] Writing file to {self.filepath}") #path bisa diganti
    
  def shutdown(self):
    self.file.close()
    self.connection.close_socket()

    
if __name__ == "__main__":
  main = Client()
  main.three_way_handshake()
  main.listen_file()
  main.shutdown()