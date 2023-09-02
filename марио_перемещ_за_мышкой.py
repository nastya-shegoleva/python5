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
    image = pygame.transform.scale(load_image('image/mario_1_2_3.png', -1).subsurface(0, 0, 97, 84), (80, 80))
    image_2 = pygame.transform.scale(load_image('image/mario_1_2_3.png', -1).subsurface(100, 0, 82, 84), (80, 80))
    image_3 = pygame.transform.scale(load_image('image/mario_1_2_3.png', -1).subsurface(190, 0, 100, 84), (80, 80))

    def __init__(self, *groups):
        super().__init__(*groups)
        self.count = 0
        self.rect = self.image.get_rect()
        self.tuple_img = (Mario.image, Mario.image_2, Mario.image_3)
        self.fps = 40
        self.x = 200
        self.y = 200

    def update(self, *args):
        self.pos = pygame.mouse.get_pos()
        self.rect.x = self.pos[0] - self.x
        self.rect.y = self.pos[1] - self.y

        if args and args[0].type == pygame.MOUSEMOTION:
            self.image = self.tuple_img[self.count % 3]
            self.count += 1
        elif args and args[0].type == pygame.MOUSEBUTTONUP and pygame.key.get_pressed()[0]:
            self.image = self.tuple_img[0]


if __name__ == '__main__':
    size = w, h = (620, 620)
    screen = pygame.display.set_mode(size)
    running = True
    screen.fill((0, 0, 0))
    all_sprite = pygame.sprite.Group()
    Mario(all_sprite)
    clock = pygame.time.Clock()
    fps = 20
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            screen.fill((0, 0, 0))
            all_sprite.draw(screen)
            all_sprite.update(event)
        clock.tick(fps)
        pygame.display.flip()
