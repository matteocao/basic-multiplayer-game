import socket
from utils import *
import pygame
import pickle
import signal
from _thread import *
import os
import websockets
import asyncio


clock = pygame.time.Clock()
thread_count = 0

async def threaded_client(conn, gs, index):
    #print("threaded client called " + str(index))

    # print("send pickle from " + str(index))
    await conn.send(pickle.dumps(gs))  # broadcast?
    await conn.recv()#64).decode()  # receive confirmation
    # print("send index from " + str(index))
    await conn.send(str(index))#.encode())
    await conn.recv()#64).decode()  # receive confirmation
    # data = connection.recv(1024*10)
    data = await conn.recv() #1024 * MULTIPL)) # receive status update ffrom client x
    player = pickle.loads(data).players[index]
    return player


# initialise players
player1 = Player("YELLOW_TRANSF_IMG", 10, [], (300, 100), (10, 10))
player2 = Player("RED_TRANSF_IMG", 10, [], (700, 100), (WIDTH - 250, 10))

# players for broadcasting
players = [player1, player2]

# initialise game status
gs = GameStatus([player1, player2])


def re_initialisation():
    global gs
    # initialise players
    player1 = Player("YELLOW_TRANSF_IMG", 10, [], (300, 100), (10, 10))
    player2 = Player("RED_TRANSF_IMG", 10, [], (700, 100), (WIDTH - 250, 10))

    # initialise game status
    gs = GameStatus([player1, player2])


async def loop_fn(conn):
    global thread_count
    global gs
    global players
    #connections.append(conn)
    print("in loop_fn()")
    #while True:
    #conn, address = server_socket.accept()  # accept new connection. stop loop until new connection
    #data = await conn.recv()#1024 * MULTIPL).decode()
    #print("data: ", str(data))
    #await conn.send("hi!")#.encode())
    akw = await conn.recv()#64).decode()

    if "psw" == akw:
        print("Password OK!")
        #print('Connected to: ' + address[0] + ':' + str(address[1]))
        # normal_client(conn, gs)
        thread_count += 1
        print('Thread Number: ' + str(thread_count))
        #connections.append(conn)

        #for index, conn in enumerate(connections):
        index = thread_count % 2
        print("Start new client " + str(index))
        while True:
            clock.tick(FPS)
            players[index] = await threaded_client(conn, gs, index)
            gs.update(players)
        if index == 0:
            thread_count = 0
            re_initialisation()


    else:
        print("Wrong password: " + str(akw))
    connections.remove(conn)


async def server_program():
    print("starting server...")
    # get the hostname
    #host = socket.gethostname()
    ON_HEROKU = os.environ.get('ON_HEROKU')

    if ON_HEROKU:
        # get the heroku port
        port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
    else:
        port = 5555
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    async with websockets.serve(loop_fn, "", port) as start_server:
        await stop #asyncio.Future()  # run forever
    #server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    #try:
    #    server_socket.bind((host, port))
    #except socket.error as e:
    #    print(str(e))

    # configure how many client the server can listen simultaneously
    #server_socket.listen(6)




        #server_socket.close()

if __name__ == '__main__':
    asyncio.run(server_program())