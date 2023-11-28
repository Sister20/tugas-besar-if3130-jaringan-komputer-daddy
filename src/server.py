from math import ceil
from lib.Connection import Connection
from lib.Segment import Segment
from lib.constants import SYN_FLAG, ACK_FLAG, FIN_FLAG, SEGMENT_SIZE, PAYLOAD_SIZE, WINDOW_SIZE
import os
from lib.Parser import Parser

class Server():
  def __init__(self):
    self.parser = Parser(server=True)
    self.ip = 'localhost'
    self.port = self.parser.get_args()["broadcast_port"]
    self.clients = []
    self.connection = Connection(self.ip, self.port, True)

    self.filepath = self.parser.get_args()["input_file"]
    self.file = self.get_file()
    print(self.file)
    self.filesize = os.path.getsize(self.filepath) if self.filepath else None
    self.filename = self.get_filename()
    self.split_file_to_segment()
    
  def get_filename(self):
      if "/" in self.filepath:
          return self.filepath.split("/")[-1]

      elif "\\" in self.filepath:
          return self.filepath.split("\\")[-1]

      return self.filepath
  
  def split_file_to_segment(self):
    self.segment_list = []
    segment_length = ceil(self.filesize / PAYLOAD_SIZE)
    
    metadata_segment = Segment()
    filename = self.filename.split(".")[0]
    extension = self.filename.split(".")[-1]
    filesize = self.filesize
    filepath = self.filepath
    
    payload = filename.encode() + ",".encode() + extension.encode() + ",".encode() + str(filesize).encode() + ",".encode() + str(filepath).encode() + ",".encode() + str(segment_length).encode()
    metadata_segment.set_payload(payload)
    header_seq_num_metadata = 2
    header_ack_num_metadata = 2
    metadata_segment.set_header(header_seq_num_metadata,header_ack_num_metadata)
    self.segment_list.append(metadata_segment)
    
    
    for i in range(segment_length):
      segment_temp = Segment() #New segment for each partition
      byte_offset = i * PAYLOAD_SIZE
      self.file.seek(byte_offset) #Shift to byteoffset
      payload_segment_temp = self.file.read(PAYLOAD_SIZE) #Get PAYLOAD_SIZE byte from file
      segment_temp.set_payload(payload_segment_temp) #Set segment payload from byte partition above
      header_seq_num = i + 3 #sequence number
      header_ack_num = 3 # acknowledge number
      segment_temp.set_header(header_seq_num,header_ack_num) #Set header for each segment (file patition)
      self.segment_list.append(segment_temp) #append partition to list
      
  def file_transfer(self,client_address):
    # Sequence number 2 for Metadata Segment (Metadata)
    segment_length = len(self.segment_list) + 2 #+2 for handshake
    window_size = min(segment_length - 2, WINDOW_SIZE) #Select how many times to send packet before asking ACK Flag from client
    sequence_base = 2 #Sequence Number

    while sequence_base < segment_length:
      sequence_max=window_size #Sn for sending segment before asking ACK
      for i in range(sequence_max):
        print(f"[!] Sending segment {sequence_base + i} to [Client {client_address[0]}:{client_address[1]}]")
        if i + sequence_base < segment_length:
            self.connection.send(self.segment_list[i + sequence_base - 2], client_address)
      
      for i in range(sequence_max):
        try:
          received_segment, response_address, verif = self.connection.listen(2) #Get response (segment) from client
          
          if(not verif): #checksum failed
            exit(1)
          
          # print(response_address[1])
          # print(client_address[1])
          # print(received_segment.get_flags())
          # print(ACK_FLAG)
          # print(sequence_base+1)
          # print(f'Received ACK {received_segment.get_header()["ack"]} from [{client_address[0]} : {client_address[1]}]')
          
          if(client_address[1] == response_address[1]) and (received_segment.get_flags() == ACK_FLAG) and (received_segment.get_header()["ack"] == sequence_base + 1):
            print(f"[!] Received ACK {sequence_base + 1} from [Client {client_address[0]}:{client_address[1]}]")
            sequence_base += 1
            window_size = min(segment_length - sequence_base, WINDOW_SIZE)
          elif client_address[1] != response_address[1]:
            print(f"[!] Received ACK from wrong client [Client {client_address[0]}:{client_address[1]}]")
          elif received_segment.get_flags() != ACK_FLAG:
            print(f"[!] Recieved Wrong Flag from [Client {client_address[0]}:{client_address[1]}]")
          else : 
            print(f"[!] Received Wrong ACK from [Client {client_address[0]}:{client_address[1]}]")
            Rn = received_segment.get_header()["ack"]
            if (Rn > sequence_base):
              sequence_max = sequence_max - sequence_base + Rn
              sequence_base = Rn
        except:
          print(f"[!] [Timeout] Problem ACK response, resending segment to [Client {client_address[0]}:{client_address[1]}]")
    else : 
      print(f"[!] File transfer complete, sending FIN to [Client {client_address[0]}:{client_address[1]}]")
      segmentFIN = Segment()
      segmentFIN.set_flags(["FIN"]) #Request FIN ACK to client
      self.connection.send(segmentFIN,client_address)
      
      while True:
        try:
          received_segment,response_address,valid = self.connection.listen()
          
          if client_address[1] == response_address[1] and received_segment.get_flags() == (FIN_FLAG + ACK_FLAG):
            print(f"[!] Recieved FIN-ACK [Client {client_address[0]}:{client_address[1]}]")
            sequence_base += 1
            break

        except:
          print(f"[!] [Timeout] Problem ACK response, resending FIN to [Client {client_address[0]}:{client_address[1]}]")
          self.connection.send(segmentFIN, client_address)
      
      # Send ACK Flag to Client
      print(f"[!] Sending ACK Flag to [Client {client_address[0]}:{client_address[1]}]")
      segmentACK = Segment()
      segmentACK.set_flags(["ACK"])
      self.connection.send(segmentACK, client_address)
        
  def listen_clients(self):
    try:
        while True:
            print("Waiting for client...")
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

                  while True :
                    more_input = input("Listen more clients? (y/n) : ").lower()
                    print()

                    if(more_input == "n"):
                      break
                    elif(more_input == "y"):
                      break
                    else : 
                      print("Input Not Valid! \n")
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
      self.file_transfer(i[0])
      
  def shutdown(self):
    self.file.close()
    self.connection.close_socket()

  def get_file(self):
    try:
      file = open(f"{self.filepath}","rb")
      return file
    except FileNotFoundError:
      print(f"{self.filepath} doesn't exists. Exiting...")
      exit(1)
if __name__ == "__main__":
   main = Server()
   main.listen_clients()
   main.start()
   main.shutdown()