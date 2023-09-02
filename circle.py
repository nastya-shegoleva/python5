import pygame
from random import randrange


def random_color() -> tuple[int, int, int]:
    return randrange(0, 255), randrange(0, 255), randrange(0, 255)


def draw_object(screen: pygame.Surface, obj:  list[pygame.Color, list[int, int], int, tuple[int, int]]):
    w, h = screen.get_size()
    screen.fill((0, 0, 0))
    index_del = []
    for circle in obj:
        pygame.draw.circle(screen, circle[0], circle[1], circle[2])
        circle[1][0] += circle[3][0] / fps
        circle[1][1] += circle[3][1] / fps
        if w < circle[1][0] or circle[1][0] < 0 or h < circle[1][1] or circle[1][1] < 0:
            index_del.append(obj.index(circle))
    for el in index_del:
        obj.pop(el)
    return obj


if __name__ == '__main__':
    size = w, h = 600, 600
    screen = pygame.display.set_mode(size)
    running = True
    shape = []
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()
    fps = 60
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shape.append([pygame.Color(random_color()), [w // 2, h // 2], randrange(10, 50),
                                  (randrange(-50, 50, 12), randrange(-50, 50, 13))])
        shape = draw_object(screen, shape)
        clock.tick(fps)
        pygame.display.flip()
