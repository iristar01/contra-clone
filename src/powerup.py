"""
道具系统 - 武器升级、生命值恢复
"""
import pygame
import random
import math
from config import *


class PowerUp(pygame.sprite.Sprite):
    """道具类"""
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.width = 28
        self.height = 28
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = -3  # 弹出效果
        self.bob_offset = random.uniform(0, 6.28)
        self.lifetime = 8000  # 8秒后消失
        self.spawn_time = pygame.time.get_ticks()
        self._draw()

    def _draw(self):
        """绘制道具"""
        self.image.fill((0, 0, 0, 0))
        w, h = self.width, self.height

        if self.powerup_type == 'spread':
            # 散射枪 - 橙色星形
            color = (255, 150, 50)
            glow = (255, 200, 100)
            pygame.draw.circle(self.image, glow, (w//2, h//2), w//2)
            pygame.draw.circle(self.image, color, (w//2, h//2), w//2 - 2)
            # S 字样
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 8, 12, 4))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 8, 4, 6))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 12, 12, 4))
            pygame.draw.rect(self.image, COLOR_WHITE, (16, 12, 4, 6))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 16, 12, 4))

        elif self.powerup_type == 'rapid':
            # 速射 - 蓝色闪电
            color = (50, 200, 255)
            glow = (100, 230, 255)
            pygame.draw.circle(self.image, glow, (w//2, h//2), w//2)
            pygame.draw.circle(self.image, color, (w//2, h//2), w//2 - 2)
            # R 字样
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 8, 4, 12))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 8, 8, 4))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 12, 8, 4))
            pygame.draw.rect(self.image, COLOR_WHITE, (14, 12, 4, 8))

        elif self.powerup_type == 'laser':
            # 激光 - 紫色菱形
            color = (255, 50, 200)
            glow = (255, 150, 230)
            pygame.draw.circle(self.image, glow, (w//2, h//2), w//2)
            pygame.draw.circle(self.image, color, (w//2, h//2), w//2 - 2)
            # L 字样
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 8, 4, 12))
            pygame.draw.rect(self.image, COLOR_WHITE, (8, 16, 10, 4))

        elif self.powerup_type == 'health':
            # 生命值 - 红色十字
            color = COLOR_RED
            glow = (255, 100, 100)
            pygame.draw.circle(self.image, glow, (w//2, h//2), w//2)
            pygame.draw.circle(self.image, color, (w//2, h//2), w//2 - 2)
            # 十字
            pygame.draw.rect(self.image, COLOR_WHITE, (w//2 - 2, 6, 4, 16))
            pygame.draw.rect(self.image, COLOR_WHITE, (6, h//2 - 2, 16, 4))

        # 边框
        pygame.draw.circle(self.image, COLOR_WHITE, (w//2, h//2), w//2 - 1, 1)

    def update(self, dt, platforms, walls):
        """更新道具"""
        # 重力
        self.vy += GRAVITY * 0.5
        if self.vy > 4:
            self.vy = 4

        self.rect.y += self.vy

        # 与地面碰撞
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.vy > 0:
                    self.rect.bottom = wall.rect.top
                    self.vy = 0

        # 悬浮摆动
        self.bob_offset += dt * 5
        bob_y = int(math.sin(self.bob_offset) * 3)
        self.rect.y += bob_y

        # 检查超时
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

    def draw(self, surface, camera_x):
        """绘制道具"""
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class PowerUpManager:
    """道具管理器"""
    def __init__(self):
        self.powerups = pygame.sprite.Group()

    def spawn(self, x, y, force_type=None):
        """在指定位置生成道具"""
        if force_type:
            ptype = force_type
        else:
            r = random.random()
            if r < 0.4:
                ptype = 'spread'
            elif r < 0.7:
                ptype = 'rapid'
            elif r < 0.9:
                ptype = 'laser'
            else:
                ptype = 'health'

        powerup = PowerUp(x, y, ptype)
        self.powerups.add(powerup)

    def update(self, player, platforms, walls, dt):
        """更新所有道具，检测拾取"""
        for pu in self.powerups:
            pu.update(dt, platforms, walls)

            # 检测玩家拾取
            if player.alive and pu.rect.colliderect(player.rect):
                if pu.powerup_type == 'health':
                    if player.health < player.max_health:
                        player.health = min(player.max_health, player.health + 1)
                        pu.kill()
                else:
                    player.upgrade_weapon(pu.powerup_type)
                    pu.kill()

    def draw(self, surface, camera_x):
        """绘制所有道具"""
        for pu in self.powerups:
            pu.draw(surface, camera_x)

    def clear(self):
        """清空道具"""
        self.powerups.empty()
