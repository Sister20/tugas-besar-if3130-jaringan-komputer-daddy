'''
This module contains the Segment class which is used to represent a segment of
a data sent from the server to the client using the UDP protocol.
'''

import struct
from constants import SYN_FLAG, ACK_FLAG, FIN_FLAG
from CRC import CRC

class SegmentFlag:
    '''
    This class is used to represent the flags of a segment.

    Attributes:
        syn: A boolean representing the SYN flag.
        ack: A boolean representing the ACK flag.
        fin: A boolean representing the FIN flag.

    Methods:
        get_flag_bytes: Returns the flags as bytes.
        get_flag: Returns the flags as an integer.
    '''
    
    def __init__(self, flag):
        self.syn = bool(flag & SYN_FLAG)
        self.ack = bool(flag & ACK_FLAG)
        self.fin = bool(flag & FIN_FLAG)

    def get_flag_bytes(self):
        return struct.pack('B', int(self.syn) | (int(self.ack) << 1) | (int(self.fin) << 2))

    def get_flag(self):
        return int(self.syn) | (int(self.ack) << 1) | (int(self.fin) << 2)

class Segment:
    '''
    This class is used to represent a segment of a data sent from the server to
    the client using the UDP protocol.

    Attributes:
        flag: A SegmentFlag object representing the flags of the segment.
        seq_num: An integer representing the sequence number of the segment.
        ack_num: An integer representing the acknowledgement number of the segment.
        checksum: An integer representing the checksum of the segment.
        payload: A bytes object representing the payload of the segment.

    Methods:
        set_header: Sets the header information of the segment.
        set_payload: Sets the payload of the segment.
        set_flags: Sets the flags of the segment.
        set_checksum: Sets the checksum of the segment.
        get_flags: Returns the flags of the segment.
        get_header: Returns the header information of the segment.
        get_payload: Returns the payload of the segment.
        _calc_checksum: Calculates the checksum of the segment.
        _verify_checksum: Verifies the checksum of the segment.
        get_bytes: Returns the byte representation of the segment.
    '''

    def __init__(self):
        self.flag = SegmentFlag(0)
        self.seq_num = 0
        self.ack_num = 0
        self.checksum = 0
        self.payload = b""

    def set_header(self, seq_num, ack_num):
        self.seq_num = seq_num
        self.ack_num = ack_num

    def set_payload(self, payload):
        self.payload = payload

    def set_flags(self, flags):
        flag_mapping = {"SYN": SYN_FLAG, "ACK": ACK_FLAG, "FIN": FIN_FLAG}
        self.flag = SegmentFlag(sum(flag_mapping[flag] for flag in flags))

    def set_checksum(self):
        self.checksum = self._calc_checksum()

    def get_flags(self):
        return self.flag.get_flag()

    def get_header(self):
        return {"seq": self.seq_num, "ack": self.ack_num}

    def get_payload(self):
        return self.payload

    def _calc_checksum(self):
        crc = CRC()
        crc.update_checksum(self.payload)
        return crc.get_checksum()

    def _verify_checksum(self):
        return self._calc_checksum() == self.checksum

    def get_bytes(self):
        self.checksum = self._calc_checksum()
        header = struct.pack("II", self.seq_num, self.ack_num)
        flag_bytes = self.flag.get_flag_bytes()
        checksum_bytes = struct.pack("H", self.checksum)
        return header + flag_bytes + b"\x00" + checksum_bytes + self.payload

    def __str__(self):
        return f"seq: {self.seq_num}, ack: {self.ack_num}, flag: {self.get_flags()}, checksum: {self.checksum}, payload: {self.payload}"
 
def main():
    # Create a Segment instance
    segment = Segment()

    # Set header information
    segment.set_header(seq_num=123, ack_num=456)

    # Set payload
    payload_data = b"Hello, UDP!"
    segment.set_payload(payload_data)

    # Set flags
    flag_list = ["SYN", "ACK"]
    segment.set_flags(flag_list)

    # Set checksum
    segment.set_checksum()

    # Display the segment details
    print("Segment Details:")
    print(segment)

    # Get the byte representation of the segment
    segment_bytes = segment.get_bytes()

    # Print the byte representation
    print("\nSegment Bytes:")
    print(segment_bytes)

    # Verify the checksum
    checksum_verification = segment._verify_checksum()
    print("\nChecksum Verification:", checksum_verification)

if __name__ == "__main__":
    main()
