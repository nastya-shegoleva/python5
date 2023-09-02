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
        # self.ag = (-90, 0, 90, 180)
        self.count = 0
        # self.image = pygame.transform.rotate(Mario.image, self.ag[self.count % 4])
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 530
        self.tuple_img = (Mario.image, Mario.image_2, Mario.image_3)

    def update(self, *args) -> None:
        if args and args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_RIGHT:
            self.image = self.tuple_img[self.count % 3]
            self.count += 1
            self.rect.move_ip(5, 0)
        if args and args[0].type == pygame.KEYUP and args[0].key == pygame.K_RIGHT:
            self.image = self.tuple_img[0]
            self.count += 1
            self.rect.move_ip(5, 0)

if __name__ == '__main__':
    size = w, h = (620, 620)
    screen = pygame.display.set_mode(size)
    running = True
    screen.fill((0, 0, 0))
    image = load_image('image/mario.png', -1)
    img_1 = image.subsurface((100, 0, 100, 100))
    img_2 = pygame.transform.scale(image, (100, 100))

    all_sprite = pygame.sprite.Group()
    Mario(all_sprite)
    clock = pygame.time.Clock()
    fps = 30
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            screen.fill((0, 0, 0))
            all_sprite.draw(screen)
            all_sprite.update(event)
        clock.tick(fps)
        pygame.display.flip()
