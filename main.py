"""
CPSC 5510, Seattle University, Project #2
This is free and unencumbered software released into the public domain.
:Author: Vaishnavi Punati
:Version: s23
"""
from sender import Sender

# note: no arguments will be passed in
sender = Sender()

for i in range(1, 10):
    # this is where your rdt_send will be called
    sender.rdt_send('msg' + str(i))
