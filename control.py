import pygame

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((800, 600))

# Шрифт для отображения текста
font = pygame.font.Font(None, 24)

# Текст с инструкциями по управлению
controls_text = [
    "Управление:",
    "Стрелка вверх - Перемещение вверх",
    "Стрелка влево - Перемещение влево",
    "Стрелка вправо - Перемещение вправо",
    "Левый Shift - Ускорение",
]

# Создание текстовой поверхности для инструкций
controls_surface = pygame.Surface((400, 600))
controls_surface.fill((255, 255, 255))

# Отображение инструкций на текстовой поверхности
for i, line in enumerate(controls_text):
    text_render = font.render(line, True, (0, 0, 0))
    controls_surface.blit(text_render, (10, 10 + i * 40))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # Заполняем экран белым цветом
    screen.blit(controls_surface, (200, 150))  # Отображаем инструкции

    pygame.display.flip()

pygame.quit()
