from random import randrange, choice

import pygame


def load_image(name, colorkey=None) -> pygame.Surface:
    pygame.init()
    image = pygame.image.load(name)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
    return image


class Particle(pygame.sprite.Sprite):
    fire = [pygame.transform.scale(load_image("image/apple.png", -1), (20, 20)), pygame.transform.scale(
        load_image("image/img.png", -1), (30, 30))]

    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(choice(fire), (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprite)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self, *args):
        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect((0, 0, w, h)):
            self.kill()


def create_particles(position):
    count = 25
    numbers = range(-5, 6)
    for _ in range(count):
        Particle(position, choice(numbers), choice(numbers))


class Block(pygame.sprite.Sprite):
    block = pygame.transform.scale(load_image("image/block.png", -1), (25, 25))
    apple = pygame.transform.scale(load_image("image/apple.png", -1), (26, 26))

    def __init__(self, *groups):
        super().__init__(*groups)

        self.image = Block.block
        self.apple_img = Block.apple
        self.rect = self.image.get_rect()
        self.rect.x = randrange(0, w)
        self.rect.y = randrange(0, 50)
        self.apple_flag = False

    def update(self, *args):
        # if self.apple_flag:
        #     if self.rect.y > h - 24:
        #         self.rect.y = h - 24
        #     else:
        #         self.rect = self.rect.move(0, 60 / fps)
        # else:
        self.rect = self.rect.move(randrange(3) - 1, randrange(3) - 1)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            self.kill()
            self.apple_flag = True
            create_particles(args[0].pos)


if __name__ == '__main__':
    size = w, h = 620, 620
    screen = pygame.display.set_mode(size)
    running = True
    screen.fill((0, 0, 0))
    GRAVITY = 0.3
    all_sprite = pygame.sprite.Group()
    for _ in range(20):
        Block(all_sprite)
    fon = Block()
    clock = pygame.time.Clock()
    fps = 30
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            all_sprite.update(event)
        screen.fill((0, 0, 0))
        all_sprite.draw(screen)
        all_sprite.update()
        clock.tick(fps)
        pygame.display.flip()
