import socket
from .Segment import Segment
from .constants import (
  SEGMENT_SIZE,
)

class Connection:
  '''
  This class is used to represent a UDP connection for both server-side and client-side communication.

    Args:
        ip (str): The IP address to bind or connect to.
        port (int): The port number to bind or connect to.
        server (bool): True if the instance is for a server, False for a client.

    Attributes:
        ip (str): The IP address used for binding or connecting.
        port (int): The port number used for binding or connecting.
        socket (socket.socket): The underlying UDP socket.

    Methods:
        send(data: Segment, dest: (str, int)) -> None:
            Send a UDP segment to the specified destination.

        listen() -> Segment:
            Listen for incoming UDP segments.

        close_socket() -> None:
            Close the UDP socket.
  '''
  def __init__(self, ip: str, port: int, server: bool):
    '''
    INITIALIZE UDP SOCKET
    '''
    # AF_INET : Using IPv4 address
    # SOCK_DGRAM (Datagram) : Connectionless protocol, for UDP
    # SO_REUSEADDR : Quickly reuse a recent closed socket address
    # SO_REUSEPORT : Allow multiple sockets want to bind to the same address and port
    # SO_BROADCAST : Enabling sending broadast message
    
    self.ip = ip
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if(server):
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    else:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    self.socket.bind((self.ip, self.port))

    if(server):
      print(f"[\] Server started on {self.ip}:{self.port}")
    else:
      print(f"[\] Client started on {self.ip}:{self.port}")
  
  def send(self, data: Segment, dest: (str, int)):
    self.socket.sendto(data.get_bytes(), dest)

  def listen(self, timeout=10, bool=False):
    try:
      if(not bool):
        self.set_timeout(timeout)
      byte, address = self.socket.recvfrom(SEGMENT_SIZE)
      incoming_segment = Segment()
      incoming_segment.set_from_bytes(byte)
      incoming_segment.set_checksum()
      verif = incoming_segment._verify_checksum()
      return incoming_segment, address, verif
    except TimeoutError as e:
      raise e

  def set_timeout(self, time):
    self.socket.settimeout(time)
  
  def close_socket(self):
    self.socket.close()