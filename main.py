import pygame
import os
from typing import List, Tuple
import pickle
from utils import *
import socket

pygame.font.init()  # initialise fonts
pygame.mixer.init()  # init sound

def main():
    """the main game loop function"""
    # connect to server
    host = socket.gethostname()  # as both code is running on same pc
    port = 5555  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    # initialisation
    win_text = ""
    clock = pygame.time.Clock()
    run = True

    while run:  # main loop
        clock.tick(FPS)
        gs = pickle.loads(client_socket.recv(1024*MULTIPL))# .decode())  # receive response
        #print("got pickle")
        client_socket.send("got pickle".encode())
        index = int(client_socket.recv(64).decode())
        client_socket.send("got index".encode())
        #print("got index:" + str(index))
        player1, player2 = gs.get()
        player = gs.get()[index]
        color = COLORS[index]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:  # this allows only one button at time to be pressed
                if event.key == pygame.K_e:  # shooting
                    player.shoot(color)
                #elif event.key == pygame.K_m:  # shooting
                #    player2.shoot(RED)

            if event.type == A_HIT:
                print("hit!")

        if player1.health <= 0:
            win_text = "Red wins"
        if player2.health <= 0:
            win_text = "Yellow wins"

        # movements
        keys_pressed = pygame.key.get_pressed()
        if index == 0:
            player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (10, WIDTH//2-50), (10, HEIGHT-50))
        else:
            player.move(keys_pressed, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, (WIDTH // 2, WIDTH - 50), (10, HEIGHT - 50))
        #player2.move(keys_pressed, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, (WIDTH//2, WIDTH-50), (10, HEIGHT-50))
        handle_bullets([player1, player2])
        draw_window([player1, player2])
        if win_text != "":
            draw_winner(win_text)
            break # get out the game loop
        gs.update([player1, player2])
        client_socket.send(pickle.dumps(gs))

    client_socket.close()
    pygame.quit()

if __name__ == "__main__":
    main()