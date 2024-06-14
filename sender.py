"""
CPSC 5510, Seattle University, Project #2
This is free and unencumbered software released into the public domain.
:Author: Vaishnavi Punati
:Version: s23

NOTE: Run receiver.py file first, before the sender is constructed.
"""
from socket import *
from util import *

RECEIVER = ('localhost', RECEIVER_PORT)


class Sender:
    """The receiver side of RDT 3.0, stop-and-wait."""

    def __init__(self):
        """
        Your constructor should not expect any argument passed in,
        as an object will be initialized as follows:
        sender = Sender()

        Please check the main.py for a reference of how your function will be
        called.
        """
        self.sequence_number = 1
        self.packet_number = 0
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.settimeout(TIMEOUT)
        self.app_msg_str = None
        self.send_pkt = None

    def __del__(self):
        self.udp.close()

    def rdt_send(self, app_msg_str):
        """reliably send a message to the receiver (MUST-HAVE DO-NOT-CHANGE)

        Args:
          app_msg_str: the message string (to be put in the data field of the
          packet)

        """
        self.sequence_number = other(self.sequence_number)

        print('original message string:', app_msg_str)
        self.app_msg_str = app_msg_str

        self.send_pkt = make_packet(app_msg_str, False, self.sequence_number)
        print('packet created:', self.send_pkt)

        self.udt_send()
        self.wait_for_ack()

    def udt_send(self):
        self.packet_number += 1
        self.udp.sendto(self.send_pkt, RECEIVER)
        print('packet num.' + str(self.packet_number)
              + ' is successfully sent to the receiver.')

    def wait_for_ack(self):
        while True:
            try:
                packet, _whom = self.udp.recvfrom(4096)
            except TimeoutError:
                print('socket timeout! Resend!\n\n')
                print('[timeout retransmission]:', self.app_msg_str)
                self.udt_send()
                continue  # stay in wait_for_ack state

            is_ack, ack_num = get_bits(packet)
            if not verify_checksum(packet):
                print('packet corrupt, resend!\n\n')
            elif not is_ack:
                print('packet is not an ack (so corrupt), resend!\n\n')
            elif ack_num != self.sequence_number:
                print('receiver acked the previous pkt, resend!\n\n')
            else:
                print('packet is received correctly: seq. num ',
                      self.sequence_number, ' = ACK num ', ack_num,
                      '. all done!\n\n', sep='')
                return

            print('[ACK-Previous retransmission]:', self.app_msg_str)
            self.udt_send()  # stay in wait_for_ack state
