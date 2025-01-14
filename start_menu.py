import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 36)

class Button:
    def __init__(self, x, y, width, height, color, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_surface = font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

button = Button(300, 250, 200, 50, (255, 0, 0), "Click Me")

button = Button(300, 250, 200, 50, (255, 0, 0), "Quit")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.is_clicked(event.pos):
                print("Button clicked!")

    screen.fill((255, 255, 255))
    button.draw(screen)
    pygame.display.flip()

pygame.quit()
