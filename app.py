import pygame
from pygame.locals import *
import random

pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 4096)
# achtergrond muziek
pygame.mixer.music.load("audio/bitsurf.ogg")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.6)


jump = pygame.mixer.Sound("audio/jump-sound.ogg")
death = pygame.mixer.Sound("audio/PUNCH_2.ogg")
hitpipe = pygame.mixer.Sound("audio/hitpipe.ogg")
ding = pygame.mixer.Sound("audio/sfx_point.ogg")
ding.set_volume(0.3)
coin_sound = pygame.mixer.Sound("audio/collect_coin.ogg")
coin_sound.set_volume(0.2)
clock = pygame.time.Clock()
fps = 60
width = 648
height = 702


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Python Bird")
#fonts
font = pygame.font.Font("Minecraft.ttf", 50)
font_hs = pygame.font.Font("Minecraft.ttf", 20)
# variables
ground_scroll = 0
scroll_speed = 4
isFlying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
high_score = 0
hs = "HIGH SCORE: "

# fotos
background = pygame.image.load("img/bg.png")
grond = pygame.image.load("img/ground.png")
button_img = pygame.image.load("img/restart.png")


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# reset score

def reset_game():
    pipe_group.empty()
    coin_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(height / 2)
    score = 0
    return score


# Sprite opzetten (stupid bird)
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if isFlying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 576:
                self.rect.y += int(self.vel)

        if game_over == False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
                jump.play()
            if pygame.key.get_pressed()[pygame.K_SPACE] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
                jump.play()
            if (
                pygame.mouse.get_pressed()[0] == 0
                and pygame.key.get_pressed()[pygame.K_SPACE] == 0
            ):
                self.clicked = False

            # Animatie
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            # Draait vogel om
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

#pipes 
class Pipes(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        # positie 1 is top, -1 is grond
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

#coins aanmaken
class coins(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,7):
            img =  pygame.image.load(f'img/coin{num}.png')
            img = pygame.transform.smoothscale(img, (50, 50))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]
      

    def update(self):
        self.rect.x -= scroll_speed

        #coins animation
        if game_over == False:
            self.counter += 1
            spin_cooldown = 8
            if self.counter > spin_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            coin_group.draw(screen)

#button aanmaken(voor restart)
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # mouse position
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

#spritegroep inspawnen
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()


flappy = Bird(100, int(height / 2))
bird_group.add(flappy)

# restart
button = Button(width // 2 - 60, height // 2 - 100, button_img)


#  Is het spel aan het draaien?
isRunning = True
isFlying = False
playdeath = True


while isRunning:
    # 60 FPS
    clock.tick(fps)
    # Tekenen achtergrond
    screen.blit(background, (0, 0))

    # Flappy op scherm flikkeren
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    
    
    #wanneer vogel e pipe elkaar raken
    if  ( pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 ) and game_over != True:
        game_over = True
        hitpipe.set_volume(1.0)
        hitpipe.play()

    #wanneer vogel en coin elkaar raken
    if pygame.sprite.groupcollide(bird_group, coin_group, False, True):
        coin_sound.play()
        score += 2
        if high_score < score:
            high_score = score
            
    
    # Scrolling achtergrond
    screen.blit(grond, (ground_scroll, 576))

    #score update wanneer door pipe
    if len(pipe_group) > 0:
        if (
            bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right
            and pass_pipe == False
        ):
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                ding.play()
                pass_pipe = False
                if high_score < score:
                    high_score = score
                  
    #score
    draw_text(str(score), font, (255, 255, 255), int(width / 2), 20)


    # check if bird has hit the ground
    if flappy.rect.bottom >= 576:
        game_over = True
        isFlying = False
        if playdeath:
            death.set_volume(0.30)
            death.play(loops=0)
            playdeath = False

    if flappy.rect.bottom < 576:
        playdeath = True

    if game_over == False and isFlying == True:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipes(width, int(height / 2) + pipe_height, -1)
            top_pipe = Pipes(width, int(height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
            coin = coins(500, random.randrange(200,500))
            coin_group.add(coin)
            
        ground_scroll -= scroll_speed

        # Reset ground
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        pipe_group.update()
        coin_group.update()
    if game_over == True:
        draw_text(str(hs), font_hs, (255, 255, 255), int(width / 2.6), 225)
        draw_text(str(high_score), font_hs,
                  (255, 255, 255), int(width / 1.65), 225)
        if button.draw() == True:
            game_over = False
            isFlying = False
            score = reset_game()
           
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and isFlying == False
            and game_over == False
        ):
            isFlying = True
        elif event.type == pygame.KEYDOWN and isFlying == False and game_over == False:
            if event.key == pygame.K_SPACE:
                isFlying = True

    pygame.display.update()

pygame.quit()