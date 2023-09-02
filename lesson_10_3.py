from random import choice, randrange, sample

import pygame
import os, sys

from data_db import db_session
from data_db.creating_tag import add_inf_game, add_stand_game
from data_db.inf_game import InfGame
from data_db.standard_game import Standard_game

SIZE_SP = 50
FPS = 10
LEVEL = 2


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = (obj.abs_pos[0] + self.dx) % ((max_x + 1) * SIZE_SP)
        obj.rect.y = (obj.abs_pos[1] + self.dy) % ((max_y + 1) * SIZE_SP)

    def update(self):
        self.dx = 0
        self.dy = 0


def load_image(name, colorkey=None) -> pygame.Surface:
    pygame.init()
    fullname = os.path.join('image', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
    return image


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, choice(numbers), choice(numbers))


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png", -1)]

    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(choice(fire), (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particle_group)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 0.4

    def update(self, *args):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect((0, 0, max_x * SIZE_SP, max_y * SIZE_SP)):
            self.kill()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None
        self.pos = None
        self.sheet = None
        self.frames = []

    def get_event(self, event):
        pass

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


class Dot(Sprite):
    dot = pygame.transform.scale(load_image("dot.png", -1), (SIZE_SP, SIZE_SP))
    apple = pygame.transform.scale(load_image("apple.png", -1), (SIZE_SP // 2, SIZE_SP // 2))
    strawberry = pygame.transform.scale(load_image("strawberry.png", -1), (SIZE_SP // 2, SIZE_SP // 2))

    elem = (dot, apple, strawberry)

    def __init__(self, x, y):
        super().__init__(dot_group)
        self.image = choice(Dot.elem)
        self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2))
        self.rect = self.rect.move(x, y)
        self.pos = (x // SIZE_SP, y // SIZE_SP)
        self.abs_pos = [self.rect.x, self.rect.y]

    def update(self) -> None:
        global SCORE, level_map
        x, y = self.pos
        # print(x, y)
        if pygame.sprite.spritecollideany(self, hero_group):
            if SCORE != 'GAME OVER':
                SCORE += 1
            self.kill()
            if level == 'inf':
                level_map[y][x] = '*'


def flag_step(flag):
    flag %= 4
    if flag == 0:
        return [0, 8]
    elif flag == 1:
        return [0, -8]
    elif flag == 2:
        return [8, 0]
    elif flag == 3:
        return [-8, 0]


class Ghost(Sprite):
    columns = 6
    rows = 1

    pink = pygame.transform.scale(load_image("ghost_pink.png", -1), ((SIZE_SP - 10) * 6, (SIZE_SP - 10)))
    red = pygame.transform.scale(load_image("ghost_red.png", -1), ((SIZE_SP - 10) * 6, (SIZE_SP - 10)))
    blue = pygame.transform.scale(load_image("ghost_blue.png", -1), ((SIZE_SP - 10) * 6, (SIZE_SP - 10)))
    orange = pygame.transform.scale(load_image("ghost_orange.png", -1), ((SIZE_SP - 10) * 6, (SIZE_SP - 10)))
    ghost_color = (pink, red, blue, orange)

    def __init__(self, x, y):
        super().__init__(ghost_group)
        sheet = choice(Ghost.ghost_color)
        self.frames = []
        self.cut_sheet(sheet, Ghost.columns, Ghost.rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.abs_pos = [self.rect.x, self.rect.y]
        self.pos = (x // SIZE_SP, y // SIZE_SP)
        self.v = [0, 8]
        self.flag = 0
        self.count = 0

    def move(self):
        global level
        self.pos = self.pos[0] % (max_x + 1), self.pos[1] % (max_y + 1)
        x, y = self.pos

        if pygame.sprite.spritecollideany(self, block_group):
            self.flag = choice([0, 1, 2, 3])

        if level == 'inf':
            print(f'x, y = {x, y}')
            prev_y = level_map[y - 1][x] == "." if y != 0 else level_map[max_y][x] == "."
            next_y = level_map[y + 1][x] == "." if y != max_y else level_map[0][x] == "."
            prev_x = level_map[y][x - 1] == "." if x != 0 else level_map[y][max_x] == "."
            next_x = level_map[y][x + 1] == "." if x != max_x else level_map[y][0] == "."
        else:
            prev_y = level_map[y - 1][x] == "." if y > 0 else False
            next_y = level_map[y + 1][x] == "." if y < max_y - 1 else False
            prev_x = level_map[y][x - 1] == "." if x > 0 else False
            next_x = level_map[y][x + 1] == "." if x < max_x - 1 else False

        self.v = flag_step(self.flag)

        # if y > 0 and level_map[y - 1][x] == "." and self.flag == 1 and self.v[1]:
        #     self.rect.move_ip(0, SIZE_SP // self.v[1])
        # elif y < max_y - 1 and level_map[y + 1][x] == "." and self.flag == 0 and self.v[1]:
        #     self.rect.move_ip(0, SIZE_SP // self.v[1])
        # elif x > 0 and level_map[y][x - 1] == "." and self.flag == 3 and self.v[0]:
        #     self.rect.move_ip(SIZE_SP // self.v[0], 0)
        # elif x < max_x - 1 and level_map[y][x + 1] == "." and self.flag == 2 and self.v[0]:
        #     self.rect.move_ip(SIZE_SP // self.v[0], 0)
        # else:
        #     self.flag += 1
        #     self.flag %= 4

        if prev_y and self.flag == 1 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif next_y and self.flag == 0 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif prev_x and self.flag == 3 and self.v[0]:
            self.rect.move_ip(SIZE_SP // self.v[0], 0)
        elif next_x and self.flag == 2 and self.v[0]:
            self.rect.move_ip(SIZE_SP // self.v[0], 0)
        else:
            self.flag += 1
            self.flag %= 4

        rect_field = pygame.Rect(x * SIZE_SP, y * SIZE_SP, SIZE_SP,
                                 SIZE_SP)

        rect_x, rect_y = self.rect.x, self.rect.y

        point_1 = rect_field.collidepoint(rect_x + (SIZE_SP - 10) // 2, rect_y)
        point_2 = rect_field.collidepoint(rect_x + (SIZE_SP - 10), rect_y + (SIZE_SP - 10) // 2)
        point_3 = rect_field.collidepoint(rect_x + (SIZE_SP - 10) // 2, rect_y + (SIZE_SP - 10))
        point_4 = rect_field.collidepoint(rect_x, rect_y + (SIZE_SP - 10) // 2)

        point_0 = rect_field.collidepoint(rect_x + (SIZE_SP - 10) // 2, rect_y + (SIZE_SP - 10) // 2)

        dx, dy = self.v[0], self.v[1]

        if not point_0:
            if dy > 0:
                if not point_1:
                    self.pos = x, y + 1
            elif dy < 0:
                if not point_3:
                    self.pos = x, y - 1
            elif dx > 0:
                if not point_4:
                    self.pos = x + 1, y
            elif dx < 0:
                if not point_2:
                    self.pos = x - 1, y
        # self.abs_pos = [self.pos[0] * SIZE_SP, self.pos[1] * SIZE_SP]

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        self.move()


class Tile(Sprite):
    tile = pygame.transform.scale(load_image("tile.jpg"), (SIZE_SP - 5, SIZE_SP - 5))

    def __init__(self, x, y):
        super().__init__(block_group)
        self.image = Tile.tile
        self.rect = self.image.get_rect().move(x, y)
        self.abs_pos = [self.rect.x, self.rect.y]


class Pacman(Sprite):
    columns = 3
    rows = 1
    img = pygame.transform.scale(load_image("main_hero.png", -1), ((SIZE_SP - 5) * 3, SIZE_SP - 5))

    def __init__(self, x, y):
        super().__init__(hero_group)
        self.sheet = Pacman.img
        self.frames = []
        self.cut_sheet(self.sheet, Pacman.columns, Pacman.rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.pos = (x // SIZE_SP, y // SIZE_SP)

    def update(self, *args) -> None:

        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        global SCORE, level, camera
        if pygame.sprite.spritecollideany(self, ghost_group):
            if level == 'inf':
                add_inf_game(SCORE)
                create_particles((self.rect[0], self.rect[1]))
            else:
                add_stand_game(SCORE, level)
                create_particles((SIZE_SP * self.pos[0], SIZE_SP * self.pos[1]))
            self.kill()
            SCORE = 'GAME OVER'
            level = None

    def move(self, x, y):
        if level != 'inf':
            self.pos = (x, y)
            self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2)).move(
                SIZE_SP * self.pos[0], SIZE_SP * self.pos[1])
        else:
            global camera
            camera.dx -= SIZE_SP * (x - self.pos[0])
            camera.dy -= SIZE_SP * (y - self.pos[1])

            self.pos = (x, y)
            for sprite in block_group:
                camera.apply(sprite)
            for sprite in ghost_group:
                camera.apply(sprite)
            for sprite in dot_group:
                camera.apply(sprite)

    def rotate(self, movement):
        x, y = self.pos
        self.frames = []
        if movement == "up":
            image = pygame.transform.rotate(Pacman.img, 90)
            self.cut_sheet(image, Pacman.rows, Pacman.columns)
            self.image = self.frames[self.cur_frame]
        elif movement == "down":
            image = pygame.transform.rotate(Pacman.img, -90)
            self.cut_sheet(image, Pacman.rows, Pacman.columns)
            self.image = self.frames[self.cur_frame]
        elif movement == "left":
            image = pygame.transform.flip(Pacman.img, True, False)
            self.cut_sheet(image, Pacman.columns, Pacman.rows)
            self.image = self.frames[self.cur_frame]
        elif movement == "right":
            image = Pacman.img
            self.cut_sheet(image, Pacman.columns, Pacman.rows)
            self.image = self.frames[self.cur_frame]
        if level != 'inf':
            self.rect = self.rect.move(x * SIZE_SP, y * SIZE_SP)
        else:
            self.rect.x, self.rect.y = (max_x // 2) * SIZE_SP, (max_y // 2) * SIZE_SP


def load_level(filename):
    filename = 'image/' + filename
    with open(filename, 'r') as mapfile:
        level_map = [line.strip() for line in mapfile]
    maxW = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(maxW, '.')), level_map))


def generate_level(levels):
    pacman, x, y, count_local = None, None, None, 0
    for y in range(len((levels))):
        for x in range(len(levels[y])):
            if levels[y][x] == '.':
                Dot(x * SIZE_SP, y * SIZE_SP)
                count_local += 1
            elif levels[y][x] == '#':
                Tile(x * SIZE_SP, y * SIZE_SP)
            elif levels[y][x] == '@':
                pacman = Pacman(x * SIZE_SP, y * SIZE_SP)
                Dot(x * SIZE_SP, y * SIZE_SP)
                levels[y][x] = "."
                count_local += 1
            elif levels[y][x] == '&':
                Ghost(x * SIZE_SP, y * SIZE_SP)
                Dot(x * SIZE_SP, y * SIZE_SP)
                levels[y][x] = "."
                count_local += 1
    return pacman, x, y, count_local + SCORE


class Button(Sprite):
    button = pygame.transform.scale(load_image('button.png', -1), (SIZE_SP * 4, SIZE_SP + 40))

    def __init__(self, button_group, text, x, y):
        super().__init__(button_group)
        self.image = Button.button
        self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2))
        self.rect = self.rect.move(x * SIZE_SP, y * SIZE_SP)
        self.text = text
        self.add_text = my_font.render(text, True, pygame.Color('white'))

    def update(self, screen, *args) -> None:
        global level, my_answer, mode
        screen.blit(self.add_text, (self.rect.x + self.rect.width // 8, self.rect.y + self.rect.height // 2.7))

        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            print(self.text)
            if self.text == 'Бесконечный':
                level = 'inf'
            elif self.text == 'Стандартный':
                level = 1
            elif self.text == 'Рейтинг':
                level = 'rating'
            elif self.text == 'Настройки':
                level = "setting"
            elif self.text == 'Включить звук':
                my_answer = "on"
            elif self.text == 'Выключить звук':
                my_answer = "off"
            elif self.text == 'Общий р.':
                mode = 1
            elif self.text == "Стандартный р.":
                mode = 2
            elif self.text == "Бесконечный р.":
                mode = 3


def start_screen():
    global level, level_map, hero, SCORE, max_x, max_y, ghost_group, particle_group, hero_group, dot_group, \
        block_group, screen, camera, my_answer, sound_flag

    SCORE = 0
    screen.fill(0)

    button_group = pygame.sprite.Group()

    intro_text = [
        "Pac-man", " ",
        "Режим: 1. Бесконечный\t2. Стандартный",
        "3. Рейтинг",
        "4. Настройки"
    ]
    x, y = 3, 1

    for text in ['Бесконечный', "Стандартный", "Рейтинг", "Настройки"]:
        Button(button_group, text, x, y)
        x, y = x, y + 2

    for line in intro_text:
        print(line)
    level = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            button_group.draw(screen)
            button_group.update(screen, event)
        if level == 'inf':
            level = 'inf'
            ghost_group = pygame.sprite.Group()
            hero_group = pygame.sprite.Group()
            block_group = pygame.sprite.Group()
            dot_group = pygame.sprite.Group()
            particle_group = pygame.sprite.Group()

            level_map = load_level(f"level_inf.map")
            hero, max_x, max_y, count = generate_level(level_map)
            camera = Camera()
            screen = pygame.display.set_mode(((max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP))
            screen.fill(0)
            camera.update()

            start_game_inf()
        elif level == 1:
            while level and level <= LEVEL:
                ghost_group = pygame.sprite.Group()
                hero_group = pygame.sprite.Group()
                block_group = pygame.sprite.Group()
                dot_group = pygame.sprite.Group()
                particle_group = pygame.sprite.Group()

                level_map = load_level(f"level_{level}.map")
                hero, max_x, max_y, count = generate_level(level_map)
                level = start_game(hero, max_x, max_y, count)
            # game_over_screen()
        elif level == 'rating':
            rating_screen()
        elif level == 'setting':
            setting_screen()
        if sound_flag:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()
        button_group.draw(screen)
        button_group.update(screen)
        pygame.display.flip()


def terminate():
    global SCORE, level
    if level:
        if level == 'inf':
            add_inf_game(SCORE)
        if level >= 1:
            add_stand_game(SCORE, level)
    pygame.quit()
    sys.exit


def generate_dot():
    global level_map
    for y in range(sample([0, 1, 2], 1)[0], len(level_map), 2):
        for x in range(sample([0, 1, 2], 1)[0], len(level_map[y]), 2):
            if level_map[y][x] == '*':
                Dot(x * SIZE_SP, y * SIZE_SP)
                level_map[y][x] = '.'


def start_game_inf():
    global SCORE, level
    game = True
    pause = False
    clock = pygame.time.Clock()
    time = False
    esc_key = False
    # level = None
    while game:
        text = my_font.render(f"SCORE: {SCORE}", False, pygame.Color('white'))
        if not esc_key:
            if not pause:
                screen.fill(0)
                if SCORE == 'GAME OVER':
                    if not time:
                        time_now = pygame.time.get_ticks() + 1000
                        time = True
                elif SCORE % 8 == 0:
                    generate_dot()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        terminate()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            move_inf(hero, "up")
                        elif event.key == pygame.K_DOWN:
                            move_inf(hero, "down")
                        elif event.key == pygame.K_LEFT:
                            move_inf(hero, "left")
                        elif event.key == pygame.K_RIGHT:
                            move_inf(hero, "right")
                        elif event.key == pygame.K_p:
                            pygame.mixer.music.pause()
                            pause = True
                        elif event.key == pygame.K_ESCAPE:
                            pygame.mixer.music.pause()
                            esc_key = True
                update_screen(screen, text)
                if time and time_now <= pygame.time.get_ticks():
                    game_over_screen()
                    game = False
            else:
                pause = pause_screen()
        else:
            if level:
                if level == 'inf':
                    add_inf_game(SCORE)
                    esc_key = start_screen()

        pygame.display.flip()
        clock.tick(FPS)


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
            hero.rotate(movement)
    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
            hero.rotate(movement)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
            hero.rotate(movement)
    elif movement == "right":
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)
            hero.rotate(movement)


def move_inf(hero, movement):
    x, y = hero.pos
    if movement == "up":
        prev_y = y - 1 if y != 0 else max_y
        if level_map[prev_y][x] in '.*':
            hero.move(x, prev_y)
            hero.rotate(movement)
    elif movement == "down":
        next_y = y + 1 if y != max_y else 0
        if level_map[next_y][x] in '.*':
            hero.move(x, next_y)
            hero.rotate(movement)
    elif movement == "left":
        prev_x = x - 1 if x != 0 else max_x
        if level_map[y][prev_x] in '.*':
            hero.move(prev_x, y)
            hero.rotate(movement)
    elif movement == "right":
        next_x = x + 1 if x != max_x else 0
        if level_map[y][next_x] in '.*':
            hero.move(next_x, y)
            hero.rotate(movement)


def update_screen(screen, text, dot=True, ghost=True, hero=True, block=True, particle=True):
    # screen.fill(0)
    if dot:
        dot_group.draw(screen)
        dot_group.update()
    if ghost:
        ghost_group.draw(screen)
        ghost_group.update()
    if hero:
        hero_group.draw(screen)
        hero_group.update()
    if block:
        block_group.draw(screen)
    if particle:
        particle_group.draw(screen)
        particle_group.update()

    screen.blit(text, (max_x * SIZE_SP - text.get_width() + 10, 10))


def pause_screen():
    global sound_flag
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if sound_flag:
                if event.key == pygame.K_p:
                    pygame.mixer.music.unpause()
                    return False
            else:
                if event.key == pygame.K_p:
                    return False

    # text_pause = my_font.render(f'SCORE: {SCORE}', False, pygame.Color('white'))
    print("PAUSED")
    return True


def start_game(hero, max_x, max_y, count):
    global level, my_answer
    screen = pygame.display.set_mode(((max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP))

    game = True
    pause = False
    clock = pygame.time.Clock()
    time = False
    esc_key = False
    while game:

        text = my_font.render(f'SCORE: {SCORE}', False, pygame.Color('white'))
        if not esc_key:
            if not pause:
                screen.fill(0)
                if count == SCORE:
                    return level + 1
                if SCORE == 'GAME OVER':
                    if not time:
                        time_now = pygame.time.get_ticks() + 3000
                        time = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        terminate()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            move(hero, "up")
                        elif event.key == pygame.K_DOWN:
                            move(hero, "down")
                        elif event.key == pygame.K_LEFT:
                            move(hero, "left")
                        elif event.key == pygame.K_RIGHT:
                            move(hero, "right")
                        elif event.key == pygame.K_p:
                            pygame.mixer.music.pause()
                            pause = True
                        elif event.key == pygame.K_ESCAPE:
                            esc_key = True

                update_screen(screen, text)
                if time and time_now <= pygame.time.get_ticks():
                    game_over_screen()
                    game = False
            else:
                pause = pause_screen()
        else:
            if level:
                if level >= 1:
                    add_stand_game(SCORE, level)
                    esc_key = start_screen()
        pygame.display.flip()
        clock.tick(FPS)


def rating_screen():
    global screen
    x, y = 1, 1

    button_group = pygame.sprite.Group()

    for text in ['Общий р.', "Стандартный р.", "Бесконечный р."]:
        Button(button_group, text, x, y)
        x, y = x + 4, y

    esc_key = False

    while True:
        screen.fill(0)
        if not esc_key:
            all_list = []
            stand_list = []
            inf_list = []
            db_sess = db_session.create_session()
            inf_game = db_sess.query(InfGame).all()
            all_list.extend(inf_game)
            inf_list.extend(inf_game)
            stand_game = db_sess.query(Standard_game).all()
            all_list.extend(stand_game)
            stand_list.extend(stand_game)
            all_list = sorted(all_list, key=lambda x: x.create_date, reverse=True)
            inf_list = sorted(inf_list, key=lambda x: x.create_date, reverse=True)
            stand_list = sorted(stand_list, key=lambda x: x.create_date, reverse=True)

            db_sess.close()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    esc_key = True
                button_group.draw(screen)
                button_group.update(screen, event)

            count = 1
            x_r, y_r = 1, 2
            if mode == 1:
                for el in all_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Бесконечный" if "InfGame" in el.__class__.__name__ else "Стандартный"} | {el.score}',
                        True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (0, y_r * SIZE_SP))
                    y_r += 1
            if mode == 2:
                for el in stand_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Стандартный"} | {el.score} | {el.level}', True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (2.5 * SIZE_SP, y_r * SIZE_SP))
                    y_r += 1
                    all_list.clear()
            if mode == 3:
                for el in inf_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Бесконечный"} | {el.score}',
                        True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (5.7 * SIZE_SP, y_r * SIZE_SP))
                    y_r += 1

        else:
            esc_key = start_screen()

        button_group.draw(screen)
        button_group.update(screen)
        pygame.display.flip()


def setting_screen():
    global screen, sound_flag, my_answer
    x, y = 2, 1
    screen.fill(0)
    button_group = pygame.sprite.Group()
    for text in ['Включить звук', 'Выключить звук']:
        Button(button_group, text, x, y)
        x, y = x + 5, y
    start = True
    esc_key = False
    while start:
        if not esc_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    esc_key = True
                button_group.draw(screen)
                button_group.update(screen, event)
                if my_answer == 'on':
                    sound_flag = True
                elif my_answer == 'off':
                    sound_flag = False
                if sound_flag:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.pause()
        else:
            esc_key = start_screen()

        button_group.draw(screen)
        button_group.update(screen)
        pygame.display.flip()


def game_over_screen():
    SIZE_SCREEN = (max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP

    game_over_img = pygame.transform.scale(load_image('game_over.png', -1), SIZE_SCREEN)
    screen = pygame.display.set_mode(SIZE_SCREEN)
    start = True
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                start = False
        screen.fill(0)
        screen.blit(game_over_img, (0, 0, max_x + 1, max_y + 1))

        pygame.display.flip()
    start_screen()


if __name__ == '__main__':
    pygame.init()

    db_session.global_init("db/game.db")
    pygame.mixer.music.load('sound/pac_myz.mp3')

    SCORE = 0

    my_font = pygame.font.SysFont(None, 30)
    max_x = 10
    max_y = 10
    level_map = None
    hero = None
    camera = None

    ghost_group = pygame.sprite.Group()
    hero_group = pygame.sprite.Group()
    block_group = pygame.sprite.Group()
    dot_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()

    screen = pygame.display.set_mode(((max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP))

    level = None
    my_answer = None
    sound_flag = True
    mode = None
    start_screen()

    # print(f"mode = {mode}")
    #
    #
    # if mode == 1:
    #     level = 'inf'
    #
    #     ghost_group = pygame.sprite.Group()
    #     hero_group = pygame.sprite.Group()
    #     block_group = pygame.sprite.Group()
    #     dot_group = pygame.sprite.Group()
    #
    #     level_map = load_level(f"level_inf.map")
    #     hero, max_x, max_y, count = generate_level(level_map)
    #     camera = Camera()
    #     screen = pygame.display.set_mode(((max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP))
    #     camera.update()
    #
    #     start_game_inf()
    # elif mode == 2:
    #     while level and level <= LEVEL:
    #         ghost_group = pygame.sprite.Group()
    #         hero_group = pygame.sprite.Group()
    #         block_group = pygame.sprite.Group()
    #         dot_group = pygame.sprite.Group()
    #
    #         level_map = load_level(f"level_{level}.map")
    #         hero, max_x, max_y, count = generate_level(level_map)
    #         level = start_game(hero, max_x, max_y, count)
    #     # game_over_screen()
    # elif mode == 3:
    #     rating_screen()
    # elif mode == 4:
    #     setting_screen()
