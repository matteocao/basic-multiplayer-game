import asyncio
import pickle

import websockets
import pygame  # noqa

from utils import *

pygame.font.init()  # initialise fonts
pygame.mixer.init()  # init sound


async def main():
    """the main game loop function"""
    # connect to my server, ws://basic-multiplayer-gam.herokuapp.com
    async with websockets.connect("ws://localhost:5555") as client_socket:
        print("Connected!")

        # initialisation
        win_text = ""
        clock = pygame.time.Clock()
        run = True
        await client_socket.send("psw")
        while run:  # main loop
            clock.tick(FPS)
            # print("in the loop")
            gs = pickle.loads(await client_socket.recv())  # 1024*MULTIPL))# .decode())  # receive response
            # print("got pickle")
            await client_socket.send("got pickle")  # .encode())
            index = int(await client_socket.recv())  # 64).decode())
            await client_socket.send("got index")  # .encode())
            # print("got index:" + str(index))
            player1, player2 = gs.get()
            player = gs.get()[index]
            color = COLORS[index]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:  # this allows only one button at time to be pressed
                    if event.key == pygame.K_e:  # shooting
                        player.shoot(color)

                if event.type == A_HIT:
                    print("hit!")

            if player1.health <= 0:
                win_text = "Red wins"
            if player2.health <= 0:
                win_text = "Yellow wins"

            # movements
            keys_pressed = pygame.key.get_pressed()
            if index == 0:
                player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (10, WIDTH // 2 - 50),
                            (10, HEIGHT - 50))
            else:
                player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (WIDTH // 2, WIDTH - 50),
                            (10, HEIGHT - 50))

            handle_bullets([player1, player2])
            draw_window([player1, player2])
            if win_text != "":
                draw_winner(win_text)
                break  # get out the game loop
            gs.update([player1, player2])

            await client_socket.send(pickle.dumps(gs))

        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
