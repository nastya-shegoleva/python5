import pygame
import sys

pygame.init()
SIZE = WEIGHT, HIEGHT = 800, 600
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
increase = True
radius = 1
x = WEIGHT // 2 - 50
y = HIEGHT // 2 + 10
w = 100
h = 20
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if increase:
        x -= 0.5
        y -= 0.5
        w += 1
        h += 1
    else:
        x += 0.5
        y += 0.5
        w -= 1
        h -= 1
    if x <= 250 or y <= 190:
        increase = False
    elif x >= 350 and y >= 290:
        increase = True
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 5)
    pygame.display.update()

    clock.tick(30)
#Репозиторий: git@github.com:nastya-shegoleva/task5.git
# хеш коммита:1913ade
