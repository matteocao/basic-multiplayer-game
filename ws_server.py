from _thread import *  # noqa
import asyncio
import signal

import websockets
import pickle

from utils import *


clock = pygame.time.Clock()
thread_count = 0


async def send_bullets(bullts, conn):
    dtobs = []
    for _, bullet in enumerate(bullts):
        dtobs.append(bullet.dumps())
    await conn.send(pickle.dumps(dtobs))


async def is_there_winner(plyers, conn):
    win_text = ""
    if plyers[0].health <= 0:
        win_text = "Red wins"
    if plyers[1].health <= 0:
        win_text = "Yellow wins"
    await conn.send(win_text)  # send win text
    await conn.recv()  # confirmation


async def threaded_client(conn, plyers, index):
    global bullets

    # update pos bullets health
    data = await conn.recv()
    print(len(data))
    dto, dtob = pickle.loads(data)  # receive single player and single bullet data
    plyers[index].obj = dto.obj
    if dtob.is_new:
        bullet = Bullet(1, 1, plyers[index], index).loads(dtob)
        bullets.append(bullet)
    bullets, plyers = handle_bullets(bullets, plyers)

    return plyers

# initialise players
player1 = Player("YELLOW_TRANSF_IMG", 10, (300, 100), (10, 10))
player2 = Player("RED_TRANSF_IMG", 10, (700, 100), (WIDTH - 250, 10))

# initialise bullets
bullets = []

# players for broadcasting
players = [player1, player2]


def re_initialisation():
    # initialise players
    global players
    global bullets
    player1 = Player("YELLOW_TRANSF_IMG", 10, (300, 100), (10, 10))  # noqa
    player2 = Player("RED_TRANSF_IMG", 10, (700, 100), (WIDTH - 250, 10))  # noqa
    bullets = []
    players = [player1, player2]


async def loop_fn(conn):
    global thread_count
    global players
    global bullets
    print("in loop_fn()")
    akw = await conn.recv()  # 64).decode()

    if "psw" == akw:
        print("Password OK!")
        thread_count += 1
        print('Thread Number: ' + str(thread_count))
        # connections.append(conn)

        # for index, conn in enumerate(connections):
        index = thread_count % 2
        print("Start connection with new client " + str(index))
        try:
            # initialise
            await conn.send(pickle.dumps(players))
            await conn.recv()  # confirmation
            print("threaded client called " + str(index))
            await conn.send(str(index))
            await conn.recv()  # receive confirmation
            while True:
                clock.tick(FPS)
                # get data from client actions
                players = await threaded_client(conn, players, index)
                # aggregate and send
                dto1, dto2 = players[0].dumps(), players[1].dumps()
                dtobs = [bullet.dumps() for bullet in bullets]
                print(len(pickle.dumps([dto1, dto2, dtobs])))
                await conn.send(pickle.dumps([dto1, dto2, dtobs]))  # broadcast?
                await conn.recv()  # receive confirmation
                await is_there_winner(players, conn)
                print("end of client loop")

        except websockets.exceptions.ConnectionClosedOK:  # noqa
            thread_count -= 1
            print('Thread Number: ' + str(thread_count))
            print("re-initialising...")
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
