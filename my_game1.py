import pygame

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 450))
pygame.display.set_caption('My Game')
flag = True
foto_new = pygame.image.load('image/nAST_page-0001.jpg').convert_alpha()
foto = pygame.transform.scale(foto_new, (800, 450))
walk_right = [pygame.image.load('image/человек_правая/чел1_правая.png').convert_alpha(),
              pygame.image.load('image/человек_правая/чел2_правая.png').convert_alpha(),
              pygame.image.load('image/человек_правая/чел3_правая.png').convert_alpha(),
              pygame.image.load('image/человек_правая/чел4_правая.png').convert_alpha()]
walk_left = [pygame.image.load('image/человек_левая/чел1_лев (2).png').convert_alpha(),
             pygame.image.load('image/человек_левая/чел4_лев (2).png').convert_alpha(),
             pygame.image.load('image/человек_левая/чел3_лев.png').convert_alpha(),
             pygame.image.load('image/человек_левая/чел2_лев.png').convert_alpha()]
ghost = pygame.image.load('image/призрак.png').convert_alpha()
foto_loser = pygame.image.load('image/foto2.png').convert_alpha()
bullet = pygame.image.load("image/bullet.png").convert_alpha()
bullet_new = pygame.transform.scale(bullet, (40, 40))
lst_bullet = []
chet = 0
x_pos = 0
sound = pygame.mixer.Sound('sound/river-night_gkhvj8e_-1.mp3')
sound.play()
x = 100
player_speed = 5
jump = 10
flag_jump = False
y_pos = 290
x_pos_ghost = 736
ghost_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ghost_timer, 5000)
lst_ghost = []
quit_metod = True
font = pygame.font.Font('font/DancingScript-SemiBold.ttf', 50)
text = font.render('You lose', True, 'LightGreen')
font_2 = pygame.font.Font('font/DancingScript-SemiBold.ttf', 20)
text_again = font_2.render('Play again', True, 'Aquamarine')
text_again_rect = text_again.get_rect(topleft=(355, 370))
bullet_coll = 6
while flag:
    screen.blit(foto, (x_pos, 0))
    screen.blit(foto, (x_pos + 800, 0))
    if quit_metod:
        # ====================================== столкновение игроков
        player_rect = walk_right[0].get_rect(topleft=(x, y_pos))
        if lst_ghost:
            for (pos, ghost_person) in enumerate(lst_ghost):
                screen.blit(ghost, ghost_person)
                ghost_person.x -= 10
                if x_pos_ghost < -10:
                    lst_ghost.pop(pos)
                if player_rect.colliderect(ghost_person):
                    quit_metod = False
        # ======================================= движение картинки
        if chet == 3:
            chet = 0
        else:
            chet += 1
        if x_pos == -800:
            x_pos = 0
        else:
            x_pos -= 10
        # ======================================= управление клавишами
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and x > 10:
            x -= player_speed
        elif keys[pygame.K_RIGHT] and x < 710:
            x += player_speed

        if keys[pygame.K_LEFT]:
            screen.blit(walk_left[chet], (x, y_pos))
        else:
            screen.blit(walk_right[chet], (x, y_pos))
        # ==================================== прыжок
        if not flag_jump:
            if keys[pygame.K_SPACE]:
                flag_jump = True
        else:
            if jump >= -10:
                if jump > 0:
                    y_pos -= (jump * jump) // 2
                else:
                    y_pos += (jump * jump) // 2
                jump -= 1
            else:
                flag_jump = False
                jump = 10
        # =====================================выпуск снарядов
        if lst_bullet:
            for pos, bul in enumerate(lst_bullet):
                screen.blit(bullet_new, (bul.x, bul.y))
                bul.x += 8
                if bul.x > 820:
                    lst_bullet.pop(pos)
                if lst_ghost:
                    for (index, ghost2) in enumerate(lst_ghost):
                        if bul.colliderect(ghost2):
                            lst_ghost.pop(index)
                            lst_bullet.pop(pos)
    else:
        screen.fill((0, 15, 0))
        screen.blit(text, (320, 150))
        screen.blit(foto_loser, (350, 250))
        pygame.mixer.pause()
        screen.blit(text_again, text_again_rect)
        mouse_pos = pygame.mouse.get_pos()

        if text_again_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            quit_metod = True
            x = 100
            lst_ghost.clear()
            sound.play()
            lst_bullet.clear()
    pygame.display.update()
    # ======================================= закрытие экрана
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
            pygame.quit()
        if event.type == ghost_timer:
            lst_ghost.append(ghost.get_rect(topleft=(720, 310)))
        if quit_metod and event.type == pygame.KEYUP and event.key == pygame.K_1 and bullet_coll > 0:
            lst_bullet.append(bullet_new.get_rect(topleft=(x + 60, y_pos + 30)))
            bullet_coll -= 1

    clock.tick(12)
