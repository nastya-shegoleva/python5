from random import randrange

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
        if self.apple_flag:
            if self.rect.y > h - 24:
                self.rect.y = h - 24
            else:
                self.rect = self.rect.move(0, 60 / fps)
        else:
            self.rect = self.rect.move(randrange(3) - 1, randrange(3) - 1)

        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            self.image = self.apple
            self.apple_flag = True


if __name__ == '__main__':
    size = w, h = 620, 620
    screen = pygame.display.set_mode(size)
    running = True
    screen.fill((0, 0, 0))
    all_sprite = pygame.sprite.Group()
    for _ in range(20):
        Block(all_sprite)
    clock = pygame.time.Clock()
    fps = 60
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
