import pygame
from random import choice
import sys


tile_images = {
    'wall': ('rock.png', ),
    'grass': ('graphics/floor/grass1.png', 'graphics/floor/grass2.png', 'graphics/floor/grass3.png',
              'graphics/floor/grass4.png'),
    'flowers': ('graphics/details/f1.png', 'graphics/details/f2.png', 'graphics/details/f3.png',
                'graphics/details/f4.png', 'graphics/details/f5.png'),
    'trees': ('graphics/objects/0.png', 'graphics/objects/01.png', 'graphics/objects/02.png', 'graphics/objects/03.png',
              'graphics/objects/04.png', 'graphics/objects/05.png')
}

enemy_images = {
    'bamboo': ('data/bamboo/0.png', 'data/bamboo/1.png', 'data/bamboo/2.png', 'data/bamboo/3.png'),
    'squid':  ('data/squid/0.png', 'data/squid/1.png', 'data/squid/2.png', 'data/squid/3.png'),
    'racoon': ('data/racoon/0.png', 'data/racoon/1.png', 'data/racoon/2.png', 'data/racoon/3.png')
}

levels = ['level1.txt', 'level2.txt', 'level3.txt']

tile_width = tile_height = 64


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(s):
    intro_text = []
    if s == 'start':
        intro_text = ["ЗАСТАВКА", "",
                      "Правила игры",
                      "Убейте всех монстров",
                      "Нажмите любую кнопку, чтобы начать игру",
                      'Движение - WASD, стрельба и прицел мышью',
                      'Регенерация - E']

    elif s == 'end':
        intro_text = ["Игра окончена",
                      "Ваш счет:", str(level.score)]

    elif s == 'level_change':
        intro_text = ["Вы прошли уровень",
                      "Ваш счет:", str(level.score),
                      "Нажмите любую кнопку, чтобы перейти на следующий уровень"]

    fon = pygame.transform.scale(pygame.image.load('data/icons/fon.png'), (1280, 720))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif (event.type == pygame.KEYDOWN or
                  event.type == pygame.MOUSEBUTTONDOWN) and s != 'end':
                return
        pygame.display.flip()
        clock.tick(60)


def level_load(filename):
    filename = 'data/levels/' + filename
    with open(filename, 'r') as mapfile:
        level_map = [line.split() for line in mapfile]
    return level_map


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos_x, pos_y, health, damage, speed, groups, obstacle_sprites):
        super().__init__(*groups)

        self.max_health = health
        self.cur_health = health
        self.damage = damage

        self.enemy_type = enemy_type

        self.iter_count = 0
        self.cur_frame = 0

        self.hp_bar_group = pygame.sprite.Group()
        self.hp_bar = HealthPointBar(self, (self.hp_bar_group, ))

        self.bullet_group = pygame.sprite.Group()
        self.obstacle_sprites = obstacle_sprites
        if self.enemy_type == 'stay':
            self.walk = [
                    pygame.transform.scale(pygame.image.load(enemy_images['bamboo'][0]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['bamboo'][1]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['bamboo'][2]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['bamboo'][3]), (64, 64))
                    ]
        elif self.enemy_type == 'follow':
            self.walk = [
                    pygame.transform.scale(pygame.image.load(enemy_images['racoon'][0]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['racoon'][1]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['racoon'][2]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['racoon'][3]), (64, 64))
                    ]
        elif self.enemy_type == 'move_vertical' or self.enemy_type == 'horizontal_move':
            self.walk = [
                    pygame.transform.scale(pygame.image.load(enemy_images['squid'][0]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['squid'][1]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['squid'][2]), (64, 64)),
                    pygame.transform.scale(pygame.image.load(enemy_images['squid'][3]), (64, 64))
                    ]
        elif self.enemy_type == 'boss':
            self.walk = [
                pygame.transform.scale(pygame.image.load('data/aooni/0.png'), (64, 64)),
                pygame.transform.scale(pygame.image.load('data/aooni/1.png'), (64, 64)),
                pygame.transform.scale(pygame.image.load('data/aooni/2.png'), (64, 64)),
                pygame.transform.scale(pygame.image.load('data/aooni/3.png'), (64, 64))
            ]

        self.image = self.walk[self.cur_frame % 4]
        self.rect = self.image.get_rect().move(pos_x * tile_width, pos_y * tile_height)

        self.speed = speed
        self.direction = pygame.math.Vector2()
        if self.enemy_type == 'move_vertical':
            self.direction.y = -1
        elif self.enemy_type == 'horizontal_move':
            self.direction.x = -1

    def update(self):
        if self.cur_health == 0:
            self.kill()
            level.score += 20
            if self.enemy_type == 'boss':
                level.boss_killed = True
        self.hp_bar_group.draw(level.surface)
        self.hp_bar_group.update()

        for bullet in level.player.bullet_group:
            if bullet.rect.colliderect(self.rect):
                self.cur_health -= 20
                bullet.kill()
            elif pygame.sprite.spritecollideany(bullet, level.collide_sprites):
                bullet.kill()

        if self.enemy_type == 'follow':
            self.follow(500)

        elif self.enemy_type == 'boss':
            self.follow(800)

        elif self.enemy_type == 'move_vertical':
            self.vertical_move()

        elif self.enemy_type == 'horizontal_move':
            self.horizontal_move()

        self.frame_change()

        if self.rect.colliderect(level.player.rect):
            level.player.cur_health -= self.damage
            if level.player.cur_cond == 'left':
                level.player.rect.x += 50
            if level.player.cur_cond == 'right':
                level.player.rect.x -= 50
            if level.player.cur_cond == 'up':
                level.player.rect.y += 50
            if level.player.cur_cond == 'down':
                level.player.rect.y -= 50

    def follow(self, dist):

        if level.player.rect.x > self.rect.x:
            self.direction.x = 1
        elif level.player.rect.x < self.rect.x:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if level.player.rect.y > self.rect.y:
            self.direction.y = 1
        elif level.player.rect.y < self.rect.y:
            self.direction.y = -1
        else:
            self.direction.y = 0

        if ((self.rect.x - level.player.rect.x) ** 2 + (self.rect.y - level.player.rect.y) ** 2) ** 0.5 <= dist:
            self.rect.x += self.direction.x * self.speed
            self.collision('horizontal')
            self.rect.y += self.direction.y * self.speed
            self.collision('vertical')

    def vertical_move(self):
        if pygame.sprite.spritecollideany(self, self.obstacle_sprites):
            self.direction.y *= -1

        self.rect.y += self.direction.y * self.speed

    def horizontal_move(self):
        if pygame.sprite.spritecollideany(self, self.obstacle_sprites):
            self.direction.x *= -1

        self.rect.x += self.direction.x * self.speed

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom

    def frame_change(self):
        self.cur_frame = (self.cur_frame + 1) % 4
        if self.iter_count == 400:
            self.iter_count = 0
        if self.iter_count % 7 == 0:
            self.image = self.walk[self.cur_frame]

        self.iter_count += 1


class HealthPointBar(pygame.sprite.Sprite):
    def __init__(self, owner, groups):
        super().__init__(*groups)
        self.owner = owner
        self.hp = self.owner.cur_health

        self.image = pygame.Surface((64, 10))
        self.image.fill((150, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        if self.owner.cur_health <= 0:
            self.kill()
        else:
            self.rect.bottom = self.owner.rect.top - 10
            self.rect.x = self.owner.rect.x
            width = (int(self.owner.cur_health / self.owner.max_health * 64))
            if width != 0:
                self.image = pygame.Surface((width, 10))
            self.image.fill((150, 0, 0))


class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, groups):
        super().__init__(*groups)
        self.image = pygame.image.load('data/fireball.png')
        self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect(center=(pos_x + 25, pos_y + 25))
        self.dir = (pygame.mouse.get_pos()[0] - pos_x + 25, pygame.mouse.get_pos()[1] - pos_y + 25)

    def update(self):
        self.rect.x += self.dir[0] // 45
        self.rect.y += self.dir[1] // 45


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y, groups):
        super().__init__(*groups)
        self.image = pygame.image.load('data/' + choice(tile_images[tile_type]))
        self.rect = self.image.get_rect().move(
            tile_width * x, tile_height * y)
        if tile_type == 'wall':
            self.rect.height = 45
        else:
            self.rect.height = 90
            self.rect = self.rect.inflate(-15, -20)


class Level:
    def __init__(self, level, surface, score):
        self.all_sprites = pygame.sprite.Group()
        self.collide_sprites = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.world_map = level_load(level)
        self.surface = surface

        self.camera = Camera()

        self.create_map()

        self.boss_killed = False

        self.score = score

    def create_map(self):
        player_x = player_y = 0
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                Tile('grass', x, y, (self.all_sprites,))
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                if self.world_map[y][x] == '#':
                    Tile('wall', x, y, (self.all_sprites, self.collide_sprites))
                elif self.world_map[y][x] == "T":
                    Tile('trees', x, y, (self.all_sprites, self.collide_sprites))
                elif self.world_map[y][x] == "F":
                    Tile('flowers', x, y, (self.all_sprites, ))
                elif self.world_map[y][x] == "E":
                    Enemy('follow', x, y, 100, 10, 2, (self.all_sprites, self.enemies)
                          , self.collide_sprites)
                elif self.world_map[y][x] == "EMV":
                    Enemy('move_vertical', x, y, 100, 50, 2, (self.all_sprites, self.enemies)
                          , self.collide_sprites)
                elif self.world_map[y][x] == "EMH":
                    Enemy('horizontal_move', x, y, 100, 50, 2, (self.all_sprites, self.enemies)
                          , self.collide_sprites)
                elif self.world_map[y][x] == "ES":
                    Enemy('stay', x, y, 100, 10, 2, (self.all_sprites, self.enemies)
                          , self.collide_sprites)
                elif self.world_map[y][x] == 'p':
                    player_x = x
                    player_y = y

        self.player = Player(player_x, player_y, 100, (self.all_sprites, ), self.collide_sprites)

    def run(self):
        self.camera.update(self.player)
        for sprite in self.all_sprites:
            self.camera.apply(sprite)
        self.all_sprites.draw(self.surface)
        self.player.update()
        self.player.bullet_group.draw(self.surface)
        self.player.bullet_group.update()
        self.enemies.update()
        self.player.hp_bar_group.draw(self.surface)
        self.player.hp_bar_group.update()
        self.spawn_boss()

    def spawn_boss(self):
        if not self.enemies:
            if not self.boss_killed:
                return Enemy('boss', 10, 3, 240, 50, 1, (self.all_sprites, self.enemies), self.collide_sprites)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, health, groups, obstacle_sprites):
        super().__init__(*groups)

        self.max_health = health
        self.cur_health = health

        self.hp_bar_group = pygame.sprite.Group()
        self.hp_bar = HealthPointBar(self, (self.hp_bar_group, ))

        self.bullet_group = pygame.sprite.Group()

        self.iter_counter = 0
        self.cur_cond = 'down'
        self.cur_frame = 0
        self.obstacle_sprites = obstacle_sprites
        self.walk = {
            'down': [
                pygame.image.load('data/player/down/down_0.png'),
                pygame.image.load('data/player/down/down_1.png'),
                pygame.image.load('data/player/down/down_2.png'),
                pygame.image.load('data/player/down/down_3.png')
            ],
            'up': [
                pygame.image.load('data/player/up/up_0.png'),
                pygame.image.load('data/player/up/up_1.png'),
                pygame.image.load('data/player/up/up_2.png'),
                pygame.image.load('data/player/up/up_3.png')
            ],
            'right': [
                pygame.image.load('data/player/right/right_0.png'),
                pygame.image.load('data/player/right/right_1.png'),
                pygame.image.load('data/player/right/right_2.png'),
                pygame.image.load('data/player/right/right_3.png')
            ],
            'left': [
                pygame.image.load('data/player/left/left_0.png'),
                pygame.image.load('data/player/left/left_1.png'),
                pygame.image.load('data/player/left/left_2.png'),
                pygame.image.load('data/player/left/left_3.png')
            ]
        }
        self.image = self.walk['down'][0]
        self.rect = self.image.get_rect().move(x * tile_width, y * tile_height)
        self.direction = pygame.math.Vector2()
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.cur_cond = 'up'
            self.cur_frame = (self.cur_frame + 1) % len(self.walk[self.cur_cond])
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.cur_cond = 'down'
            self.cur_frame = (self.cur_frame + 1) % len(self.walk[self.cur_cond])
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.cur_cond = 'right'
            self.cur_frame = (self.cur_frame + 1) % len(self.walk[self.cur_cond])
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.cur_cond = 'left'
            self.cur_frame = (self.cur_frame + 1) % len(self.walk[self.cur_cond])
        else:
            self.direction.x = 0

        if keys[pygame.K_e]:
            self.heal()

        if self.direction.x == 0 and self.direction.y == 0:
            self.cur_frame = 0

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom

    def shoot(self):
        if self.alive():
            return Fireball(self.rect.x, self.rect.y, (self.bullet_group, level.all_sprites))

    def heal(self):
        if self.cur_health != 100:
            self.cur_health += 2

    def update(self):
        self.input()
        self.move()
        if self.cur_health <= 0 or level.boss_killed:
            self.kill()
            global running
            running = False

    def move(self):
        if self.iter_counter == 100:
            self.iter_counter = 0

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.speed
        self.collision('vertical')

        if self.iter_counter % 7 == 0:
            self.image = self.walk[self.cur_cond][self.cur_frame]
        self.iter_counter += 1


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - 1280 // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - 720 // 2)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Игра')
    icon = pygame.image.load('data/icons/icon.jpg')
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()

    start_screen('start')

    score = 0

    pygame.mixer.music.load('data/sounds/music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.6)

    for i in levels:
        level = Level(i, screen, score)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    level.player.shoot()

            screen.fill('black')
            level.run()
            pygame.display.update()
            clock.tick(60)

        score += level.score

        if level.player.cur_health <= 0 or (i == levels[-1] and level.boss_killed):
            start_screen('end')
            break
        else:
            start_screen('level_change')
