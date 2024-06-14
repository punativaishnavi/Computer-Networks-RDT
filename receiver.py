"""
CPSC 5510, Seattle University, Project #2
This is free and unencumbered software released into the public domain.
:Author: Vaishnavi Punati
:Version: s23

NOTE: Run this file first, before the sender is constructed.
"""
from socket import *
from time import sleep
from util import *


class Receiver(object):
    """The receiver side of RDT 3.0, stop-and-wait."""

    def __init__(self):
        self.seq_num = 0
        self.packet_num = 0
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.bind(('localhost', RECEIVER_PORT))
        self.packet = None
        self.whom = None
        self.sender = None
        self.packet_is_ack = None
        self.packet_seq_num = None

    def __del__(self):
        self.udp.close()

    def wait_for_n_from_below(self):
        """This method is either of the two states from the FSM for the
        receiver.
        """
        while True:
            self.rdt_receive()
            if not self.corrupt() and self.has_correct_sequence():
                message = extract(self.packet)
                self.deliver_data(message)
                print('packet is delivered, now creating and sending the ACK '
                      'packet...')
                self.udt_send(make_packet('', True, self.seq_num))
                print('all done for this packet!\n\n')
                self.seq_num = other(self.seq_num)
            else:
                if self.packet_num % 3 != 0:
                    print('packet is not correct, so sending previous ack')
                self.udt_send(make_packet('', True, other(self.seq_num)))
                print('all done for this packet!\n\n')

    @staticmethod
    def deliver_data(message):
        """Stub to represent delivering data to the application"""
        print('packet is expected, message string delivered:', message)

    def rdt_receive(self):
        """Receive from the communication layer below"""

        # Requirement: number all the received packet from 1
        self.packet_num += 1

        self.packet, self.sender = self.udp.recvfrom(4096)
        self.packet_is_ack, self.packet_seq_num = get_bits(self.packet)
        print('packet num.{} received:'.format(self.packet_num), self.packet)

        # Requirement: simulate timeout for packets divisible by 6
        if self.packet_num % 6 == 0:
            print('simulating packet loss: sleep a while to trigger event on '
                  'the send side...')
            print('all done for this packet!\n\n')
            sleep(TIMEOUT)
            return self.rdt_receive()

        # Requirement: simulate packet corruption for packets divisible by 3
        if self.packet_num % 3 == 0:
            print('simulating packet bit errors/corrupted: ACK the previous '
                  'packet!')
            packet = bytearray(self.packet)
            packet[0] += 1  # put in any sort of corruption
            self.packet = packet

    def corrupt(self):
        """check if packet is corrupt"""
        if self.packet_is_ack:
            print('packet is an ACK!')
        return self.packet_is_ack or not verify_checksum(self.packet)

    def has_correct_sequence(self):
        """check if packet has expected sequence number"""
        return self.packet_seq_num == self.seq_num

    def udt_send(self, packet):
        """use the underlying communication channel to send the ACK"""
        self.udp.sendto(packet, self.sender)


if __name__ == '__main__':
    Receiver().wait_for_n_from_below()
