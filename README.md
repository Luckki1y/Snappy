# Snappy

Snappy is a automation script for running snapshots off a RFSoc 4x2. This python package works by creating an ssh session into the RFSoc, starting the souk readout server
and a persistent python enviorment within the board. This allows the program to send commands to run and therefore take snapshots.

## Installation

To install:

## Setup

To setup this project after installing the dependencies and the files, create a new file called ssh_identities.py. Within this file add the following
'''python

username = YOUR_USERNAME

host = YOUR_HOST

password = YOUR_PASSWORD

'''
This is all needed to ensure the paramiko module can successfully create a ssh session into your RFSoc

