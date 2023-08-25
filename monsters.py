#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygame import *

import blocks
import pyganim
import os
import player


WIN_WIDTH = 800 #Ширина создаваемого окна
WIN_HEIGHT = 640 # Высота
MONSTER_WIDTH = 35
MONSTER_HEIGHT = 35
MONSTER_COLOR = "#2110FF"
ICON_DIR = os.path.dirname(__file__) #  Полный путь к каталогу с файлами


ANIMATION_MONSTERHORYSONTAL = [('%s/monsters/дпс.png' % ICON_DIR)]


class Monster(sprite.Sprite):
    def __init__(self, x, y, left, up, playerx, playery):
        sprite.Sprite.__init__(self)
        self.image = Surface((MONSTER_WIDTH, MONSTER_HEIGHT))
        self.image.fill(Color(MONSTER_COLOR))
        self.rect = Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.image.set_colorkey(Color(MONSTER_COLOR))
        self.startX = x
        self.startY = y
        self.xvel = left
        self.yvel = up
        boltAnim = []
        for anim in ANIMATION_MONSTERHORYSONTAL:
            boltAnim.append((anim, 0.3))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

        self.playerx = playerx
        self.playery = playery

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if self.rect.move(xvel, yvel).colliderect(p.rect) and self != p:
                if isinstance(p, blocks.Platform):
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                    if yvel < 0:
                        self.rect.top = p.rect.bottom

    def update(self, platforms, player):
        self.image.fill(Color(MONSTER_COLOR))
        self.boltAnim.blit(self.image, (0, 0))

        player_x = player.rect.centerx
        player_y = player.rect.centery

        # Определение направления движения к игроку
        if player_x > self.rect.centerx:
            self.xvel = abs(self.xvel)  # Движение вправо
        else:
            self.xvel = -abs(self.xvel)  # Движение влево

        if player_y > self.rect.centery:
            self.yvel = abs(self.yvel)  # Движение вниз
        else:
            self.yvel = -abs(self.yvel)  # Движение вверх

        # Проверка, есть ли прямой путь к игроку по горизонтали
        can_reach_x = True
        if self.xvel > 0:
            for p in platforms:
                if p.rect.collidepoint(self.rect.right + self.xvel, self.rect.centery):
                    can_reach_x = False
                    break
        elif self.xvel < 0:
            for p in platforms:
                if p.rect.collidepoint(self.rect.left + self.xvel, self.rect.centery):
                    can_reach_x = False
                    break

        # Проверка, есть ли прямой путь к игроку по вертикали
        can_reach_y = True
        if self.yvel > 0:
            for p in platforms:
                if p.rect.collidepoint(self.rect.centerx, self.rect.bottom + self.yvel):
                    can_reach_y = False
                    break
        elif self.yvel < 0:
            for p in platforms:
                if p.rect.collidepoint(self.rect.centerx, self.rect.top + self.yvel):
                    can_reach_y = False
                    break

        # Если есть прямой путь, продолжаем двигаться
        if can_reach_x:
            self.rect.x += self.xvel
        if can_reach_y:
            self.rect.y += self.yvel


        # Проверка столкновений с платформами
        self.collide(self.xvel, self.yvel, platforms)

        # Проверка, находится ли монстр достаточно близко к платформе

            # Обновление позиции монстра
        self.rect.y += self.yvel
        self.rect.x += self.xvel

        # Проверка выхода за границы экрана
        if self.rect.left < 0 or self.rect.right > WIN_WIDTH:
            self.xvel = -self.xvel
        if self.rect.top < 0 or self.rect.bottom > WIN_HEIGHT:
            self.yvel = -self.yvel