from math import ceil
from lib.Connection import Connection
from lib.Segment import Segment
from lib.constants import SYN_FLAG, ACK_FLAG, FIN_FLAG, PAYLOAD_SIZE, WINDOW_SIZE
import os
from lib.Parser import Parser
from concurrent.futures import ThreadPoolExecutor

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
      return os.path.basename(self.filepath)
  
  def split_file_to_segment(self):
    # Create metadata segment
    metadata_segment = Segment()
    filename, extension = os.path.splitext(self.filename)
    filesize = self.filesize
    filepath = self.filepath
    segment_length = ceil(filesize / PAYLOAD_SIZE)

    # Set metadata payload
    payload = f"{filename},{extension},{filesize},{filepath},{segment_length}".encode()
    metadata_segment.set_payload(payload)

    # Set metadata header
    metadata_segment.set_header(seq_num=2, ack_num=2)

    self.segment_list = [metadata_segment]

    # Create segments for file partitions
    for i in range(segment_length):
        # Create a new segment for each partition
        segment_temp = Segment()

        # Set payload from file partition
        byte_offset = i * PAYLOAD_SIZE
        self.file.seek(byte_offset)
        payload_segment_temp = self.file.read(PAYLOAD_SIZE)
        segment_temp.set_payload(payload_segment_temp)

        # Set header for each segment (file partition)
        header_seq_num = i + 3
        header_ack_num = 3
        segment_temp.set_header(seq_num=header_seq_num, ack_num=header_ack_num)

        # Append partition to the list
        self.segment_list.append(segment_temp)
      
  def file_transfer(self, client_address):
    segment_length = len(self.segment_list) + 2  # +2 for handshake
    window_size = min(segment_length - 2, WINDOW_SIZE)
    sequence_base = 2

    while sequence_base < segment_length:
        sequence_max = window_size

        # Send segments
        for i in range(sequence_max):
            current_sequence = i + sequence_base
            if current_sequence < segment_length:
                segment_to_send = self.segment_list[current_sequence - 2]
                print(f"[!] Sending segment {current_sequence} to [Client {client_address[0]}:{client_address[1]}]")
                self.connection.send(segment_to_send, client_address)

        # Receive acknowledgments
        for i in range(sequence_max):
            try:
                received_segment, response_address, verif = self.connection.listen(2)

                if not verif:
                    raise Exception("Checksum failed")

                if (
                    client_address[1] == response_address[1]
                    and received_segment.get_flags() == ACK_FLAG
                    and received_segment.get_header()["ack"] == sequence_base + 1
                ):
                    print(f"[!] Received ACK {sequence_base + 1} from [Client {client_address[0]}:{client_address[1]}]")
                    sequence_base += 1
                    window_size = min(segment_length - sequence_base, WINDOW_SIZE)
                elif client_address[1] != response_address[1]:
                    print(f"[!] Received ACK from wrong client [Client {client_address[0]}:{client_address[1]}]")
                elif received_segment.get_flags() != ACK_FLAG:
                    print(f"[!] Received Wrong Flag from [Client {client_address[0]}:{client_address[1]}]")
                else:
                    print(f"[!] Received Wrong ACK from [Client {client_address[0]}:{client_address[1]}]")
                    Rn = received_segment.get_header()["ack"]
                    if Rn > sequence_base:
                        sequence_max = sequence_max - sequence_base + Rn
                        sequence_base = Rn
            except Exception as e:
                print(f"[!] [Error] {str(e)} while handling ACK response, resending segment to [Client {client_address[0]}:{client_address[1]}]")

    # Transfer complete, send FIN
    print(f"[!] File transfer complete, sending FIN to [Client {client_address[0]}:{client_address[1]}]")
    segmentFIN = Segment()
    segmentFIN.set_flags(["FIN"])
    self.connection.send(segmentFIN, client_address)

    # Wait for FIN-ACK
    while True:
        try:
            received_segment, response_address, valid = self.connection.listen()

            if not valid:
                raise Exception("Checksum failed")

            if (
                client_address[1] == response_address[1]
                and received_segment.get_flags() == (FIN_FLAG + ACK_FLAG)
            ):
                print(f"[!] Received FIN-ACK [Client {client_address[0]}:{client_address[1]}]")
                sequence_base += 1
                break
        except Exception as e:
            print(f"[!] [Error] {str(e)} while handling ACK response, resending FIN to [Client {client_address[0]}:{client_address[1]}]")
            self.connection.send(segmentFIN, client_address)

    # Send ACK to complete the transfer
    print(f"[!] Sending ACK Flag to [Client {client_address[0]}:{client_address[1]}]")
    segmentACK = Segment()
    segmentACK.set_flags(["ACK"])
    self.connection.send(segmentACK, client_address)

  def listen_clients(self):
    try:
        while True:
            print("Waiting for client...")
            received_segment, client_address, verif = self.connection.listen()

            if verif and received_segment.get_flags() == SYN_FLAG:
                try:
                  self.handle_client_request(received_segment, client_address)
                except StopIteration:
                  break
            else:
                print("Invalid flag or checksum failed.")

    except KeyboardInterrupt:
        print("Server is shutting down.")

  def handle_client_request(self, received_segment, client_address):
    print(f"Received SYN from {client_address} : ")
    print(received_segment)
    print()

    if client_address not in self.clients:
        self.clients.append((client_address, received_segment))
        print(f"Received request from {client_address[0]}:{client_address[1]}")

        while True:
            more_input = input("Listen more clients? (y/n) : ").lower()
            print()

            if more_input in {"n", "y"}:
                break
            else:
                print("Input Not Valid! \n")

        if more_input == "n":
            raise StopIteration  # Terminate the loop
    else:
        print(f"Already received client request from {client_address[0]}:{client_address[1]}")

  def three_way_handshake(self, received_segment: Segment, client_address):
    syn_ack_req = Segment()
    syn_ack_req.set_flags(["SYN", "ACK"])

    header = received_segment.get_header()
    temp_header_seq = 0
    temp_header_ack = header["seq"] + 1

    syn_ack_req.set_header(temp_header_seq, temp_header_ack)

    self.connection.send(syn_ack_req, client_address)

    received_segment, client_address, verif = self.connection.listen()
    print(f"Received ACK from {client_address} : ")
    print(received_segment)
    print()

    if not verif:
        print("Checksum Failed. Abort Handshake.")
        exit(1)

    if received_segment.get_flags() == ACK_FLAG:
        print("Handshake successful")

  def start(self):
    # Run in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        handshake_futures = [executor.submit(self.three_way_handshake, client[1], client[0]) for client in self.clients]
        transfer_futures = [executor.submit(self.file_transfer, client[0]) for client in self.clients]

        # Wait for all handshake tasks to complete
        for future in handshake_futures:
            future.result()

        # Wait for all file transfer tasks to complete
        for future in transfer_futures:
            future.result()
      
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