import pygame

pygame.init()
size = W, H = 600, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Задание №1')
flag = True
pi = 3.14
my_font = pygame.font.Font('font/DancingScript-SemiBold.ttf', 30)
text = my_font.render('Lesson 3. Snowman', True, (25, 255, 50))
# text = my_font.render('Lesson 3. Snowman', True, (70, 255, 100))
# text = my_font.render('Lesson 3. Snowman', True, 'blue')
# text = my_font.render('Lesson 3. Snowman', True, 'black')
while flag:
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, 'black', (W // 2, 500), 110, 3)
    pygame.draw.circle(screen, 'black', (W // 2, 313), 80, 3)
    pygame.draw.line(screen, 'black', [100, 350], [198, 458], 3)
    pygame.draw.line(screen, 'black', [400, 458], [500, 350], 3)
    pygame.draw.circle(screen, 'black', (330, 300), 4)
    pygame.draw.circle(screen, 'black', (275, 300), 4)
    pygame.draw.polygon(screen, 'orange', ((300, 325), (292, 330), (308, 330)))
    pygame.draw.arc(screen, 'black', (290, 340, 20, 10), pi, 2 * pi, 3)
    screen.blit(text, (200, 100))
    # =============================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
            pygame.quit()
    pygame.display.update()
