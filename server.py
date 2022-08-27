import socket
from utils import  *
import pygame
import pickle
from _thread import *


def server_program():
    # get the hostname
    host = socket.gethostname()
    port = 5555  # initiate port no above 1024
    thread_count = 0
    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    try:
        server_socket.bind((host, port))
    except socket.error as e:
        print(str(e))

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)

    def threaded_client(conn, gs, index):
        while True:
            clock.tick(FPS)
            #print("send pickle from " + str(index))
            conn.sendall(pickle.dumps(gs))
            conn.recv(64).decode()
            #print("send index from " + str(index))
            conn.sendall(str(index).encode())
            conn.recv(64).decode()
            #data = connection.recv(1024*10)
            gs.update(pickle.loads(conn.recv(1024 * MULTIPL)).players)
        conn.close()

    def normal_client(conn, gs, index):
        """not t use, just for basic testing"""
        while True:
            clock.tick(FPS)
            conn.send(pickle.dumps(gs))  # data.encode())
            conn.recv(64).decode()
            conn.send(str(index).encode())
            conn.recv(64).decode()
            # receive data stream. it won't accept data packet greater than 1024 bytes
            gs.update(pickle.loads(conn.recv(1024 * MULTIPL)).players)
            #gs = pickle.loads(conn.recv(1024 * 10))  # .decode()
        conn.close()  # close the connection


    clock = pygame.time.Clock()
    connections = []
    while True:
        conn, address = server_socket.accept()  # accept new connection. stop loop until new connection
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        #normal_client(conn, gs)
        thread_count += 1
        print('Thread Number: ' + str(thread_count))
        connections.append(conn)
        if thread_count == 2:
            # initialise players
            player1 = Player("YELLOW_TRANSF_IMG", 10, [], (300, 100), (10, 10))
            player2 = Player("RED_TRANSF_IMG", 10, [], (700, 100), (WIDTH - 250, 10))

            # initialise game status
            gs = GameStatus([player1, player2])
            
            for index, conn in enumerate(connections):
                print("Start new client " + str(index))
                start_new_thread(threaded_client, (conn, gs, index))
            thread_count = 0
            connections = []

    server_socket.close()








if __name__ == '__main__':
    server_program()