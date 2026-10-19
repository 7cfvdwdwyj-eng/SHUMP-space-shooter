import pygame
import random
import os 
import time

# ---------------------------------------------------------------------------
# Asset folders (img/ and sound/ sit next to this script)
# ---------------------------------------------------------------------------
img_dir = os.path.join(os.path.dirname(__file__), 'img')
sound_dir = os.path.join(os.path.dirname(__file__), 'sound')

# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------
WIDTH = 1080
HEIGHT = 720
FPS = 60

# Colours as (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)

# Find the system's Arial font file so we can draw text with it
font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    """Draw white text onto `surf`, horizontally centred on x with its top at y."""
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)   # True = anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# ---------------------------------------------------------------------------
# Pygame setup
# ---------------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup Space Shooter")
clock = pygame.time.Clock()
ticks = 0            # frames elapsed since launch (used for the on-screen clock)
difficulty = 0       # creeps up every frame; makes newly spawned enemies faster
pygame.mouse.set_visible(False)   # hide the OS cursor

# ---------------------------------------------------------------------------
# Load images (convert() / convert_alpha() makes drawing much faster)
# ---------------------------------------------------------------------------
background = pygame.image.load(os.path.join(img_dir, 'starfield.png')).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))   # stretch to window size
background_rect = background.get_rect()

player_img = pygame.image.load(os.path.join(img_dir, "playerShip1_red.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 48))

enemy_img = pygame.image.load(os.path.join(img_dir, "enemyBlue3.png")).convert_alpha()  
enemy_img = pygame.transform.scale(enemy_img, (50, 38))

bullet_img = pygame.image.load(os.path.join(img_dir, "laserRed16.png")).convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (10, 40))

# Small flash shown on an enemy (or player) when it takes a hit
hit_img = pygame.image.load(os.path.join(img_dir, "enemyhit.png")).convert_alpha()
hit_img = pygame.transform.scale(hit_img, (41, 41))

enemy_bullet_img = pygame.image.load(os.path.join(img_dir, "laserBlue16.png")).convert_alpha()
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (10, 40))

tank_img = pygame.image.load(os.path.join(img_dir, "enemyBlack4.png")).convert_alpha()
tank_img = pygame.transform.scale(tank_img, (75, 63))

speeder_img = pygame.image.load(os.path.join(img_dir, "enemyRed2.png")).convert_alpha()
speeder_img = pygame.transform.scale(speeder_img, (50, 38))

# HUD icons: `lives` = one icon per health point, `defence` = one icon per shield point
lives = pygame.image.load(os.path.join(img_dir, "playerLife1_red.png")).convert_alpha()
defence = pygame.image.load(os.path.join(img_dir, "shield_gold.png")).convert_alpha()
cursor = pygame.image.load(os.path.join(img_dir, "cursor.png")).convert_alpha()   # NOTE: loaded but never drawn

# Power-up pickup images
heal_img = pygame.image.load(os.path.join(img_dir, "heal.png")).convert_alpha()
heal_img = pygame.transform.scale(heal_img, (21, 21))

full_heal_img = pygame.image.load(os.path.join(img_dir, "full_heal.png")).convert_alpha()
full_heal_img = pygame.transform.scale(full_heal_img, (31, 31))

shield_img = pygame.image.load(os.path.join(img_dir, "shield_gold.png")).convert_alpha()
shield_img = pygame.transform.scale(shield_img, (26, 26))

# Number sprites used to draw the score and the clock
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

# Lookup table: digit character -> image, so str(score) can be drawn digit by digit
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

# ---------------------------------------------------------------------------
# Sounds and music
# ---------------------------------------------------------------------------
shoot_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'pew.wav'))
explosion_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    explosion_sounds.append(pygame.mixer.Sound(os.path.join(sound_dir, sound)))

for sound in explosion_sounds:
    sound.set_volume(0.05)   # quiet, so explosions don't drown everything out
pygame.mixer.music.load(os.path.join(sound_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.02)



# ---------------------------------------------------------------------------
# Sprite classes
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        # Radius for circle collision (80% of the ship width -> forgiving hitbox)
        self.radius = int(self.rect.width * .80 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)   'draws a circle'
        # Start bottom-centre of the screen
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

        self.health = 5
        # NOTE: `Shield` (capital S) is the power-up CLASS defined further down,
        # not the `shield` boolean, so this comparison is always False and the
        # player always starts with 3 shield points (they only show on the HUD
        # when the lowercase `shield` flag is True).
        if Shield == False:
            self.shield_health  = 0
        else:
            self.shield_health = 3

    def update(self):
        # Reset movement each frame, then read the keys
        self.speedx = 0
        self.speedy = 0

        # Remember last position (currently unused)
        self.lasttop = self.rect.top
        self.lastleft = self.rect.left

        # WASD movement, 8 pixels per frame
        keystate = pygame.key.get_pressed() 
        if keystate[pygame.K_a]: 
            self.speedx = -8
        if keystate[pygame.K_d]:  
            self.speedx = 8
        self.rect.x += self.speedx

        if keystate[pygame.K_w]:  
            self.speedy = -8
        if keystate[pygame.K_s]: 
            self.speedy = 8
        self.rect.y +=self.speedy
       
        # Keep the player inside the window
        if self.rect.right > WIDTH: 
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
        if self.rect.bottom > HEIGHT:  
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

        # Remove the sprite when out of health
        if self.health <= 0:  
             self.kill()
        
        # NOTE: this sets shield_health to False (== 0) rather than the int 0.
        # It works because False behaves like 0, but `= 0` would be clearer.
        if self.shield_health <= 0:
            self.shield_health = False
        
    def shoot(self):
        # Spawn a bullet at the top-centre of the ship
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)    # so it gets updated and drawn
        bullets.add(bullet)        # so we can check it against enemies
        shoot_sound.play()
        shoot_sound.set_volume(0.03) 
    
class Enemy(pygame.sprite.Sprite):
    """Base class for all enemies. Subclasses just pick the stats."""
    def __init__(self, image, speed_y, health, shoot_chance):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(BLACK)   # treat black pixels as transparent
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # Spawn at a random x, just above the top of the screen
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        # Fall speed scales up as `difficulty` increases (+~26% after 60 seconds' worth of frames)
        self.speedy = speed_y * (difficulty / 950 + 1)
        self.speedx = random.randrange(-3, 3)   # slight random sideways drift
        self.health = health
        # Each frame there's a 1-in-100 roll; the enemy fires if the roll equals this number.
        # NOTE: that means the real chance is always 1% per frame, whatever the value is
        # (as long as it's 1-100). Values above 100 (e.g. Tank's 150) NEVER fire.
        self.shoot_chance = shoot_chance

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Despawn once off the bottom or too far off either side
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.kill()
  
            # Drop a power-up when an enemy leaves the screen.
            # NOTE: every condition is `<= 100`, which is always true, so a heal ALWAYS
            # drops and the full heal / shield branches are never reached. The comments
            # suggest 10% / 5% / 2% were intended.
            if random.randint(1, 100) <= 100:  # 10% chance of spawning a heal
                self.heals()
            elif random.randint(1, 100) <= 100:  # 5% chance of spawning a full heal
                self.full_heal()
            elif random.randint(1, 100) <= 100:  # 2% chance of spawning a shield
                self.shield()
        # Random chance to fire (see note in __init__)
        if random.randint(1, 100) == self.shoot_chance:
            self.enemy_shoot()


    def enemy_shoot(self):
        enemy_bullet = Enemy_Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
        shoot_sound.play()
        shoot_sound.set_volume(0.03)

    # The three methods below spawn a power-up at the enemy's position
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


# Three enemy types: (image, fall speed, health, shoot_chance)
class Mob(Enemy):
    """Basic enemy: average speed, 1 hit to kill."""
    def __init__(self):
        super().__init__(enemy_img, 5, 1, 50)


class Speeder(Enemy):
    """Fast enemy, 2 hits to kill."""
    def __init__(self):
        super().__init__(speeder_img, 7, 2, 80)


class Tank(Enemy):
    """Slow, tough enemy, 5 hits to kill."""
    def __init__(self):
        super().__init__(tank_img, 3, 5, 150)
        
# Points awarded for killing each enemy type
enemy_types = {
    Mob: {'score': 3},
    Speeder: {'score': 8},
    Tank: {'score': 13}
}

class Bullet(pygame.sprite.Sprite):
    """Player bullet: travels straight up."""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10   # negative = upwards
        
    def update(self):
        self.rect.y += self.speedy
        
        # Remove once it leaves the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Enemy_Bullet(pygame.sprite.Sprite):
    """Enemy bullet: travels straight down."""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()

        self.rect.top = y
        self.rect.centerx = x
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy

        # NOTE: this bullet moves DOWN, so `bottom < 0` is never true and it is never
        # removed. It should probably be `self.rect.top > HEIGHT`.
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    """Base class for pickups: drift slowly downwards."""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.speedy = 1

    def update(self):
        self.rect.y += self.speedy
        # NOTE: same issue as Enemy_Bullet - these fall down, so this never triggers
        # and pickups pile up off-screen forever.
        if self.rect.bottom < 0:
            self.kill()

class Heal(PowerUp):
    def __init__(self, x, y):
        super().__init__(heal_img, x, y)
        # NOTE: this heals the player the moment the pickup is CREATED, not when it's
        # collected (collection also heals - see handle_other_collisions).
        if player.health < 5:    
            player.health += 1

class Full_Heal(PowerUp):
    def __init__(self, x, y):
        super().__init__(full_heal_img, x, y)
        # NOTE: likewise, this fully heals on creation rather than on pickup.
        player.health = 5 

class Shield(PowerUp):
    def __init__(self, x, y):
        super().__init__(shield_img, x, y)
            
class Hit(pygame.sprite.Sprite):
    """Short-lived hit flash drawn over whatever was hit."""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = hit_img
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.health = 5          # acts as a lifetime counter (frames)
        self.shield_health = 3   # NOTE: counted down but never used

    def update(self):
        # Disappears after 5 frames
        self.health -= 1
        if self.health == 0:
            self.kill()
        self.shield_health -= 1

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def spawn_enemy(enemy):
    """Add an enemy to the sprite groups so it's updated, drawn and collidable."""
    all_sprites.add(enemy)
    mobs.add(enemy)
    # NOTE: every enemy (including Tanks and Speeders) goes into `mobs`; the `tank`
    # and `speeder` groups created in reset_game_state() are never filled.

def saveScore(score):
    """Append the score to scores.txt (only if it's above 0)."""
    with open("scores.txt", "a") as scores:
        if score > 0:
            scores.write(str(score))
            scores.write("\n")

def loadScore():
    """Read every saved score and return them as a list, highest first."""
    # NOTE: this crashes with FileNotFoundError if scores.txt doesn't exist yet.
    # saveScore() normally creates it first, since "a" mode creates the file.
    scores = []
    with open("scores.txt", "r") as files:
        for score in files.readlines():
            scores.append(int(score.rstrip()))   # strip the newline, convert to int
    scores.sort(reverse=True)
    return scores

screen = pygame.display.set_mode((WIDTH, HEIGHT))   # NOTE: duplicate of the earlier set_mode call

def show_game_over_screen(score):
    """Title / game over screen. Saves the score, shows the top 5, waits for a key."""
    saveScore(score)
    scores = loadScore()

    screen.blit(background, background_rect)

    # Title and instructions
    draw_text(screen, "SHUMP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "W, A, S and D to move, Left click to shoot", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 4 / 5)
    draw_text(screen, "Avoid being hit, 5 bullets then you lose", 18, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text(screen, "High scores:", 32, WIDTH / 1.125, HEIGHT / 4)

    # List the top 5 scores down the right-hand side
    if scores:
        for i, score in enumerate(scores[:5], start=1):
            draw_text(screen, f"{score}", 28, WIDTH / 1.125, HEIGHT / 4 + i * 40)
    else:
        draw_text(screen, "No high scores yet", 28, WIDTH / 1.125, HEIGHT / 16 * 5)

    pygame.display.flip()
    pygame.time.wait(2000)   # brief pause so you don't skip it by accident

    # Wait here until a key is released (or the window is closed)
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()   # NOTE: doesn't exit the loop, so the program may error afterwards
            if event.type == pygame.KEYUP:
                waiting = False
    
# ---------------------------------------------------------------------------
# Initial game state (reset_game_state() rebuilds all of this on each new game)
# ---------------------------------------------------------------------------
all_sprites = pygame.sprite.Group()   # everything that gets updated and drawn
player = Player()

all_sprites.add(player)

mobs = pygame.sprite.Group()          # all enemies
for i in range(8):                    # start with 8 enemies on screen
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

bullets = pygame.sprite.Group()        # player bullets
enemy_bullets = pygame.sprite.Group()  # enemy bullets
heals = pygame.sprite.Group()          # heal pickups

score = 0
pygame.mixer.music.play(loops=-1)      # loop the background music forever
shield = False                         # True while the player has an active shield

def reset_game_state():
    """Throw everything away and start a fresh game."""
    # NOTE: `time` here shadows the `time` module imported at the top (unused anyway),
    # and `font` / `frame_count` are set but never used.
    global all_sprites, mobs, bullets, player, tank, speeder, enemy_bullets, heals, full_heals, shields, hit, score, time, font, frame_count
    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    tank = pygame.sprite.Group()
    speeder = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    heals = pygame.sprite.Group()
    full_heals = pygame.sprite.Group()
    shields = pygame.sprite.Group()
    hit = pygame.sprite.Group()
    score = 0
    time = 0
    font = pygame.font.Font(None, 25)
    frame_count = 0

def spawn_enemies():
    """Called every frame; randomly spawns at most one new enemy."""
    spawn_chance = 300
    if random.randint(1, spawn_chance) == spawn_chance:          # 1/300 per frame -> Tank
        spawn_enemy(Tank())
    elif random.randint(1, spawn_chance // 3) == 1:              # 1/100 per frame -> Speeder
        spawn_enemy(Speeder())
    elif random.randint(1, spawn_chance // 2) == 1:              # 1/150 per frame -> Mob
        spawn_enemy(Mob())

def handle_player_shooting():
    """Fire once per left-click (holding the button doesn't auto-fire)."""
    global prevMB1
    if pygame.mouse.get_pressed()[0] and not prevMB1:   # button down now, but wasn't last frame
        player.shoot()
    prevMB1 = pygame.mouse.get_pressed()[0]             # remember for next frame

def handle_collisions():
    handle_player_collisions()
    handle_enemy_collisions()
    handle_other_collisions()

def handle_player_collisions():
    """Player touching an enemy: lose the shield if you have one, otherwise it's game over."""
    global game_over, shield
    # True = the enemy is destroyed on contact. collide_circle uses each sprite's .radius.
    # NOTE: Group(mobs, tank, speeder) builds a new group every frame; tank/speeder are empty.
    player_hit = pygame.sprite.spritecollide(player, pygame.sprite.Group(mobs, tank, speeder), True, pygame.sprite.collide_circle)
    if player_hit:
        if shield:
            shield = False
        else:
            game_over = True

def handle_enemy_collisions():
    """Player bullets hitting enemies: damage them, flash, and award score on a kill."""
    global score
    for enemy_group in [mobs, tank, speeder]:
        for enemy in enemy_group:
            enemy_class = type(enemy)
            if enemy_class in enemy_types:   # safety check that it's a known enemy type
                # False = don't auto-kill the enemy; we apply damage ourselves
                hits = pygame.sprite.spritecollide(enemy, bullets, False)
                for bullet in hits:
                    all_sprites.add(Hit(enemy.rect.x, enemy.rect.y))   # hit flash
                    bullet_damage = 1 
                    enemy.health -= bullet_damage
                    bullet.kill()   # bullet is used up
                    if enemy.health <= 0:
                        enemy.kill()
                        score += enemy_types[type(enemy)]['score']
            
def handle_other_collisions():
    """Pickups (heal / full heal / shield)."""
    global shield
    heal = pygame.sprite.spritecollide(player, heals, True, pygame.sprite.collide_circle)
    if heal:
        player.health = min(player.health + 1, 5)    # +1 health, capped at 5
    full_heal = pygame.sprite.spritecollide(player, full_heals, True, pygame.sprite.collide_circle)
    if full_heal:
        player.health = 5
    shield_hit = pygame.sprite.spritecollide(player, shields, True, pygame.sprite.collide_circle)
    if shield_hit:
        shield = True
        player.shield_health = 3
    # Enemy bullet damage is currently disabled (commented out below), so enemy
    # bullets are harmless; only touching an enemy hurts you.
    '''bullet_hit = pygame.sprite.spritecollide(player, enemy_bullets, True, False)
    if bullet_hit:
        if shield:
            player.shield_health -= 1
            if player.shield_health <= 0:
                shield = False
        else:
            player.health -= 1
            all_sprites.add(Hit(player.rect.x, player.rect.y))
            random.choice(explosion_sounds).play()'''

# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
def draw_screen():
    """Draw one full frame. Order matters: later things are drawn on top."""
    screen.blit(background, background_rect)
    draw_player_health()
    draw_shield_health()
    all_sprites.draw(screen)
    draw_score()
    draw_clock()
    pygame.display.flip()   # push the finished frame to the display

def draw_player_health():
    """One life icon per health point, top-left."""
    for i in range(player.health):
        screen.blit(lives, (i * 40, 5))

def draw_shield_health():
    """One shield icon per shield point, under the lives. Only while shielded."""
    global shield  
    if shield:
        for i in range(player.shield_health):
            screen.blit(defence, (i * 40, 35))

def draw_score():
    """Draw the score top-centre using the numeral images (30px per digit)."""
    score_str = str(score)
    text_width = len(score_str) * 30
    x_pos = (WIDTH - text_width) // 2   # centre the whole number
    for i, digit in enumerate(score_str):
        screen.blit(numberImgs[digit], (x_pos + i * 30, 10)) 


def draw_clock():
    """Draw the elapsed seconds top-right, padded to 3 digits."""
    # NOTE: `ticks` counts since the program started, not since this game started,
    # and `% 60` wraps it back to 0 every minute (so it only shows seconds, 0-59).
    elapsed_time = ticks // FPS
    seconds = str(elapsed_time % 60)

    # Zero-pad to 3 digits (e.g. "7" -> "007").
    # NOTE: a 1-digit value becomes 2 digits and then hits the second check, giving 3.
    # A 2-digit value skips the first check and gets padded by the second.
    if len(seconds) < 3:
        seconds = '0' + seconds
    if len(seconds) == 2:
        seconds = '0' + seconds

    for i in range(len(seconds)):
        screen.blit(numberImgs[seconds[i]], (960 + i * 30, 10))

# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------
game_over = True    # start on the title screen
running = True
prevMB1 = False     # was the left mouse button down last frame?

while running:
    clock.tick(FPS)         # cap the frame rate at 60 FPS
    ticks += 1
    difficulty += 0.25      # enemies spawned later fall faster

    # Show the title/game over screen, then start a fresh game
    if game_over:
        show_game_over_screen(score)
        reset_game_state()
        game_over = False

    # Handle window close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False     
            
    spawn_enemies()             # maybe add a new enemy

    handle_player_shooting()    # fire on click

    handle_collisions()         # bullets, pickups, enemy contact

    all_sprites.update()        # move everything

    draw_screen()               # render the frame

pygame.quit()