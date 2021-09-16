import random   # To generate random numbers
import sys      # To use sys.exit to exit the program/game
import pygame   
from pygame.locals import *     # Basic pygame imports

# Global Variables for the game
FPS = 32    # frames per second
SCREENWIDTH = 289 
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) # initialize a window screen
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

def welcome_screen():
    """
    Displays Welcome images on the screen
    """
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2) # To display player on the center
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():    # when user performs an event on game
            # if user clicks on cross (x) button, then close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # if user presser space or up arrow key, start the game
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def main_game():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # list of upper pipes
    upper_pipes = [
        {'x': SCREENWIDTH+200, 'y': new_pipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': new_pipe2[0]['y']},
    ]
    # list of lower pipes
    lower_pipes = [
        {'x': SCREENWIDTH+200, 'y': new_pipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': new_pipe2[1]['y']},
    ]

    pipe_velx = -4
    player_vely = -9
    player_max_vely = 10
    player_min_vely = -8
    player_acc_vely = 1

    player_flap_accv = -8   # velocity while flapping
    player_flapped = False  # True only when bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    player_vely = player_flap_accv
                    player_flapped = True
                    GAME_SOUNDS['wing'].play()
        
        crash_test = is_collide(playerx, playery, upper_pipes, lower_pipes) # True if player is crashed
        if crash_test:
            return

        # Check score
        player_mid_pos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if player_vely < player_max_vely and not player_flapped:
            player_vely += player_acc_vely

        if player_flapped:
            player_flapped = False
        player_height = GAME_SPRITES['player'].get_height()
        playery = playery + min(player_vely, GROUNDY - playery - player_height)

        # move pipes to the left
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_velx
            lower_pipe['x'] += pipe_velx

        # add a new pipe when first pipe is about to cross left most part of screen
        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # if pipe is out of the screen, remove it
        if upper_pipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # Blit our sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lower_pipe['x'], lower_pipe['y']))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        my_digits = [int(x) for x in list(str(score))]
        width = 0
        for digit in my_digits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        x_offset = (SCREENWIDTH - width) / 2

        for digit in my_digits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (x_offset, SCREENHEIGHT*0.12))
            x_offset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def is_collide(playerx, playery, upper_pipes, lower_pipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upper_pipes:
        pipe_height = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipe_height + pipe['y'] and abs(playerx - pipe['x']) < 
        GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    for pipe in lower_pipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x'])< GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True
    return False

        

def get_random_pipe():
    """""""""
    Generate positions of two pipes (one straight & one rotated) for blitting the screen
    """
    pipe_height = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2*offset))
    pipex = SCREENWIDTH + 10
    y1 = pipe_height - y2 + offset
    pipe = [
        {'x' : pipex, 'y': -y1},    # Upper pipe
        {'x' : pipex, 'y': y2}
    ]
    return pipe


if __name__ == "__main__":
    # Our game starts from here
    print("hi")
    pygame.init()   # Initializes all pygame's module
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird by Sujal Duwa")
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),   
         # convert_alpha() optimizes the image
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),   
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )

    #Game images
    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha() 
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha() 
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),  # rotates to generate inverted pipe in the game
        pygame.image.load(PIPE).convert_alpha()  
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    #Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    while True:
        welcome_screen()    # shows welcome screen until a button is pressed
        main_game()         # the main function of game
