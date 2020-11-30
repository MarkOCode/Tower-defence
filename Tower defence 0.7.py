# setup
import pygame
from pygame import gfxdraw
import time
#import random
import math
from spritesheet import SpriteSheet

pygame.init()


####################################################################################
########################## object and class setup ##################################

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, health, value, path_segment, steps, dx, dy):
        super().__init__()

        self.speed = speed
        self.health = health
        self.value = value
        self.path_segment = path_segment
        self.steps = steps
        self.dx = dx
        self.dy = dy
        # set icon and icon detection rectangle
        self.image = self._load_sprites()
        self.image = pygame.transform.scale(self.image, (22, 30))
        self.rect = self.image.get_rect()
        # self.rect = self.rect.inflate(-20,-20)

    def _load_sprites(self):
        filename = "chess_symbols_trans.png"
        sprites = SpriteSheet(filename)

        # cut sprites from spritesheet
        b_king = sprites.image_at((68, 70, 85, 85))
        w_king = sprites.image_at((68, 212, 85, 85))
        b_queen = sprites.image_at((230, 70, 85, 85))
        w_queen = sprites.image_at((230, 212, 85, 85))
        b_rook = sprites.image_at((405, 70, 85, 85))
        w_rook = sprites.image_at((405, 212, 85, 85))
        b_bishop = sprites.image_at((560, 70, 85, 85))
        w_bishop = sprites.image_at((560, 212, 85, 85))
        b_knight = sprites.image_at((740, 70, 85, 85))
        w_knight = sprites.image_at((740, 212, 85, 85))
        b_pawn = sprites.image_at((921, 81, 56, 75))
        w_pawn = sprites.image_at((921, 224, 56, 75))
        return w_pawn

    def update(self):
        global money

        # movement
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        self.steps -= 1

        # check if reached end of segment, if so, set new direction
        if self.steps <= 0:
            global path
            if self.path_segment == len(path):  # if enemy at end of path
                self.kill()
                money -= 500
            else:
                segment = path[self.path_segment]
                dist = distance((self.rect.centerx, self.rect.centery), segment)
                self.dx = (segment[0] - self.rect.centerx) / dist * self.speed
                self.dy = (segment[1] - self.rect.centery) / dist * self.speed
                self.steps = round(dist / self.speed)
                self.path_segment += 1

        # wrap at end of screen / keep on screen vertically
        if self.rect.centerx >= screen_width:
            self.rect.centerx = 0
        if self.rect.y >= screen_height:
            self.rect.y -= 10
        if self.rect.y <= 0:
            self.rect.y += 10

        # hit detection
        shot_hit_list = pygame.sprite.spritecollide(self, shotList, True)
        for item in shot_hit_list:
            self.health -= item.power

            if self.health <= 0:
                self.kill()
                money += self.value
            return money


class Base(pygame.sprite.Sprite):
    def __init__(self, filled):
        super().__init__()

        self.filled = filled
        self.image = baseIMG
        self.rect = self.image.get_rect()
        # set icon and icon detection rectangle

    def update(self):
        pass


class Tower(pygame.sprite.Sprite):
    def __init__(self, shot_speed, shot_power, shot_range, level, counter):
        super().__init__()

        self.shot_speed = shot_speed
        self.shot_power = shot_power
        self.shot_range = shot_range
        self.level = level
        self.counter = counter

        # set icon and icon detection rectangle
        self.image = archerIMG[self.level].convert()
        self.image.set_colorkey(white)
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()

    def update(self):
        shoot = False
        if self.counter >= 10:
            shoot = True
        self.counter += 1
        if shoot == True:

            ## find a target
            for item in enemyList:
                x_var = (item.rect.centerx - self.rect.centerx)
                y_var = (item.rect.centery - self.rect.centery)
                distance = math.sqrt(pow(x_var, 2) + pow(y_var, 2))
                if distance < self.shot_range and self.counter >= 10:
                    x_var = x_var / distance
                    y_var = y_var / distance
                    shot = Shot(x_var, y_var, self.shot_speed, self.shot_power, self.shot_range)
                    shot.rect.center = self.rect.center
                    angle = math.atan2(shot.deltax, shot.deltay)
                    #### attempt to rotate tower - needs fixing   self.image = pygame.transform.rotate(self.image, angle*180/3.14 - 90)

                    # check angle maths            print(shot.deltax, shot.deltay, angle)
                    # shot.image = pygame.transform.rotate(arrowIMG, angle*180/3.14 - 90)
                    shotList.add(shot)
                    all_sprites_list.add(shot)

                    # reset counter
                    self.counter = 0
                    continue

    def upgrade(self, money, upgrade_cost):
        if money >= upgrade_cost and self.level <= 2:
            money -= upgrade_cost
            self.level += 1
            self.shot_speed += 10  # upgrade adds 10 to shot speed
            self.shot_power += 2  # upgrade adds 2 to shot power
            upgrade_cost *= 2  # double the cost each upgrade
            self.image = archerIMG[self.level].convert()
            self.image.set_colorkey(white)
            self.image = pygame.transform.scale(self.image, (40, 40))
        return money


class Shot(pygame.sprite.Sprite):
    def __init__(self, deltax, deltay, speed, power, srange):
        super().__init__()

        # set icon and icon detection rectangle
        # self.image = arrowIMG.convert()
        # self.image.set_colorkey(white)
        # self.image = pygame.transform.scale(self.image,(50,50))
        self.image = pygame.Surface([5, 5])
        self.image.fill(black)
        self.rect = self.image.get_rect()

        # set other parameters
        self.deltax = deltax
        self.deltay = deltay
        self.speed = speed
        self.power = power
        self.srange = srange

    def update(self):
        self.rect.centerx += int(self.deltax * self.speed)
        self.rect.centery += int(self.deltay * self.speed)
        self.srange -= self.speed
        if self.srange < 0:
            self.kill()


#####################################################################################
######################################## functions ###################################


class Point(pygame.sprite.Sprite):  # class to allow x/y to be used with pygame sprite detector
    def __init__(self, x, y):
        super(pygame.sprite.Sprite, self).__init__()
        self.rect = pygame.Rect(x, y, 1, 1)


def enemy_create(x, y):
    enemy = Enemy(5, 100, 100, 1, 0, 0, 0)  # speed, health, value, path_segment(1), steps, dx, dy)
    enemy.rect.centerx = x
    enemy.rect.centery = y
    all_sprites_list.add(enemy)
    enemyList.add(enemy)


def your_score(score):
    value = score_font.render("Your score: " + str(score), True, yellow)
    # upg_value = score_font.render("Upgrade costs: " + str(upgrade_cost), True, blue)
    screen.blit(value, [0, 0])
    # screen.blit (upg_value, [100,0]


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [int(screen_width / 2 - len(msg) * 5), int(screen_height / 2)])
    pygame.display.update()


def spacing(object1, object2):
    return math.sqrt(((object1.rect.x - object2.rect.x) ** 2) + ((object1.rect.y - object2.rect.y) ** 2))


def distance(coord1, coord2):
    return math.sqrt(((coord1[0] - coord2[0]) ** 2) + ((coord1[1] - coord2[1]) ** 2))


def tower_place(x, y, base):
    archer = Tower(20, 20, 300, 0, 0)  # shot speed, power, range, level, counter
    archer.rect.centerx = x
    archer.rect.centery = y
    towerList.add(archer)
    all_sprites_list.add(archer)
    base.kill()


def base_place(base_list):
    for i in base_list:
        spot = Base(False)  # filled
        spot.rect.centerx = i[0]
        spot.rect.centery = i[1]
        baseList.add(spot)
        all_sprites_list.add(spot)


# makes mouse detection array 2x2 pixels
def mouse_array(mouse_list):
    mouse_list.append((mouse_list[0][0] , mouse_list[0][1]))
    mouse_list.append((mouse_list[0][0], mouse_list[0][1] ))
    mouse_list.append((mouse_list[0][0] , mouse_list[0][1] ))
    return mouse_list


#######################################################################################
############################### game loop ############################################

# game loop
def gameLoop():
    game_over = False
    game_close = False
    global money
    money = 0
    upgrade_cost = 40
    tower_cost = 40
    screen.blit(backgroundIMG, (0, 0))
    base_place(tower_base)
    baseList.draw(screen)
    message("Place your tower", red)
    pygame.display.update()

    # set towers
    tower_click = False
    while tower_click == False:
        for evt in pygame.event.get():
            if evt.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print(pos)
                detect = Point(pos[0], pos[1])
                # print(detect.rect.top, detect.rect.bottom,detect.rect.left,detect.rect.right)
                # print(pygame.sprite.spritecollide(Point(pos[0],pos[1]), baseList, False))
                base_list = pygame.sprite.spritecollide(detect, baseList, False)
                if base_list != []:
                    for base in base_list:
                        tower_place(base.rect.centerx, base.rect.centery, base)
                        tower_click = True

    # initiate game timer
    game_start = pygame.time.get_ticks()
    spawn_count = 0

    while not game_over:

        # game end loop
        while game_close == True:
            screen.fill(blue)
            your_score(money)
            message("You Won! Press Q-Quit or C-Play Again", red)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # shooting
        towerList.update()

        # update enemy and move bullets
        shotList.update()
        enemyList.update()

        # draw screen
        # screen.fill(white)
        screen.blit(backgroundIMG, (0, 0))
        all_sprites_list.draw(screen)
        your_score(money)
        pygame.display.update()
        clock.tick(game_speed)
        timer = pygame.time.get_ticks() - game_start

        # create elephant enemy
        if timer >= spawn_time[spawn_count]:
            enemy_create(path[0][0], path[0][1])
            spawn_count += 1
            if spawn_count == len(spawn_time) - 1:
                spawn_complete = True

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                quit()
                x = False
            if evt.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                detect = Point(pos[0], pos[1])
                if pygame.sprite.spritecollide(detect, towerList, False) != []:
                    tower_list = pygame.sprite.spritecollide(detect, towerList, False)
                    for tower in tower_list:
                        money = tower.upgrade(money, upgrade_cost)
                        if money == None:
                            money = 0
                if pygame.sprite.spritecollide(detect, baseList, False) != []:
                    base_list = pygame.sprite.spritecollide(detect, baseList, False)
                    for base in base_list:
                        if money >= tower_cost:
                            tower_place(base.rect.centerx, base.rect.centery, base)
                            money -= tower_cost

    # quit
    pygame.quit()
    quit()


######################################################################################
################################  value setup and call game loop #####################

# set colours and icons
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (148, 148, 184)
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
archerIMG = [pygame.image.load('archer_tower2.png')
    , pygame.image.load('archer_tower3.png')
    , pygame.image.load('archer_tower4.png')
    , pygame.image.load('archer_tower5.png')]
arrowIMG = pygame.image.load('arrow.png')
backgroundIMG = pygame.image.load('Tower_def background.png')

# base image setup
baseIMG = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.gfxdraw.aacircle(baseIMG, 20, 20, 19, grey)
pygame.gfxdraw.filled_circle(baseIMG, 20, 20, 19, grey)

# path, base locations and spawn times
path = ((0, 220), (100, 220), (100, 100), (220, 100), (220, 250), (380, 250), (380, 180), (600, 180))
tower_base = ((60, 180), (160, 140), (260, 220), (340, 140), (540, 230), (540, 130))
spawn_time = (
1000, 7000, 14000, 20000, 25000, 26000, 30000, 31000, 32000, 33000, 34000, 35000, 36000, 37000, 38000, 39000,
9999999999)

# set game screen
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tower defence game by Mark')
pygame.display.set_icon(archerIMG[0])
game_speed = 10
timer = 0

# set sprite groups
shotList = pygame.sprite.Group()
baseList = pygame.sprite.Group()
towerList = pygame.sprite.Group()
enemyList = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()

clock = pygame.time.Clock()

message("Welcome to TOWER DEFENCE", red)
pygame.display.update()
time.sleep(2)
screen.fill(white)
pygame.display.update()
gameLoop()
