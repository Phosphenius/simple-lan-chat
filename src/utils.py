# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

def create_broadcast_socket():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    return sock
