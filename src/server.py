#!/usr/bin/python

from socket import socket, AF_INET, SOCK_STREAM
from select import select

from settings import PORT, BUFSIZE, MAGIC_NUM, BROADCAST_MSG
from utils import create_broadcast_socket

def broadcast_data(sock, msg, clients):
    for client in clients:
        if client != sock:
            try:
                client.send(msg)
            except Exception as err:
                print(err)

def main():
    print('Server is up!')

    brdcst_sock = create_broadcast_socket()
    srv_sock = socket(AF_INET, SOCK_STREAM)
    srv_sock.bind(('', PORT))
    srv_sock.listen(2)
    clients = []

    try:
        brdcst_sock.bind(('', PORT))
        while True:
            read, write, err = select(
            [brdcst_sock, srv_sock] + clients, [], [])

            for sock in read:
                if sock is brdcst_sock:
                    msg, addr = brdcst_sock.recvfrom(BUFSIZE)
                    if msg == BROADCAST_MSG:
                        brdcst_sock.sendto(MAGIC_NUM, addr)
                elif sock is srv_sock:
                    client, addr = srv_sock.accept()
                    clients.append(client)
                    print('Client connected ({0})'.format(addr[0]))
                    broadcast_data(client,
                    '{0} entered room'.format(addr[0]), clients)
                else:
                    msg = sock.recv(BUFSIZE)
                    if msg == '':
                        clients.remove(sock)
                        print('Client disconnected ({0})'.format(
                        sock.getpeername()[0]))
                    else:
                        ipaddr = sock.getpeername()[0]
                        broadcast_data(sock, '{0}: {1}'.format(ipaddr, 
                        msg),
                        clients)
    finally:
        for client in clients:
            client.close()
        brdcst_sock.close()


if __name__ == '__main__':
    main()

