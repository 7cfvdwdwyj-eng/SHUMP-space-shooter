# credit:
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nlFPS

import pygame
import random
import os 
from os import path
import time

img_dir = os.path.join(os.path.dirname(__file__), 'img')
sound_dir = os.path.join(os.path.dirname(__file__), 'sound')

WIDTH = 1080
HEIGHT = 720
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# initialize pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup Space Shooter")
clock = pygame.time.Clock()
ticks = 0
difficulty = 0
pygame.mouse.set_visible(False)

# game images
background = pygame.image.load(os.path.join(img_dir, 'starfield.png')).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()

player_img = pygame.image.load(os.path.join(img_dir, "playerShip1_red.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 48))

enemy_img = pygame.image.load(os.path.join(img_dir, "enemyBlue3.png")).convert_alpha()  
enemy_img = pygame.transform.scale(enemy_img, (50, 38))

bullet_img = pygame.image.load(os.path.join(img_dir, "laserRed16.png")).convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (10, 40))

hit_img = pygame.image.load(os.path.join(img_dir, "enemyhit.png")).convert_alpha()
hit_img = pygame.transform.scale(hit_img, (41, 41))

enemy_bullet_img = pygame.image.load(os.path.join(img_dir, "laserBlue16.png")).convert_alpha()
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (10, 40))

tank_img = pygame.image.load(os.path.join(img_dir, "enemyBlack4.png")).convert_alpha()
tank_img = pygame.transform.scale(tank_img, (75, 63))

speeder_img = pygame.image.load(os.path.join(img_dir, "enemyRed2.png")).convert_alpha()
speeder_img = pygame.transform.scale(speeder_img, (50, 38))

lives = pygame.image.load(os.path.join(img_dir, "playerLife1_red.png")).convert_alpha()
defence = pygame.image.load(os.path.join(img_dir, "shield_gold.png")).convert_alpha()
cursor = pygame.image.load(os.path.join(img_dir, "cursor.png")).convert_alpha()

# power up images
heal_img = pygame.image.load(os.path.join(img_dir, "heal.png")).convert_alpha()
heal_img = pygame.transform.scale(heal_img, (21, 21))

full_heal_img = pygame.image.load(os.path.join(img_dir, "full_heal.png")).convert_alpha()
full_heal_img = pygame.transform.scale(full_heal_img, (31, 31))

shield_img = pygame.image.load(os.path.join(img_dir, "shield_gold.png")).convert_alpha()
shield_img = pygame.transform.scale(shield_img, (26, 26))

# number images 
img1 = pygame.image.load(os.path.join(img_dir, "numeral1.png")).convert_alpha()
img2 = pygame.image.load(os.path.join(img_dir, "numeral2.png")).convert_alpha()
img3 = pygame.image.load(os.path.join(img_dir, "numeral3.png")).convert_alpha()
img4 = pygame.image.load(os.path.join(img_dir, "numeral4.png")).convert_alpha()
img5 = pygame.image.load(os.path.join(img_dir, "numeral5.png")).convert_alpha()
img6 = pygame.image.load(os.path.join(img_dir, "numeral6.png")).convert_alpha()
img7 = pygame.image.load(os.path.join(img_dir, "numeral7.png")).convert_alpha()
img8 = pygame.image.load(os.path.join(img_dir, "numeral8.png")).convert_alpha()
img9 = pygame.image.load(os.path.join(img_dir, "numeral9.png")).convert_alpha()
img0 = pygame.image.load(os.path.join(img_dir, "numeral0.png")).convert_alpha()

numberImgs = {
    "0": img0,
    "1": img1,
    "2": img2,
    "3": img3,
    "4": img4,
    "5": img5,
    "6": img6,
    "7": img7,
    "8": img8,
    "9": img9
}


# game sounds
shoot_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'pew.wav'))
explosion_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    explosion_sounds.append(pygame.mixer.Sound(os.path.join(sound_dir, sound)))

for sound in explosion_sounds:
    sound.set_volume(0.05)
pygame.mixer.music.load(os.path.join(sound_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.02)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .80 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)   'draws a circle'
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

        self.health = 5
        if Shield == False:
            self.shield_health  = 0
        else:
            self.shield_health = 3

    def update(self):
        self.speedx = 0
        self.speedy = 0

        self.lasttop = self.rect.top
        self.lastleft = self.rect.left

        keystate = pygame.key.get_pressed() # get a keypress events from pygame
        if keystate[pygame.K_a]: # if the key 'a' gets pressed the player will move to the left a speed of 8
            self.speedx = -8
        if keystate[pygame.K_d]:  # if the key 'd' gets pressed the player will move to the right a speed of 8
            self.speedx = 8
        self.rect.x += self.speedx

        if keystate[pygame.K_w]:  # if the key 'w' gets pressed the player will move forward a speed of 8
            self.speedy = -8
        if keystate[pygame.K_s]: # if the key 's' gets pressed the player will move backwards a speed of 8
            self.speedy = 8
        self.rect.y +=self.speedy
       
        if self.rect.right > WIDTH: # this will stop the player from going of the edge of the screen
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
        if self.rect.bottom > HEIGHT:  # this will stop the player from going of the edge of the screen
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

        if self.health <= 0:  # the players health drops below 0 the player will be killed and the game will stop
             self.kill()
        
        if self.shield_health <= 0:
            self.shield_health = False
        
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()
        shoot_sound.set_volume(0.03) 
    
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, speed_y, health, shoot_chance):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = speed_y * (difficulty / 950 + 1)
        self.speedx = random.randrange(-3, 3)
        self.health = health
        self.shoot_chance = shoot_chance

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.kill()
  
        if self.health <= 0:
            self.kill()
            if random.randint(1, 50) == 50:
                self.heals()
            elif random.randint(1, 150) == 49:
                self.full_heal()
            elif random.randint(1, 100) == 2:
                self.shield()
        if random.randint(1, 100) == self.shoot_chance:
            self.enemy_shoot()

    def enemy_shoot(self):
        enemy_bullet = Enemy_Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
        shoot_sound.play()
        shoot_sound.set_volume(0.03)

    def heals(self):
        heal = Heal(self.rect.centerx, self.rect.top)
        all_sprites.add(heal)
        heals.add(heal)

    def full_heal(self):
        full_heal = Full_Heal(self.rect.centerx, self.rect.top)
        all_sprites.add(full_heal)
        full_heals.add(full_heal)

    def shield(self):
        shield = Shield(self.rect.centerx, self.rect.top)
        all_sprites.add(shield)
        shields.add(shield)


class Mob(Enemy):
    def __init__(self):
        super().__init__(enemy_img, 5, 1, 50)


class Speeder(Enemy):
    def __init__(self):
        super().__init__(speeder_img, 7, 2, 80)


class Tank(Enemy):
    def __init__(self):
        super().__init__(tank_img, 3, 5, 150)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()

        self.rect.top = y
        self.rect.centerx = x
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy

        # kill if moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Heal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = heal_img
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.speedy = 1

    def update(self):
        self.rect.y += self.speedy
        # remove if it is off the screen
        if self.rect.bottom < 0:
            self.kill()

class Full_Heal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = full_heal_img
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.speedy = 1
    
    def update(self):
        self.rect.y += self.speedy
        # remove if it is off the screen
        if self.rect.bottom < 0:
            self.kill()

class Hit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = hit_img
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.health = 5
        self.shield_health = 3

    def update(self):
        self.health -= 1
        if self.health == 0:
            self.kill()
        self.shield_health -= 1
        
class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = shield_img
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.speedy = 1

    def update(self):
        self.rect.y += self.speedy
        # remove if it is off the screen
        if self.rect.bottom < 0:
            self.kill()  

def saveScore(score):
    with open("scores.txt", "a") as scores:
        if score > 0:
            scores.write(str(score))
            scores.write("\n")

def loadScore():
    scores = []
    with open("scores.txt", "r") as files:
        for score in files.readlines():
            scores.append(int(score.rstrip()))
    scores.sort(reverse=True)
    return scores

screen = pygame.display.set_mode((WIDTH, HEIGHT))

def show_game_over_screen():
    saveScore(score)
    scores = loadScore()
    screen.blit(background, background_rect)
    draw_text(screen, "SHUMP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "W, A, S and D to move, Left click to shoot", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 4 / 5)
    draw_text(screen, "Avoid being hit, 5 bullets then you lose", 18, WIDTH / 2, HEIGHT * 3 / 4 )
    draw_text(screen, "High scores:", 32, WIDTH / 1.125, HEIGHT / 4)
    if scores:
        draw_text(screen, f" {scores[0]}", 28, WIDTH / 1.125, HEIGHT / 16 * 5)
        draw_text(screen, f" {scores[1]}", 28, WIDTH / 1.125, HEIGHT / 14 * 5)
        draw_text(screen, f" {scores[2]}", 28, WIDTH / 1.125, HEIGHT / 12 * 5)
        draw_text(screen, f" {scores[3]}", 28, WIDTH / 1.125, HEIGHT / 10.5 * 5)
        draw_text(screen, f" {scores[4]}", 28, WIDTH / 1.125, HEIGHT / 9.5 * 5)
    else:
        draw_text(screen, "No high scores yet", 28, WIDTH / 1.125, HEIGHT / 16 * 5)

    
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
            
      
all_sprites = pygame.sprite.Group()
player = Player()

all_sprites.add(player)

#create new sprite group for enemies
mobs = pygame.sprite.Group()
for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
heals = pygame.sprite.Group()

score = 0
pygame.mixer.music.play(loops=-1)

# Game loop
game_over = True
running = True

while running:
    ticks += 1
    difficulty += 0.25
    if game_over:
        show_game_over_screen()
        game_over = False
        shield = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)    
        tank = pygame.sprite.Group()
        speeder = pygame.sprite.Group()
        enemy_bullet = pygame.sprite.Group()
        heals = pygame.sprite.Group()
        full_heals = pygame.sprite.Group()
        shields = pygame.sprite.Group()
        hit = pygame.sprite.Group()
   
        score = 0
        time = 0
        
        font = pygame.font.Font(None, 25)
        frame_count = 0
  
    # keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    #clock.tick(60)
    mouseState = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    if random.randint(1, 300) == 300:
        t = Tank()
        all_sprites.add(t)
        tank.add(t)

    if random.randint(1, 90) == 1:
        s = Speeder()
        all_sprites.add(s)
        speeder.add(s)
    
    if random.randint(1, 60) == 1:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
    
    if player.health <= 0:
        game_over = True

    # stop auto fire and allows shooting 
    if mouseState[0]:
        if prevMB1 == False:
            player.shoot()
        prevMB1 = True
    else:
        prevMB1 = False

    # Update
    all_sprites.update()
    
    # check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    if hits:
        if shield == False:
            game_over = True
        
        if shield == True:
            shield = False
        
        # check to see if a tank hit the player
    hits = pygame.sprite.spritecollide(player, tank, True, pygame.sprite.collide_circle)
    if hits:
        if shield == False:
            game_over = True
        
        if shield == True:
            shield = False
            
    hits = pygame.sprite.spritecollide(player, speeder, True, pygame.sprite.collide_circle)
    if hits:
        if shield == False:
            game_over = True
        
        if shield == True:  
            shield = False
            
    # check to see if heal hit player
    heal = pygame.sprite.spritecollide(player, heals, True, pygame.sprite.collide_circle)
    if heal:
        player.health += 1
        if player.health > 5:
            player.health = 5

     # check to see if full heal hit player
    full_heal = pygame.sprite.spritecollide(player, full_heals, True, pygame.sprite.collide_circle)
    if full_heal:
        player.health = 5
        
    hits = pygame.sprite.spritecollide(player, shields, True, pygame.sprite.collide_circle)
    if hits:
        shield = True
        player.shield_health = 3

    pygame.sprite.groupcollide(bullets, enemy_bullets, True, True)
    
    # check to see if a bullet hit a player
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True, False)
    if hits:
        if shield == False:
            player.health -= 1
        
        if shield == True:
            player.shield_health -= 1
            
            if player.shield_health <= 0:
                shield = False
        all_sprites.add(Hit(player.rect.x, player.rect.y))
        random.choice(explosion_sounds).play()

    hits = pygame.sprite.groupcollide(bullets, tank, False, False)
    for enemy in hits:
        
        all_sprites.add(Hit(enemy.rect.x, enemy.rect.y))

    hits = pygame.sprite.groupcollide(bullets, speeder, False, False)
    for enemy in hits:
        all_sprites.add(Hit(enemy.rect.x, enemy.rect.y))
        


    # check to see if a bullet hit a tank
    hits = pygame.sprite.groupcollide(tank, bullets, False, True)
    for enemy in hits:
        enemy.health -= 1
       
        if enemy.health <= 0:
            score += 18
            random.choice(explosion_sounds).play()

    hits = pygame.sprite.groupcollide(mobs, bullets, False, True)
    for enemy in hits:
        enemy.health -= 1
       
        if enemy.health == 0:
            score += 3
            random.choice(explosion_sounds).play()

    # check to see if a bullet hit a speeder
    hits = pygame.sprite.groupcollide(speeder, bullets, False, True)
    for enemy in hits:
        enemy.health -= 1
    
        if enemy.health <= 0:
            score += 5
            random.choice(explosion_sounds).play()

    # Draw / render

    screen.blit(background, background_rect)
    
    # displays your health
    if player.health >= 5:
        screen.blit(lives, (160, 5))
    
    if player.health >= 4:
        
        screen.blit(lives, (120, 5))
        
    if player.health >= 3:
        screen.blit(lives, (80, 5))
        
    if player.health >= 2:
        screen.blit(lives, (40, 5))
       
    if player.health >= 1:
        screen.blit(lives, (0, 5))
      
    # if you the shield buff this will display how much of that shield is left  
    if shield == True:    
        if player.shield_health >= 3:
            screen.blit(defence, (80, 35))
        
        if player.shield_health >= 2:
            screen.blit(defence, (40, 35))
       
        if player.shield_health >= 1:
            screen.blit(defence, (0, 35))

    all_sprites.draw(screen)    
    
    # this will print your current score to the middle of the screen no matter the score
    Score = str(score)
    if Score == 0:
        screen.bilt("0", (WIDTH / 2, 12))
    else:
        text_width = len(str(Score)) * 30
        x_pos = (WIDTH - text_width) / 2
        for i in range(len(str(Score))):
            screen.blit(numberImgs[str(Score)[i]], (x_pos + i * 30, 12))
    
    if game_over == True:  # sets the game difficulty back to zero when you start the game
        difficulty = 0
    # clock
    if game_over == True:
        ticks = 0
    elapsed_time = ticks // FPS
    # Calculate the number of seconds that have elapsed
    seconds = str(elapsed_time % 60)
    for i in range(len(seconds)):
        screen.blit(numberImgs[seconds[i]], (960 + i * 30, 10))
    
    pygame.display.flip()

pygame.quit()