# Flags for header
SYN_FLAG = 0b000000010 # (1st bit)
ACK_FLAG = 0b000010000 # (4th bit)
FIN_FLAG = 0b000000001 # (0th bit)

# CRC constants
CRC_INIT = 0xffff
CRC_XOROUT = 0x0000
CRC_POLY = 0x1021

# Connection constants
SEGMENT_SIZE = 32768