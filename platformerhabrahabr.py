#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем библиотеку pygame
import pygame
import pygame.mixer
import sys
from blocks import *
from monsters import *
from player import *
import subprocess

# Инициализируем Pygame сразу после импорта
pygame.init()

# Объявляем переменные
WIN_WIDTH = 800  # Ширина создаваемого окна
WIN_HEIGHT = 640  # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную
BACKGROUND_COLOR = "#000000"
MENU_FONT = pygame.font.Font(None, 36)
MENU_TEXT_COLOR = (255, 255, 255)

FILE_DIR = os.path.dirname(__file__)


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - WIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(l, t, w, h)


def loadLevel():
    global playerX, playerY  # объявляем глобальные переменные, это координаты героя

    levelFile = open('%s/levels/1.txt' % FILE_DIR)
    line = " "
    commands = []
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    endLine = line.find("|")  # то ищем символ конца строки
                    level.append(line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"

        if line[0] != "":  # если строка не пустая
            commands = line.split()  # разбиваем ее на отдельные команды
            if len(commands) > 1:  # если количество команд > 1, то ищем эти команды
                if commands[0] == "player":  # если первая команда - player
                    playerX = int(commands[1])  # то записываем координаты героя
                    playerY = int(commands[2])
                if commands[0] == "portal":  # если первая команда portal, то создаем портал
                    tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                    entities.add(tp)
                    platforms.append(tp)
                    animatedEntities.add(tp)
                if commands[0] == "monster":  # если первая команда monster, то создаем монстра
                    mn = Monster(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]),
                                 int(commands[5]),int(commands[6]))
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)

def main():
    pygame.init()  # Инициация PyGame, обязательная строчка
    # Очистка списков перед каждым новым уровнем
    level.clear()
    entities.empty()
    animatedEntities.empty()
    monsters.empty()
    platforms.clear()
    # загрузка уровня
    loadLevel()
    screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
    pygame.display.set_caption("Безумный Леха")  # Пишем в шапку
    bg_image = pygame.image.load(
        "blocks/задний фон.jpg").convert()  # Замените "путь_к_изображению.jpg" на путь к вашему изображению
    gaz_music = pygame.mixer.Sound("music/gaz.mp3")
    gaz_music.set_volume(0.2)  # Установка громкости в половину максимальной
    up_music = pygame.mixer.Sound("music/stay_pl.mp3")
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    bg.blit(bg_image, (0, 0))
    left = right = False  # по умолчанию - стоим
    up = False
    running = False

    hero = Player(playerX, playerY)  # создаем героя по (x,y) координатам
    entities.add(hero)
    timer = pygame.time.Clock()
    x = y = 0  # координаты
    for row in level:  # вся строка
        for col in row:  # каждый символ
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == 's':
                wl = Wall(x, y)
                entities.add(wl)
                platforms.append(wl)
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "P":
                pr = Princess(x, y)
                entities.add(pr)
                platforms.append(pr)
                animatedEntities.add(pr)

            x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
        y += PLATFORM_HEIGHT  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)
    game_over = False
    while not game_over:  # Основной цикл программы
        timer.tick(60)
        for e in pygame.event.get():  # Обрабатываем события
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_UP:
                up_music.play()
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                gaz_music.play()
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                gaz_music.play()
                right = True
            if e.type == KEYDOWN and e.key == K_LSHIFT:
                running = True
            if e.type == KEYUP and e.key == K_UP:
                up_music.stop()
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                gaz_music.stop()
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                gaz_music.stop()
                left = False
            if e.type == KEYUP and e.key == K_LSHIFT:
                running = False
        if hero.winner or hero.live == 0:
            game_over = True
            # Завершаем анимации, музыку и другие процессы, если есть
            up_music.stop()
            gaz_music.stop()
        if game_over:
            break
        screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
        if hero.respawning:
            screen.blit(hero.death_image, (500, 500))  # Отобразите изображение смерти
        animatedEntities.update()  # показываем анимацию
        monsters.update(platforms)  # передвигаем всех монстров
        camera.update(hero)  # центризируем камеру относительно персонажа
        hero.update(left, right, up, running, platforms)  # передвижения
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.update()  # обновление и вывод всех изменений на экран
    if hero.live == 0:
        return game_over_menu(screen)  # Если возвращено True, то перезапускаем игру
    if hero.winner:
        return winner_menu(screen)  # Если победа меню побед


level = []
entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться


def display_menu(screen):
    # Создайте текст и кнопки меню
    start_text = MENU_FONT.render("Начать игру", True, MENU_TEXT_COLOR)
    exit_text = MENU_FONT.render("Выйти", True, MENU_TEXT_COLOR)
    control_text = MENU_FONT.render("Управление", True, MENU_TEXT_COLOR)
    start_rect = start_text.get_rect()
    exit_rect = exit_text.get_rect()
    control_rect = control_text.get_rect()
    picture = pygame.image.load('screen_picture/pictureMain.jpg').convert()
    bg = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    # Размещение текста меню на экране
    start_rect.centerx = WIN_WIDTH // 2
    start_rect.centery = WIN_HEIGHT // 2 + 20
    control_rect.centerx = WIN_WIDTH // 2
    control_rect.centery = WIN_HEIGHT // 2 + 70
    exit_rect.centerx = WIN_WIDTH // 2
    exit_rect.centery = WIN_HEIGHT // 2 + 120

    bg.blit(picture, (0, 0))
    screen.blit(bg, (0, 0))
    screen.blit(start_text, start_rect)
    screen.blit(control_text, control_rect)
    screen.blit(exit_text, exit_rect)
    pygame.display.flip()


def game_over_menu(screen):
    # Жаль, что ты проиграл
    font = pygame.font.Font(None, 36)
    text = font.render("Жаль, что ты проиграл конечно", True, (255, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (WIN_WIDTH // 2, WIN_HEIGHT // 2 - 40)

    # Кнопка "Повторить"
    retry_button = pygame.Rect(WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 20, 200, 40)
    retry_text = font.render("Повторить", True, (255, 255, 255))
    retry_text_rect = retry_text.get_rect()
    retry_text_rect.center = retry_button.center

    # Кнопка "Закрыть программу"
    quit_button = pygame.Rect(WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 70, 200, 40)
    quit_text = font.render("Закрыть программу", True, (255, 255, 255))
    quit_text_rect = quit_text.get_rect()
    quit_text_rect.center = quit_button.center

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if retry_button.collidepoint(mouse_pos):
                    # Здесь вы можете добавить логику для перезапуска игры
                    return main()
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        screen.fill((0, 0, 0))  # Заливаем экран черным цветом
        screen.blit(text, text_rect)
        screen.blit(retry_text, retry_text_rect)
        screen.blit(quit_text, quit_text_rect)
        pygame.display.flip()


def winner_menu(screen):
    # Победа
    font = pygame.font.Font(None, 36)
    text = font.render("Победа!!!", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (WIN_WIDTH // 2, WIN_HEIGHT // 2 - 40)

    # Кнопка "Повторить"
    retry_button = pygame.Rect(WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 20, 200, 40)
    retry_text = font.render("Повторить", True, (255, 0, 0))
    retry_text_rect = retry_text.get_rect()
    retry_text_rect.center = retry_button.center

    # Кнопка "Закрыть программу"
    quit_button = pygame.Rect(WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 70, 200, 40)
    quit_text = font.render("Закрыть программу", True, (255, 0, 0))
    quit_text_rect = quit_text.get_rect()
    quit_text_rect.center = quit_button.center

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if retry_button.collidepoint(mouse_pos):
                    # Здесь вы можете добавить логику для перезапуска игры
                    return main()
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        screen.fill((0, 0, 0))  # Заливаем экран черным цветом
        screen.blit(text, text_rect)
        screen.blit(retry_text, retry_text_rect)
        screen.blit(quit_text, quit_text_rect)
        pygame.display.flip()


def main_menu():
    pygame.init()
    pygame.display.set_caption("Безумный Лёха!")

    # Создаем start_rect и exit_rect с нужными размерами
    width = 200
    height = 40
    start_rect = pygame.Rect(WIN_WIDTH // 2 - width // 2, WIN_HEIGHT // 2 + 20, width, height)
    control_rect = pygame.Rect(WIN_WIDTH // 2 - width // 2, WIN_HEIGHT // 2 + 70, width, height)
    exit_rect = pygame.Rect(WIN_WIDTH // 2 - width // 2, WIN_HEIGHT // 2 + 120, width, height)
    screen = pygame.display.set_mode(DISPLAY)
    # музыка на задний фон
    pygame.mixer.music.load('music/bg.mp3')
    pygame.mixer.music.play(-1)  # -1 означает бесконечное воспроизведение
    while True:
        display_menu(screen)
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    pygame.mixer.music.fadeout(2000)  # Плавное выключение музыки в течение 2 секунд
                    main()  # Начните игру, когда выбрана опция "Начать игру"
                if control_rect.collidepoint(mouse_pos):
                    # Запустите скрипт control.py как отдельный процесс
                    subprocess.Popen(["python", "control.py"])
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main_menu()  # Запускаем главное меню при запуске программы. Передаём их в функцию main_menu
