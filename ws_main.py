import asyncio
import pickle

import websockets
import pygame  # noqa

from utils import *

pygame.font.init()  # initialise fonts
pygame.mixer.init()  # init sound

bullets = []


async def main():
    global bullets
    """the main game loop function"""
    # connect to my server, ws://basic-multiplayer-gam.herokuapp.com
    async with websockets.connect("ws://localhost:5555") as client_socket:
        print("Connected!")

        # initialisation
        clock = pygame.time.Clock()
        run = True
        await client_socket.send("psw")
        # initialise
        players = pickle.loads(await client_socket.recv())
        await client_socket.send("got the players")
        index = int(await client_socket.recv())  # index of the player
        await client_socket.send("got index")  # .encode())
        color = COLORS[index]
        while run:  # main loop
            clock.tick(FPS)
            # print("in the loop")
            player = players[index]
            # move and shoot

            dtob = DTOB(1, 1, index, False)  # dummy!
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:  # this allows only one button at time to be pressed
                    if event.key == pygame.K_e:  # shooting
                        try:
                            dtob = player.shoot(color, index, bullets).dumps()
                        except AttributeError:
                            dtob = DTOB(1, 1, index, False)  # dummy!

                if event.type == A_HIT:
                    print("hit!")

            # movements
            keys_pressed = pygame.key.get_pressed()
            if index == 0:
                player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (10, WIDTH // 2 - 50),
                            (10, HEIGHT - 50))
            else:
                player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (WIDTH // 2, WIDTH - 50),
                            (10, HEIGHT - 50))

            # send one single player and the new bullet
            dto = player.dumps()
            await client_socket.send(pickle.dumps([dto, dtob]))

            # new game status
            dto1, dto2, dtobs = pickle.loads(await client_socket.recv())
            await client_socket.send("confirmed!")
            bullets = [Bullet(1, 1, players[dtob.index], index).loads(dtob) for dtob in dtobs]
            players[0].loads(dto1)
            players[1].loads(dto2)

            # is there a winner?
            win_text = await client_socket.recv()  # receive win text
            await client_socket.send("got win_text!")

            # drawing
            draw_window(players, bullets)
            if win_text != "":
                draw_winner(win_text)
                break  # get out the game loop

        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
