"""
CPSC 5510, Seattle University, Project #2
This is free and unencumbered software released into the public domain.
:Author: Vaishnavi Punati
:Version: s23
"""

from socket import *

RECEIVER_PORT = 10111
TIMEOUT = 0.3  # 300 ms


def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet_wo_checksum: the packet byte data (including headers except for
      checksum field)

    Returns:
      the checksum in bytes

    >>> a = b'\\x08\\x00\\x00\\x00\\x24\\xd3\\x01\\x00'
    >>> b = b'\\x1a\\x15\\x7d\\xd9\\xb5\\x16\\xd9\\x41'
    >>> create_checksum(a + b)
    b'\\xab\\xe5'
    >>> create_checksum(a + b + b'\\x01') # check odd number of bytes
    b'\\xab\\xe4'
    >>> create_checksum(b'COMPNETW\\x00@msg1')
    b'\\xf7\\xde'
    """
    csum = 0
    count_to = (len(packet_wo_checksum) // 2) * 2
    count = 0
    while count < count_to:
        this_val = int.from_bytes(packet_wo_checksum[count:count + 2], 'big')
        csum = csum + this_val
        count = count + 2
    if count_to < len(packet_wo_checksum):
        csum = csum + packet_wo_checksum[count]
    csum = (csum >> 16) + (csum & 0xffff)
    answer = ~csum & 0xffff
    return answer.to_bytes(2, 'big')


def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet: the whole (including original checksum) packet byte data

    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise

    >>> verify_checksum(b'COMPNETW\\xf7\\xde\\x00@msg1')
    True
    >>> verify_checksum(b'COMPNETW\\xf8\\xde\\x00@msg1')
    False
    """
    if len(packet) < 12:
        print('packet truncated!')
        return False
    len_field = int.from_bytes(packet[10:12], 'big')
    length = len_field >> 2
    if len(packet) != length:
        print('packet too short!')
        return False
    checksum = packet[8:10]
    return checksum == create_checksum(packet[:8] + packet[10:])


def make_packet(data_str, ack, seq_num):
    """Make a packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      data_str: the string of the data (to be put in the Data area)
      ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
      seq_num: an int tells the sequence number, i.e., 0 or 1

    Returns:
      a created packet in bytes

    >>> make_packet('msg1', False, 0)
    b'COMPNETW\\xf7\\xde\\x00@msg1'
    >>> make_packet('', True, 1)
    b'COMPNETW\\xcc\\x90\\x003'
    >>> make_packet('', False, 1)
    b'COMPNETW\\xcc\\x92\\x001'
    """
    data = bytes(data_str, 'UTF-8')
    preamble = b'COMPNETW'
    length = 12 + len(data)
    ack_num = 1 if ack else 0
    len_field = (length << 2 | ack_num << 1 | seq_num).to_bytes(2, 'big')
    checksum = create_checksum(preamble + len_field + data)
    return preamble + checksum + len_field + data


def get_bits(packet):
    """returns pair (is_ack, seq_num)
    >>> get_bits(make_packet('msg1', False, 0))
    (False, 0)
    >>> get_bits(make_packet('', True, 1))
    (True, 1)
    >>> get_bits(make_packet('', False, 1))
    (False, 1)
    """
    seq_num = packet[11] & 1
    is_ack = (packet[11] & 2) == 2
    return is_ack, seq_num


def extract(packet):
    """Extract the data string from the packet
    >>> extract(make_packet('msg1', False, 0))
    'msg1'
    """
    return str(packet[12:], 'UTF-8')


def other(current_seq_num):
    """Toggler for sequence number to/from 0/1
    >>> other(0)
    1
    >>> other(1)
    0
    """
    return (current_seq_num + 1) % 2
