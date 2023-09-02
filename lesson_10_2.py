from math import floor, ceil
from random import choice, randrange, sample

import pygame
import os, sys

SIZE_SP = 50
FPS = 10
LEVEL = 2


def load_image(name, colorkey=None) -> pygame.Surface:
    pygame.init()
    fullname = os.path.join('image', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        # image = image.convert()
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
        super().__init__(ghost_group)
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

    def update(self) -> None:
        global SCORE
        if pygame.sprite.spritecollideany(self, hero_group):
            SCORE += 1
            self.kill()


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
        self.pos = (x // SIZE_SP, y // SIZE_SP)
        self.v = [0, 8]
        self.flag = 0
        self.count = 0

    def move(self):
        x, y = self.pos
        if pygame.sprite.spritecollideany(self, block_group):
            self.flag = choice([0, 1, 2, 3])

        self.v = flag_step(self.flag)

        if y > 0 and level_map[y - 1][x] == "." and self.flag == 1 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif y < max_y - 1 and level_map[y + 1][x] == "." and self.flag == 0 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif x > 0 and level_map[y][x - 1] == "." and self.flag == 3 and self.v[0]:
            self.rect.move_ip(SIZE_SP // self.v[0], 0)
        elif x < max_x - 1 and level_map[y][x + 1] == "." and self.flag == 2 and self.v[0]:
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

        global SCORE
        if pygame.sprite.spritecollideany(self, ghost_group):
            SCORE = 'GAME OVER'
            self.kill()
            create_particles((SIZE_SP * self.pos[0], SIZE_SP * self.pos[1]))
            for _ in range(30):
                pass

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2)).move(
            SIZE_SP * self.pos[0], SIZE_SP * self.pos[1])

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
        self.rect = self.rect.move(x * SIZE_SP, y * SIZE_SP)


def load_level(filename):
    filename = 'image/' + filename
    with open(filename, 'r') as mapfile:
        level_map = [line.strip() for line in mapfile]
    maxW = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(maxW, '.')), level_map))


def generate_level(levels):
    pacman, x, y, count_local = None, None, None, 0
    for y in range(len(levels)):
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


def start_screen():
    global level, SCORE

    SCORE = 0

    intro_text = [
        "Pac-man", " ",
        "Режим: 1. Бесконечный\t2. Стандартный",
        "3. Рейтинг",
        "4. Настройки"
    ]

    for line in intro_text:
        print(line)
    level = 1
    while True:
        text = input()
        if text == '1':
            return 1
        if text == '2':
            return 2
        if text == '3':
            return 3
        if text == '4':
            return 4
        print('введите корректные данные')


def terminate():
    pygame.quit()
    sys.exit


def start_game_inf():
    pass


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


def pause_screen():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                return False
    # text_pause = my_font.render(f'SCORE: {SCORE}', False, pygame.Color('white'))
    print("PAUSED")
    return True


def start_game(hero, max_x, max_y, count):
    global level
    screen = pygame.display.set_mode(((max_x + 1) * SIZE_SP, (max_y + 1) * SIZE_SP))

    game = True
    pause = False
    clock = pygame.time.Clock()

    while game:
        text = my_font.render(f'SCORE: {SCORE}', False, pygame.Color('white'))
        if not pause:
            if count == SCORE:
                return level + 1
            if SCORE == 'GAME OVER':
                return None
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
                        pause = True
            screen.fill(0)
            dot_group.draw(screen)
            dot_group.update()
            ghost_group.draw(screen)
            ghost_group.update()
            hero_group.draw(screen)
            hero_group.update()
            block_group.draw(screen)

            screen.blit(text, (max_x * SIZE_SP - text.get_width() + 10, 10))
        else:
            pause = pause_screen()
        pygame.display.flip()
        clock.tick(FPS)


def rating_screen():
    pass


def setting_screen():
    pass


def game_over_screen():
    print('GAME OVER')
    # start_screen()


if __name__ == '__main__':
    pygame.init()
    SCORE = 0

    my_font = pygame.font.SysFont(None, 30)

    level = 1

    mode = start_screen()
    print(f"mode = {mode}")

    if mode == 1:
        start_game_inf()
    elif mode == 2:
        while level and level <= LEVEL:
            ghost_group = pygame.sprite.Group()
            hero_group = pygame.sprite.Group()
            block_group = pygame.sprite.Group()
            dot_group = pygame.sprite.Group()

            level_map = load_level(f"level_{level}.map")
            hero, max_x, max_y, count = generate_level(level_map)
            level = start_game(hero, max_x, max_y, count)
        game_over_screen()
    elif mode == 3:
        rating_screen()
    elif mode == 4:
        setting_screen()
