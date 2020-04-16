import os
import sys
import random
import pygame

#initializes game
pygame.font.init()

# size of window
WIDTH, HEIGHT = 800, 650

#window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Battle the UFOs')

# load images
# our player
SHIP = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'main_ship.png')),
                            (50, 50))

# load enemies
ENEMY1 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'enemy1.png')),
                                (70, 50))
ENEMY2 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'enemy2.png')),
                                (70, 50))

# load own laser                               
LASER = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'myLaser.png')),
                                (25, 30))
# load enemy bullets                            
ENEMY_LASER = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'enemyLaser.png')), 
                                    (25, 30))

# load background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background.jpg')),
                             (WIDTH, HEIGHT))



class Laser:

    ''' bullets which are used by player and enemies '''

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):
        self.y += speed

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class SpaceShip:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.pres_image = None
        self.gun_image = None
        self.bullet_image = None
        self.lasers = []
        self.cool_down = 0               #so enemies can not constantly shoot

    def cooldown(self):
        ''' not possible to shoot without break '''
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    def move_lasers(self, speed, obj):
        ''' let bullets move '''
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def draw(self, window):
        window.blit(self.pres_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def get_width(self):
        return self.pres_image.get_width()

    def get_height(self):
        return self.pres_image.get_height()

class Player(SpaceShip):

    ''' character played by player '''

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.pres_image = None
        self.gun_image = SHIP
        self.bullet_image = LASER
        self.mask = pygame.mask.from_surface(self.gun_image)
        self.max_health = health

    def draw(self, window):
        #pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50))
        window.blit(self.gun_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
        self.healthbar(window)

    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x, self.y, self.bullet_image)
            self.lasers.append(laser)
            self.cool_down = 1

    def move_lasers(self, speed, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for ob in obj:
                    if laser.collision(ob):
                        obj.remove(ob)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.gun_image.get_height()+10,
                            self.gun_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.gun_image.get_height()+10,
                            self.gun_image.get_width() * (self.health/self.max_health), 10))

class Enemy(SpaceShip):

    ''' object of enemy '''

    ENEMY_MAP = {
                'enemy1': (ENEMY1, ENEMY_LASER),
                'enemy2': (ENEMY2, ENEMY_LASER)
    }
    def __init__(self, x, y, enemy, health=100):
        super().__init__(x, y, health)
        #self.pres_image = ENEMY
        self.pres_image, self.bullet_image = self.ENEMY_MAP[enemy]
        self.mask = pygame.mask.from_surface(self.pres_image)

    def move(self, speed):
        self.y += speed

    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x-20, self.y, self.bullet_image)
            self.lasers.append(laser)
            self.cool_down = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



def main():

    ''' main loop of game '''

    run = True
    FPS = 100
    clock = pygame.time.Clock()

    level = 1
    lives = 5

    main_font = pygame.font.SysFont('comicsans', 50)

    # create player
    player = Player(250, 400)
    player_speed = 5

    # speed of bullet
    bullet_speed = 2             # adjust to shoot slower/faster

    #create enemy
    enemies = []
    wave_length = 5
    enemy_speed = 1               # adjust if enemies should be slower/faster

    # game flow    #enemy = Enemy(250, 10)
    lost = False
    lost_count = 0


    def draw_window():
        ''' draws all game elements '''

        #draw background
        WIN.blit(BG, (0, 0))

        # what is written on screen;; level/lives and lost
        main_font = pygame.font.SysFont('comicsans', 50)
        lost_font = pygame.font.SysFont('comicsans', 40)

        #draw lives and level
        lives_label = main_font.render(f'Lives: {lives}', 1, (186, 22, 219))
        level_label = main_font.render(f'Level: {level}', 1, (136, 5, 162))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # draw player
        player.draw(WIN)

        #draw enemy
        for enemy in enemies:
            enemy.draw(WIN)

        #shown when game is lost
        if lost:
            lost_label = lost_font.render('Oh no, you lost..!', 1, 
                                            (255, 0, 0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    # actual game run
    while run:
        clock.tick(FPS)
        draw_window()

        # counts remaining lives and stops
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        # stops if lost
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # create enemies from Enemy
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100),
                                random.choice(['enemy1', 'enemy2']))
                enemies.append(enemy)


        # windows can be exited, program will closed after
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


        # control our player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:                #left, 'a'
            player.x -= player_speed
        if keys[pygame.K_d]:                #right, 'd'
            player.x += player_speed
        if keys[pygame.K_w]:
            player.y -= player_speed       #up, 'w'
        if keys[pygame.K_s]:                #down, 's'
            player.y += player_speed
        if keys[pygame.K_SPACE]:            #shoot, space
            player.shoot()

        #define habit of our enemies
        for enemy in enemies[:]:
            enemy.move(enemy_speed)
            enemy.move_lasers(bullet_speed, player)

            if random.randrange(0, 2*50) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # let bullets move
        player.move_lasers(-bullet_speed, enemies)


def start_window():

    ''' welcoming window and where main() runs'''

    title_font = pygame.font.SysFont('comicsans', 30)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render('Welcome to this game! Press mouse if you are ready!',
                                         1, (65, 85, 55))
        WIN.blit(title_label, (100, 100))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == '__main__':

    start_window()