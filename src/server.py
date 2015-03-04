#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, error
from select import select
import sys

from settings import PORT, BUFSIZE, MAGIC_NUM, BROADCAST_MSG
from utils import create_broadcast_socket

def broadcast_data(sock, msg, clients):
    for client in clients:
        if client != sock:
            try:
                client.send(msg.encode())
            except error as err:
                print(err)

def prompt():
    sys.stdout.write('> ')
    sys.stdout.flush()


def main():
    print('Server is up!')
    prompt()
    
    running = True
    brdcst_sock = create_broadcast_socket()
    srv_sock = socket(AF_INET, SOCK_STREAM)
    srv_sock.bind(('', PORT))
    srv_sock.listen(2)
    clients = []

    try:
        brdcst_sock.bind(('', PORT))
        while running:
            readable, _, _ = select(
            [brdcst_sock, srv_sock, sys.stdin] + clients, [], [])

            for sock in readable:
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
                    prompt()
                elif sock is sys.stdin:
                    cmd = sys.stdin.readline().strip()
                    
                    if cmd == 'exit' or cmd == 'shutdown':
                        print('shutting down...')
                        brdcst_sock.close()
                        srv_sock.close()
                        
                        for client in clients:
                            client.close()
                            
                        running = False
                        break
                    elif cmd == 'lsclients':
                        for client in clients:
                            prompt()
                            print(client.getpeername())
                    prompt()
                else:
                    msg = sock.recv(BUFSIZE).decode()
                    if msg == '':
                        clients.remove(sock)
                        print('Client disconnected ({0})'.format(
                        sock.getpeername()[0]))
                        prompt()
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

