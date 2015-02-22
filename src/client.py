#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, error
import tkinter as tk

from settings import PORT, BUFSIZE, MAGIC_NUM, BROADCAST_MSG
from utils import create_broadcast_socket
from fsm import FiniteStateMachine


class ChatApplication(tk.Frame, FiniteStateMachine):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        FiniteStateMachine.__init__(self)
        self.grid()
        self.create_widgets()

        self.change_state(ClientBroadcastState())

    def create_widgets(self):
        self.text_box = tk.Text(self, state=tk.DISABLED)
        self.text_box.grid()

        self.textin_var = tk.StringVar()
        self.textin = tk.Entry(self, textvariable=self.textin_var)
        self.textin.grid(row=1, column=0)

        self.send_btn = tk.Button(self, text='Send')
        self.send_btn.grid(row=1, column=1)

class ClientBroadcastState(object):
    def __init__(self):
        self.bcast_sock = create_broadcast_socket()
        self.bcast_sock.setblocking(False)
        self.client = None
        self.done = False

    def enter(self, fsm, _):
        self.client = fsm
        self.client.send_btn.config(state=tk.DISABLED)
        self.client.after(500, func=self.broadcast)

    def broadcast(self):
        print('broadcasting')
        self.bcast_sock.sendto(BROADCAST_MSG, ('<broadcast>', PORT))

        try:
            msg, addr = self.bcast_sock.recvfrom(BUFSIZE)

            if msg == MAGIC_NUM:
                comm_sock = socket(AF_INET, SOCK_STREAM)
                comm_sock.connect((addr[0], PORT))
                self.done = True
                self.bcast_sock.close()
                self.client.change_state(ClientConnectedState(comm_sock))
        except error:
            pass

        if not self.done:
            self.client.after(500, func=self.broadcast)


class ClientConnectedState(object):
    def __init__(self, conn):
        self.conn = conn
        self.conn.setblocking(False)
        self.client = None

    def enter(self, fsm, _):
        self.client = fsm
        self.client.send_btn.config(state=tk.NORMAL,
        command=self.send_message)
        self.client.master.bind('<Return>', self.send_message)

        self.client.after(500, func=self.fetch_messages)

    def send_message(self, *_):
        msg = self.client.textin_var.get()
        if msg == '':
            return
        self.client.textin_var.set('')
        self.client.text_box.config(state=tk.NORMAL)
        self.client.text_box.insert(tk.END, 'You: {0}\n'.format(msg))
        self.client.text_box.config(state=tk.DISABLED)

        try:
            self.conn.send(msg.encode())
        except error:
            pass

    def fetch_messages(self):
        try:
            msg = self.conn.recv(BUFSIZE).decode()
            if not msg:
                self.client.change_state(ClientBroadcastState())
            else:
                self.client.text_box.config(state=tk.NORMAL)
                self.client.text_box.insert(tk.END,
                'Somebody: {0}\n'.format(msg))
                self.client.text_box.config(state=tk.DISABLED)
        except error:
            pass

        self.client.after(500, func=self.fetch_messages)

def main():
    root = tk.Tk()
    app = ChatApplication(root)
    app.mainloop()

if __name__ == '__main__':
    main()
