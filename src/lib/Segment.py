'''
This module contains the Segment class which is used to represent a segment of
a data sent from the server to the client using the UDP protocol.
'''

import struct
from src.lib.constants import SYN_FLAG, ACK_FLAG, FIN_FLAG

class SegmentFlag:
    '''
    This class is used to represent the flag of a segment.
    
    Attributes:
        syn: A boolean representing the SYN flag.
        ack: A boolean representing the ACK flag.
        fin: A boolean representing the FIN flag.

    Methods:
        get_flag_bytes: Returns the flag as a byte.
        get_flag: Returns the flag as an integer.
    '''

    def __init__(self, flag):
        self.syn = flag & SYN_FLAG
        self.ack = flag & ACK_FLAG
        self.fin = flag & FIN_FLAG

    def get_flag_bytes(self):
        return struct.pack('B', self.syn | self.ack | self.fin)
    
    def get_flag(self):
        return self.syn | self.ack | self.fin
    

class Segment:
    '''
    This class is used to represent a segment of a data sent from the server to
    the client using the UDP protocol.

    Attributes:
        flag: An integer representing the flag of the segment.
        seq_num: An integer representing the sequence number of the segment.
        ack_num: An integer representing the acknowledgement number of the segment.
        checksum: A bytes object representing the checksum of the segment.
        payload: A bytes object representing the data of the segment.

    Methods:
        syn: Returns a boolean representing the SYN flag of the segment.
        ack: Returns a boolean representing the ACK flag of the segment.
        fin: Returns a boolean representing the FIN flag of the segment.
        syn_ack: Returns a boolean representing the SYN-ACK flag of the segment.
        fin_ack: Returns a boolean representing the FIN-ACK flag of the segment.
        _calc_checksum: Calculates the checksum of the segment.
        _update_checksum: Updates the checksum of the segment.
        _verify_checksum: Verifies the checksum of the segment.
        get_bytes: Returns the segment as bytes.
    '''
