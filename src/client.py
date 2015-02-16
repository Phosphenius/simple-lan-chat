#!/usr/bin/python

from socket import socket, AF_INET, SOCK_STREAM
from threading import Timer
from thread import start_new_thread
from select import select
import sys

from settings import (PORT, BUFSIZE, MAGIC_NUM, BROADCAST_MSG,
                        CLIENT_BROADCAST_INTERVAL)
from utils import create_broadcast_socket
from fsm import FiniteStateMachine

class ClientBroadcastState(object):
    def __init__(self):
        self.client = None
        self.brdcst_sock = create_broadcast_socket()
        self.brdcst_sock.setblocking(False)

    def enter(self, fsm, old_state):
        self.client = fsm
        self.broadcast()

    def broadcast(self):
        print('Searching for server...')

        self.brdcst_sock.sendto(BROADCAST_MSG, ('<broadcast>', PORT))

        timer = Timer(CLIENT_BROADCAST_INTERVAL, self.broadcast)
        timer.start()

        try:
            msg, addr = self.brdcst_sock.recvfrom(BUFSIZE)
            if msg == MAGIC_NUM:
                print 'Found server at: {0}'.format(addr[0])
                comm_sock = socket(AF_INET, SOCK_STREAM)
                try:
                    comm_sock.connect((addr[0], PORT))
                    print 'Successfully connected!'
                    self.brdcst_sock.close()
                    timer.cancel()
                    self.client.change_state(
                    ClientConnectedState(comm_sock))
                except Exception as ex:
                    print('Cannot connect {0}'.format(ex))
        except:
            pass


class ClientConnectedState(object):
    def __init__(self, comm_sock):
        self.comm_sock = comm_sock
        self.input_queue = []

    def prompt(self):
        sys.stdout.write('>> ')
        sys.stdout.flush()

    def enter(self, fsm, old_state):
        self.prompt()
        while True:
            read, write, err = select([self.comm_sock, sys.stdin],
            [], [])

            for sock in read:
                if sock is self.comm_sock:
                    msg = sock.recv(BUFSIZE)
                    if not msg:
                        print 'Disconnected from server!'
                        fsm.change_state(ClientBroadcastState())
                    else:
                        sys.stdout.write(msg)
                        self.prompt()
                else:
                    msg = sys.stdin.readline()
                    self.comm_sock.send(msg)
                    self.prompt()


class ChatClient(FiniteStateMachine):
    def __init__(self):
        FiniteStateMachine.__init__(self)


    def start(self):
        self.change_state(ClientBroadcastState())

def main():
    client = ChatClient()
    client.start()

if __name__ == '__main__':
    main()
