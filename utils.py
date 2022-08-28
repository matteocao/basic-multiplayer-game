import os
from typing import List, Tuple

import pygame


try:
    pygame.font.init()  # initialise fonts
    pygame.mixer.init()  # init sound
except:  # in case no audio devices  # noqa
    os.environ['SDL_AUDIODRIVER'] = 'dsp'
    pass


class Bullet:
    """class handling the bullet"""
    def __init__(self, color, obj, player):
        self.color = color
        self.obj = obj
        self.player = player

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.obj)

    def move(self, opponent, vel, x_allowed):
        self.obj.x += vel
        if opponent.obj.colliderect(self.obj):
            pygame.event.post(pygame.event.Event(A_HIT))  # broadcasting the event, not really used here
            opponent.got_hit()
            self.player.bullets.remove(self)
        elif not (x_allowed[0] <= self.obj.x <= x_allowed[1]):
            self.player.bullets.remove(self)


class Player:
    VEL_SPACESHIP = 5
    MAX_BULLETS = 3

    def __init__(self, spaceship_img: str,
                 health: int,
                 bullets: List[Bullet],
                 position: Tuple[int, int],
                 pos_health: Tuple[int, int]):
        self.spaceship_img = spaceship_img
        self.health = health
        self.bullets = bullets
        self.obj = pygame.Rect(*position, *SPACE_SHIP_SIZE)
        self.pos_health = pos_health

    def got_hit(self):
        self.health -= 1
        BULLET_HIT_SOUND.play()

    def draw(self, win):
        win.blit(eval(self.spaceship_img), (self.obj.x, self.obj.y))

    def draw_health(self, win):
        health_text = HEALTH_FONT.render("Health: " + str(self.health), True, WHITE)
        win.blit(health_text, self.pos_health)

    def move(self, keys_pressed, left, right, up, down, x_allowed, y_allowed):
        if keys_pressed[left] and x_allowed[0] <= (self.obj.x - self.VEL_SPACESHIP) <= x_allowed[1]:  # LEFT
            self.obj.x -= self.VEL_SPACESHIP
        if keys_pressed[right] and x_allowed[0] <= (self.obj.x + self.VEL_SPACESHIP) <= x_allowed[1]:  # RIGHT
            self.obj.x += self.VEL_SPACESHIP
        if keys_pressed[up] and y_allowed[0] <= (self.obj.y - self.VEL_SPACESHIP) <= y_allowed[1]:  # UP
            self.obj.y -= self.VEL_SPACESHIP
        if keys_pressed[down] and y_allowed[0] <= (self.obj.y + self.VEL_SPACESHIP) <= y_allowed[1]:  # DOWN
            self.obj.y += self.VEL_SPACESHIP

    def shoot(self, color):
        if len(self.bullets) <= self.MAX_BULLETS:
            obj = pygame.Rect(self.obj.x, self.obj.y + self.obj.height // 2, 10, 5)
            bullet = Bullet(color, obj, self)
            self.bullets.append(bullet)
            BULLET_FIRE_SOUND.play()


class GameStatus:
    """this class contains the info about the game status that
    needs to be shared between client and server"""

    def __init__(self, players):
        self.players = players

    def update(self, players):
        self.players = players

    def get(self):
        return self.players


# hits UID
A_HIT = pygame.USEREVENT + 1  # this is just a UID

# color data
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
COLORS = (YELLOW, RED, BLACK, WHITE)

# fonts data
HEALTH_FONT = pygame.font.SysFont("comicsans", 40)
WINNER_FONT = pygame.font.SysFont("comicsans", 90)

# background data
WIDTH, HEIGHT = 900, 500
try:
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # window of the game
except:  # no video device available on server  # noqa
    pass

BORDER = pygame.Rect(WIDTH / 2 - 5, 0, 10, HEIGHT)  # middle barrier
SPACE = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "space.png")), (WIDTH, HEIGHT))

# fps
FPS = 30

# spaceship images (load and transform)
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_yellow.png"))
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_red.png"))
SPACE_SHIP_SIZE = (55, 40)
YELLOW_TRANSF_IMG = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, SPACE_SHIP_SIZE), 90)
RED_TRANSF_IMG = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, SPACE_SHIP_SIZE), -90)

# sounds
if pygame.mixer.get_init() is not None:
    BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Gun+Silencer.mp3"))
    BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Grenade+1.mp3"))


def draw_window(players):
    """draw all objects"""
    WIN.blit(SPACE, (0, 0))  # background
    pygame.draw.rect(WIN, BLACK, BORDER)  # middle bar
    for player in players:
        player.draw_health(WIN)  # (WIDTH - red_health_text.get_width() -10, 10)
        player.draw(WIN)
        for bullet in player.bullets:
            bullet.draw(WIN)
    pygame.display.update()  # update the window display


def draw_winner(text):
    """draw winning text"""
    win_text = WINNER_FONT.render("Winner: " + text, True, WHITE)
    WIN.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(5000)


def handle_bullets(players):
    """move bullets around"""
    for bullet in players[0].bullets:
        bullet.move(players[1], 8, (0, WIDTH))
    for bullet in players[1].bullets:
        bullet.move(players[0], -8, (0, WIDTH))
