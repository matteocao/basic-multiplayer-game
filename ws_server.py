from _thread import *  # noqa
import asyncio
import signal

import websockets
import pickle

from utils import *


clock = pygame.time.Clock()
thread_count = 0


async def threaded_client(conn, gstate, index):
    # print("threaded client called " + str(index))

    # print("send pickle from " + str(index))
    await conn.send(pickle.dumps(gstate))  # broadcast?
    await conn.recv()  # receive confirmation
    # print("send index from " + str(index))
    await conn.send(str(index))
    await conn.recv()  # receive confirmation
    data = await conn.recv()  # receive status update from client x
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
    player1 = Player("YELLOW_TRANSF_IMG", 10, [], (300, 100), (10, 10))  # noqa
    player2 = Player("RED_TRANSF_IMG", 10, [], (700, 100), (WIDTH - 250, 10))  # noqa

    # initialise game status
    gs = GameStatus([player1, player2])


async def loop_fn(conn):
    global thread_count
    global gs
    global players
    # connections.append(conn)
    print("in loop_fn()")
    akw = await conn.recv()  # 64).decode()

    if "psw" == akw:
        print("Password OK!")
        thread_count += 1
        print('Thread Number: ' + str(thread_count))
        # connections.append(conn)

        # for index, conn in enumerate(connections):
        index = thread_count % 2
        print("Start new client " + str(index))
        try:
            while True:
                clock.tick(FPS)
                players[index] = await threaded_client(conn, gs, index)
                gs.update(players)
        except websockets.exceptions.ConnectionClosedOK:
            thread_count -= 1
            print('Thread Number: ' + str(thread_count))
            re_initialisation()

    else:
        print("Wrong password: " + str(akw))


async def server_program():
    print("starting server...")
    # get the hostname
    ON_HEROKU = os.environ.get('ON_HEROKU')

    if ON_HEROKU:
        # get the heroku port
        port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995
        host = ""
    else:
        port = 5555
        host = "localhost"
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    print("Server at: ", host, port)
    async with websockets.serve(loop_fn, host, port):
        await stop  # asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(server_program())
