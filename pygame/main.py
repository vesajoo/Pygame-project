import pygame
import random
import os


pygame.init()

#Window dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Test')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#Game variables
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0
if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else: 
    high_score = 0

#define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
PANEL = (153, 217, 234)

#define font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

#load images
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
jumpy_image = pygame.image.load('assets/jump.png').convert_alpha()
platform_image = pygame.image.load('assets/wood.png').convert_alpha()

#function for outputting text on screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function for drawing info panel
def draw_panel():
    pygame.draw.rect(screen, PANEL, (0,0,SCREEN_WIDTH, 30))
    pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

#Function for drawing background
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0,0 + bg_scroll))
    screen.blit(bg_image, (0,-600 + bg_scroll))

#player class
class Player():
    def __init__(self, x, y) -> None:
        self.image = pygame.transform.scale(jumpy_image,(45,45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.rect.center = (x,y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        #Reset variables
        scroll = 0
        dx = 0
        dy = 0

        #Process keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True

        if key[pygame.K_d]:
            dx = 10
            self.flip = False
        
        #Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #Ensure player doesn't go off the screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left

        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        #Check collision with platforms
        for platform in platform_group:
            #Collision in y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #Check if above the platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20


        #Check if player bounced to top of screen
        if self.rect.top <= SCROLL_THRESH:
            #if player is jumping
            if self.vel_y < 0:
                scroll = -dy


        #Update rect position
        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x-12, self.rect.y-5))
        pygame.draw.rect(screen, WHITE, self.rect, 2)

#Platform class
class Platform(pygame.sprite.Sprite):

    def __init__(self, x, y, width) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        #Update platforms vertical position
        self.rect.y += scroll
        #check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


#Player instance
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

#Create sprite groups
platform_group = pygame.sprite.Group()

#Create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200)
platform_group.add(platform)


#Game loop
while True:

    clock.tick(FPS)

    if game_over == False:

        scroll = jumpy.move()

        #draw background
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        #Generate platforms
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            platform = Platform(p_x, p_y, p_w)
            platform_group.add(platform)

        #update platforms
        platform_group.update(scroll)

        #update score
        if scroll > 0:
            score += scroll

        #draw line at previous high score
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

        #draw sprites
        platform_group.draw(screen)
        jumpy.draw()

        #draw panel
        draw_panel()
        
        #Check game over
        if jumpy.rect.top > SCREEN_HEIGHT:
            game_over = True

    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 15
            for y in range(0, 6, 2):
                pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y+1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text('GAME OVER!', font_big, WHITE, 130, 200)
            draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 30, 300)
        #update high score
        if score > high_score:
            high_score = score
            with open('score.txt','w') as file:
                file.write(str(high_score))

        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            #reset variables
            game_over = False
            score = 0
            scroll = 0
            fade_counter = 0
            #reposition jumpy
            jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
            #reset platforms
            platform_group.empty()
            #Create starting platform
            platform = Platform(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200)
            platform_group.add(platform)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    pygame.display.update()

pygame.quit()