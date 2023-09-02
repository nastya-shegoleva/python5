from random import choice, randrange

import pygame
import os, sys

from data_db_snake import db_session_snake
from data_db_snake.creating_tag_snake import add_inf_game, add_stand_game
from data_db_snake.inf_game_snake import InfGame_snake
from data_db_snake.standart_game_snake import Standard_game_snake

SIZE_SP = 20
FPS = 10
LEVEL = 2


def load_image(name, colorkey=None) -> pygame.Surface:
    pygame.init()
    fullname = os.path.join('image', name)
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


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, choice(numbers), choice(numbers))


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("particle_snake.png", -1)]

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
        if not self.rect.colliderect((0, 0, scr_x * SIZE_SP, scr_y * SIZE_SP)):
            self.kill()


def update_screen(screen, text, dot=True, hero=True, particle=True, ghost=True):
    if dot:
        dot_group.draw(screen)
        dot_group.update()
    if ghost:
        ghost_group.draw(screen)
        ghost_group.update()
    if hero:
        hero_group.draw(screen)
        hero_group.update()
    if particle:
        particle_group.draw(screen)
        particle_group.update()
    screen.blit(text, (scr_x * SIZE_SP - text.get_width() - 15, 10))


class Dot(Sprite):
    dot = pygame.transform.scale(load_image("apple.png", -1), (SIZE_SP, SIZE_SP))

    def __init__(self, x, y):
        super().__init__(dot_group)
        self.image = Dot.dot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args) -> None:
        global SCORE, count_friut, ghost_flag
        if pygame.sprite.spritecollideany(self, hero_group):
            if SCORE != 'GAME OVER':
                SCORE += 1
                self.kill()
            count_friut = False
            if SCORE % 3 == 0:
                ghost_flag = False
        else:
            count_friut = True


def generate_dot():
    global count_friut, SCORE
    if not count_friut:
        Dot(randrange(25, (SIZE_SP * scr_x) - 25), randrange(25, (SIZE_SP * scr_y) - 25))
    count_friut = True


def ghost_generate():
    global ghost_flag, SCORE
    if not ghost_flag:
        Ghost(randrange(25, (SIZE_SP * scr_x) - 25), randrange(25, (SIZE_SP * scr_y) - 25))
    ghost_flag = True


class Snake(Sprite):
    snake = pygame.transform.scale(load_image('new_head_snake.png', -1), (SIZE_SP * 2, SIZE_SP * 2))

    def __init__(self):
        super().__init__(hero_group)
        self.image = Snake.snake
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200
        self.head_snake_list = [self.rect.x, self.rect.y]
        self.snake_body_list = [[self.rect.x, self.rect.y], [self.rect.x - 40, self.rect.y]]

    def update(self, *args) -> None:
        global SCORE, direction, change_to, scr_x, scr_y, screen, level
        if args and args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_RIGHT:
            change_to = 'right'
        if args and args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_LEFT:
            change_to = 'left'
        if args and args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP:
            change_to = 'up'
        if args and args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_DOWN:
            change_to = 'down'
        if any((change_to == "right" and not direction == "left",
                change_to == "left" and not direction == "right",
                change_to == "up" and not direction == "down",
                change_to == "down" and not direction == "up")):
            direction = change_to
        if direction == "right":
            self.image = pygame.transform.rotate(Snake.snake, -90)
            self.rect.x += 20
        elif direction == "left":
            self.image = pygame.transform.rotate(Snake.snake, 90)
            self.rect.x -= 20
        elif direction == "up":
            self.image = pygame.transform.rotate(Snake.snake, 0)
            self.rect.y -= 20
        elif direction == "down":
            self.image = pygame.transform.rotate(Snake.snake, 180)
            self.rect.y += 20

        if not self.rect.colliderect((25, 25, scr_x * SIZE_SP - 20, scr_y * SIZE_SP - 20)) and SCORE != 'GAME OVER':
            if level == 'inf':
                add_inf_game(SCORE)
            elif level >= 1:
                add_stand_game(SCORE, level)
            if self.rect.x - 15 < 0 or self.rect.y - 15 < 0:
                create_particles((self.rect.x + 10, self.rect.y + 10))
                self.kill()
                SCORE = 'GAME OVER'
                level = None
            elif self.rect.x + 15 > scr_x or self.rect.y + 15 > scr_y:
                create_particles((self.rect.x - 30, self.rect.y - 30))
                self.kill()
                SCORE = 'GAME OVER'
                level = None
        elif pygame.sprite.spritecollideany(self, ghost_group) and SCORE != 'GAME OVER':
            if level == 'inf':
                add_inf_game(SCORE)
            elif level >= 1:
                add_stand_game(SCORE, level)
            create_particles((self.rect.x, self.rect.y))
            self.kill()
            SCORE = 'GAME OVER'

    def move(self, x, y):
        self.update()


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

    pink = pygame.transform.scale(load_image("ghost_pink.png", -1), ((SIZE_SP + 5) * 6, (SIZE_SP + 5)))
    red = pygame.transform.scale(load_image("ghost_red.png", -1), ((SIZE_SP + 5) * 6, (SIZE_SP + 5)))
    blue = pygame.transform.scale(load_image("ghost_blue.png", -1), ((SIZE_SP + 5) * 6, (SIZE_SP + 5)))
    orange = pygame.transform.scale(load_image("ghost_orange.png", -1), ((SIZE_SP + 5) * 6, (SIZE_SP + 5)))
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
        global SCORE
        self.pos = self.pos[0] % (scr_x + 1), self.pos[1] % (scr_y + 1)
        x, y = self.pos

        if not self.rect.colliderect((30, 30, scr_x * SIZE_SP - 30, scr_y * SIZE_SP - 30)):
            self.flag = choice([0, 1, 2, 3])

        self.v = flag_step(self.flag)

        if self.flag == 1 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif self.flag == 0 and self.v[1]:
            self.rect.move_ip(0, SIZE_SP // self.v[1])
        elif self.flag == 3 and self.v[0]:
            self.rect.move_ip(SIZE_SP // self.v[0], 0)
        elif self.flag == 2 and self.v[0]:
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
        global SCORE, ghost_flag
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if SCORE != 'GAME OVER':
            if SCORE % 13 == 0:
                self.kill()
        self.move()


def start_game_inf():
    global SCORE, level, field, movement, change_to
    game = True
    clock = pygame.time.Clock()
    time = False
    pause = False
    esc_key = False
    field = pygame.transform.scale(load_image('black_field.png'), screen.get_size())
    snake = Snake()
    dot = Dot(randrange(25, (SIZE_SP * scr_x) - 25), randrange(25, (SIZE_SP * scr_y) - 25))
    while game:
        text = my_font.render(f"SCORE: {SCORE}", False, pygame.Color('cornflower blue'))
        if not esc_key:
            if not pause:
                screen.blit(field, (0, 0))
                generate_dot()
                ghost_generate()
                if SCORE == 'GAME OVER':
                    if not time:
                        time_now = pygame.time.get_ticks() + 1000
                        time = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        close()
                    if event.type == pygame.KEYDOWN:
                        hero_group.update(event)
                        if event.key == pygame.K_UP:
                            snake.move(snake, 'up')
                        elif event.key == pygame.K_DOWN:
                            snake.move(snake, 'down')
                        elif event.key == pygame.K_LEFT:
                            snake.move(snake, 'left')
                        elif event.key == pygame.K_RIGHT:
                            snake.move(snake, 'right')
                        if event.key == pygame.K_p:
                            pause = True
                        elif event.key == pygame.K_ESCAPE:
                            pygame.mixer.music.pause()
                            esc_key = True
                    dot.update()
                update_screen(screen, text)

                if time and time_now <= pygame.time.get_ticks():
                    game_over_screen()
                    SCORE = 0
                    game = False
            else:
                pause = pause_screen()
        else:
            if level:
                if level == 'inf':
                    add_inf_game(SCORE)
                    esc_key = splash_screen()
        clock.tick(FPS)
        pygame.display.flip()


def start_game_standart():
    global SCORE, level, field, movement, change_to, chet
    game = True
    clock = pygame.time.Clock()
    time = False
    pause = False
    esc_key = False
    level_num_2 = False
    field = pygame.transform.scale(load_image('black_field.png'), screen.get_size())
    snake = Snake()
    dot = Dot(randrange(25, (SIZE_SP * scr_x) - 25), randrange(25, (SIZE_SP * scr_y) - 25))
    win = False
    level = 1
    while game:
        if not level_num_2:
            text = my_font.render(f"SCORE: {SCORE}", False, pygame.Color('cornflower blue'))
            if not esc_key:
                if not pause:
                    screen.blit(field, (0, 0))
                    generate_dot()
                    ghost_generate()
                    if chet == SCORE:
                        level_num_2 = True
                    if SCORE == 'GAME OVER':
                        if not time:
                            time_now = pygame.time.get_ticks() + 1000
                            time = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            close()
                        if event.type == pygame.KEYDOWN:
                            hero_group.update(event)
                            if event.key == pygame.K_UP:
                                snake.move(snake, 'up')
                            elif event.key == pygame.K_DOWN:
                                snake.move(snake, 'down')
                            elif event.key == pygame.K_LEFT:
                                snake.move(snake, 'left')
                            elif event.key == pygame.K_RIGHT:
                                snake.move(snake, 'right')
                            if event.key == pygame.K_p:
                                pause = True
                            elif event.key == pygame.K_ESCAPE:
                                pygame.mixer.music.pause()
                                esc_key = True
                        dot.update()
                    update_screen(screen, text)

                    if time and time_now <= pygame.time.get_ticks():
                        game_over_screen()
                        SCORE = 0
                        game = False
                else:
                    pause = pause_screen()
            else:
                if level:
                    if level == 1:
                        add_stand_game(SCORE, level)
                        esc_key = splash_screen()
        else:
            level = 2
            field_green = pygame.transform.scale(load_image('field.png'), screen.get_size())
            if SCORE != 'GAME OVER' and level_num_2:
                text = my_font.render(f"SCORE: {int(SCORE) - 3}", False, pygame.Color('cornflower blue'))
            if not esc_key:
                if not pause:
                    screen.blit(field_green, (0, 0))
                    generate_dot()
                    ghost_generate()
                    if SCORE == 'GAME OVER':
                        if not time:
                            time_now = pygame.time.get_ticks() + 1000
                            time = True
                    if SCORE == 26 and level_num_2:
                        win = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            close()
                        if event.type == pygame.KEYDOWN:
                            hero_group.update(event)
                            if event.key == pygame.K_UP:
                                snake.move(snake, 'up')
                            elif event.key == pygame.K_DOWN:
                                snake.move(snake, 'down')
                            elif event.key == pygame.K_LEFT:
                                snake.move(snake, 'left')
                            elif event.key == pygame.K_RIGHT:
                                snake.move(snake, 'right')
                            if event.key == pygame.K_p:
                                pause = True
                            elif event.key == pygame.K_ESCAPE:
                                pygame.mixer.music.pause()
                                esc_key = True
                        dot.update()
                    update_screen(screen, text)
                    if time and time_now <= pygame.time.get_ticks():
                        game_over_screen()
                        SCORE = 0
                        game = False
                    if win:
                        if level:
                            if level == 2:
                                add_stand_game(SCORE, level)
                                win_screen()
                                SCORE = 0
                                game = False
                else:
                    pause = pause_screen()
            else:
                if level:
                    if level == 2:
                        add_stand_game(SCORE, level)
                        esc_key = splash_screen()
        clock.tick(FPS)
        pygame.display.flip()


def game_over_screen():
    SIZE_SCREEN = (scr_x) * SIZE_SP, (scr_y) * SIZE_SP
    game_over_img = pygame.transform.scale(load_image('SNAKE.png'), SIZE_SCREEN)
    screen = pygame.display.set_mode(SIZE_SCREEN)
    start = True
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                start = False
        screen.blit(game_over_img, (0, 0, scr_x + 1, scr_y + 1))

        pygame.display.flip()
    splash_screen()


def win_screen():
    global screen, SCORE, level
    SIZE_SCREEN = (scr_x) * SIZE_SP, (scr_y) * SIZE_SP

    foto_win = pygame.transform.scale(load_image('you_win.png'), screen.get_size())
    screen = pygame.display.set_mode(SIZE_SCREEN)
    start = True
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start = False

        screen.blit(foto_win, (0, 0, scr_x + 1, scr_y + 1))

        pygame.display.flip()
    splash_screen()


def close():
    global SCORE, level
    if level:
        if level == 'inf':
            add_inf_game(SCORE)
        if level >= 1:
            add_stand_game(SCORE, level)
    pygame.quit()
    sys.exit


class Button(Sprite):
    button_green = pygame.transform.scale(load_image('button_green.png', -1), (SIZE_SP * 12, SIZE_SP * 4))

    # button_red = pygame.transform.scale(load_image('red_button.png', -1), (SIZE_SP * 12, SIZE_SP * 4))

    def __init__(self, button_group, text, x, y):
        super().__init__(button_group)
        self.image = Button.button_green
        self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2))
        self.rect = self.rect.move(x * SIZE_SP, y * SIZE_SP)
        self.text = text
        self.all_text = my_font.render(self.text, True, 'white')

    def update(self, screen, *args) -> None:
        global level
        screen.blit(self.all_text, (self.rect.x + self.rect.width // 10, self.rect.y + self.rect.height // 2.7))
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            if self.text == 'Бесконечный режим':
                level = 'inf'
            if self.text == 'Стандартный режим':
                level = 1
            if self.text == 'Рейтинг':
                level = 'rating'
            if self.text == 'Настройки':
                level = 'setting'


class Button_for_setting(Sprite):
    button_red = pygame.transform.scale(load_image('red_button.png', -1), (SIZE_SP * 10, SIZE_SP * 4))

    def __init__(self, button_group, text, x, y):
        super().__init__(button_group)
        self.image = Button_for_setting.button_red
        self.rect = self.image.get_rect(center=(SIZE_SP // 2, SIZE_SP // 2))
        self.rect = self.rect.move(x * SIZE_SP, y * SIZE_SP)
        self.text = text
        self.all_text = my_font.render(self.text, True, 'white')

    def update(self, screen, *args) -> None:
        global sound_off_on, menu, mode
        screen.blit(self.all_text, (self.rect.x + self.rect.width // 10, self.rect.y + self.rect.height // 2.7))
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            if self.text == 'Включить звук':
                sound_off_on = "on"
            if self.text == 'Выключить звук':
                sound_off_on = "off"
            if self.text == "Меню":
                menu = 'menu'
            elif self.text == 'Общий р.':
                mode = 1
            elif self.text == "Стандартный р.":
                mode = 2
            elif self.text == "Бесконечный р.":
                mode = 3


def setting_screen():
    global screen, sound_flag, sound_off_on, menu
    x, y = 6, 5
    foto_setting = pygame.transform.scale(load_image('foto_setting.png'), screen.get_size())
    screen.blit(foto_setting, (0, 0))
    button_group = pygame.sprite.Group()
    for text in ['Включить звук', 'Выключить звук']:
        Button_for_setting(button_group, text, x, y)
        x, y = x, y + 4
    but = Button_for_setting(button_group, "Меню", 33, 5)
    start = True
    menu_flag = False
    while start:
        if not menu_flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                if event.type == pygame.MOUSEBUTTONDOWN and but.rect.collidepoint(event.pos):
                    menu_flag = True
                button_group.draw(screen)
                button_group.update(screen, event)
                if sound_off_on == 'on':
                    sound_flag = True
                elif sound_off_on == 'off':
                    sound_flag = False
                if sound_flag:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.pause()

        else:
            menu_flag = splash_screen()

        button_group.draw(screen)
        button_group.update(screen)
        pygame.display.flip()


def pause_screen():
    global sound_flag
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close()
        elif event.type == pygame.KEYDOWN:
            if sound_flag:
                if event.key == pygame.K_p:
                    pygame.mixer.music.unpause()
                    return False
            else:
                if event.key == pygame.K_p:
                    return False
    return True


def rating_screen():
    global screen
    x, y = 5, 2

    button_group = pygame.sprite.Group()

    for text in ['Общий р.', "Стандартный р.", "Бесконечный р."]:
        Button_for_setting(button_group, text, x, y)
        x, y = x + 15, y

    esc_key = False

    while True:
        screen.fill(0)
        if not esc_key:
            all_list = []
            stand_list = []
            inf_list = []
            db_sess = db_session_snake.create_session()
            inf_game = db_sess.query(InfGame_snake).all()
            all_list.extend(inf_game)
            inf_list.extend(inf_game)
            stand_game = db_sess.query(Standard_game_snake).all()
            all_list.extend(stand_game)
            stand_list.extend(stand_game)
            all_list = sorted(all_list, key=lambda x: x.create_date, reverse=True)
            inf_list = sorted(inf_list, key=lambda x: x.create_date, reverse=True)
            stand_list = sorted(stand_list, key=lambda x: x.create_date, reverse=True)

            db_sess.close()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    esc_key = True
                button_group.draw(screen)
                button_group.update(screen, event)

            count = 1
            x_r, y_r = 5, 5
            if mode == 1:
                for el in all_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Бесконечный" if "InfGame" in el.__class__.__name__ else "Стандартный"} | {el.score}',
                        True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (0, y_r * SIZE_SP))
                    y_r += 2
            if mode == 2:
                for el in stand_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Стандартный"} | {el.score} | {el.level}', True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (13 * SIZE_SP, y_r * SIZE_SP))
                    y_r += 2
                    all_list.clear()
            if mode == 3:
                for el in inf_list[:6]:
                    print(el.__class__.__name__)
                    text = my_font.render(
                        f'{count} | {"Бесконечный"} | {el.score}',
                        True, pygame.Color("white"))
                    count += 1
                    screen.blit(text, (27 * SIZE_SP, y_r * SIZE_SP))
                    y_r += 2

        else:
            esc_key = splash_screen()
        button_group.draw(screen)
        button_group.update(screen)
        pygame.display.flip()


def splash_screen():
    global level, SCORE, scr_x, scr_y, particle_group, hero_group, dot_group, screen, \
        ghost_group, ghost_flag, chet, level_num_2
    SCORE = 0
    img_snake = pygame.transform.scale(load_image('img_snake.png'), screen.get_size())
    screen.blit(img_snake, (0, 0))
    button_group = pygame.sprite.Group()
    x, y = 7, 4
    for word in ['Бесконечный режим', 'Стандартный режим']:
        Button(button_group, word, x, y)
        y += 5
    x, y = 32, 4
    for word in ['Рейтинг', 'Настройки']:
        Button(button_group, word, x, y)
        y += 5
    level = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            button_group.draw(screen)
            button_group.update(screen, event)
        if level == 'inf':
            level = 'inf'
            hero_group = pygame.sprite.Group()
            dot_group = pygame.sprite.Group()
            particle_group = pygame.sprite.Group()
            ghost_group = pygame.sprite.Group()
            screen = pygame.display.set_mode(((scr_x) * SIZE_SP, (scr_y) * SIZE_SP))

            start_game_inf()
        elif level == 1:
            level = 1
            while not level_num_2:
                hero_group = pygame.sprite.Group()
                dot_group = pygame.sprite.Group()
                particle_group = pygame.sprite.Group()
                ghost_group = pygame.sprite.Group()
                screen = pygame.display.set_mode(((scr_x) * SIZE_SP, (scr_y) * SIZE_SP))
                start_game_standart()
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


if __name__ == '__main__':
    pygame.init()
    SCORE = 0
    scr_x = 40
    scr_y = 30
    db_session_snake.global_init("db_snake/game_snake.db")
    screen = pygame.display.set_mode((SIZE_SP * scr_x, SIZE_SP * scr_y))
    pygame.mixer.music.load('sound/Snake Sound.mp3')
    hero_group = pygame.sprite.Group()
    dot_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()
    ghost_group = pygame.sprite.Group()
    my_font = pygame.font.SysFont(None, 30)
    direction = 'right'
    change_to = direction
    count_friut = True
    ghost_flag = True
    level = None
    chet = 13
    level_num_2 = False
    sound_off_on = None
    sound_flag = True
    mode = None
    menu = None
    splash_screen()
