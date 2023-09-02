import math

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


class Mario(pygame.sprite.Sprite):
    img = pygame.transform.scale(load_image('image/mario_1_2_3.png', -1).subsurface(100, 0, 82, 84), (80, 80))

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = self.img.get_rect()
        self.rect.x = 200
        self.rect.y = 310

    def rotate(self, x_mouse, y_mouse):
        new_image = pygame.transform.rotate(self.img,
                                            math.degrees(math.atan2(x_mouse - self.rect.x, y_mouse - self.rect.y)))
        new_rect = new_image.get_rect(center=self.rect.center)
        screen.fill((0, 0, 40))
        screen.blit(new_image, new_rect)


if __name__ == '__main__':
    size = w, h = (620, 620)
    screen = pygame.display.set_mode(size)
    all_sprite = pygame.sprite.Group()
    Mario(all_sprite)
    clock = pygame.time.Clock()
    fps = 30
    character = Mario()
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        character.rotate(*pygame.mouse.get_pos())
        pygame.display.update()
