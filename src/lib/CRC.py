'''
This module contains the CRC class which is used to calculate the checksum of a
segment using 16-bit CRC.
'''

from .constants import CRC_INIT, CRC_XOROUT, CRC_POLY

class CRC:
    '''
    This class is used to calculate the checksum of a segment using 16-bit CRC.

    Attributes:
        _table: A list of 256 16-bit integers used to calculate the checksum.
        _checksum: A 16-bit integer representing the checksum of the segment.

    Methods:
        _calc_table: Calculates the table used to calculate the checksum.
        update_checksum: Updates the checksum of the segment.
        get_checksum: Returns the checksum of the segment as bytes.
    '''

    def __init__(self):
        self._table = self._calc_table()
        self._checksum = CRC_INIT

    def _calc_table(self):
        '''
        Calculates the table used to calculate the checksum.

        Returns:
            A list of 256 16-bit integers used to calculate the checksum.
        '''
        table = []
        for i in range(256):
            crc = 0
            c = i << 8
            for j in range(8):

                # If the MSB is 1
                if (crc ^ c) & 0x8000:
                    crc = (crc << 1) ^ CRC_POLY
                else:
                    crc <<= 1
                c <<= 1

                # Mask the CRC to 16 bits
                crc &= 0xffff
            table.append(crc)
        return table

    def update_checksum(self, data):
        '''
        Updates the checksum of the segment.

        Args:
            data: A bytes object representing the data of the segment.
        '''
        for byte in data:
            self._checksum = (self._checksum << 8) ^ self._table[(self._checksum >> 8) ^ byte]
            self._checksum &= 0xffff

    def get_checksum(self):
        '''
        Returns the checksum of the segment as bytes.

        Returns:
            A bytes object representing the checksum of the segment.
        '''
        return self._checksum ^ CRC_XOROUT
    