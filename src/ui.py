"""
UI / HUD 系统
"""
import pygame
from config import *


class UI:
    """游戏用户界面"""
    def __init__(self):
        self.font_available = False
        try:
            pygame.font.init()
            self.font_large = pygame.font.SysFont("simhei", 48, bold=True)
            self.font_medium = pygame.font.SysFont("simhei", 32, bold=True)
            self.font_small = pygame.font.SysFont("simhei", 20)
            self.font_tiny = pygame.font.SysFont("simhei", 14)
            self.font_available = True
        except (NotImplementedError, pygame.error):
            pass

    def _draw_text(self, surface, text, x, y, color=COLOR_WHITE, size='medium', center=True):
        """绘制文字（带降级方案）"""
        if self.font_available:
            font = getattr(self, f'font_{size}', self.font_medium)
            surf = font.render(text, True, color)
            if center:
                x -= surf.get_width() // 2
            surface.blit(surf, (x, y))
            return surf.get_height()
        else:
            # 降级：绘制简单色块表示文字区域
            # 为了在无字体时也能运行，用色块和简单图案代替
            w = len(text) * (12 if size == 'large' else 8 if size == 'medium' else 6)
            h = 16 if size == 'large' else 12 if size == 'medium' else 8
            if center:
                x -= w // 2
            pygame.draw.rect(surface, color, (x, y, w, h))
            return h

    def draw_hud(self, surface, player, score, wave):
        """绘制游戏内 HUD"""
        # 生命值 - 心形图标
        heart_full = self._draw_heart(16, True)
        heart_empty = self._draw_heart(16, False)

        for i in range(player.max_health):
            x = 20 + i * 28
            y = 20
            if i < player.health:
                surface.blit(heart_full, (x, y))
            else:
                surface.blit(heart_empty, (x, y))

        # 分数
        self._draw_text(surface, f"Score: {score}", SCREEN_WIDTH - 20, 20, COLOR_WHITE, 'medium', center=True)

        # 波次
        self._draw_text(surface, f"Wave {wave}", SCREEN_WIDTH - 20, 55, COLOR_YELLOW, 'small', center=True)

        # 武器类型
        weapon_names = {
            'normal': 'Normal',
            'spread': 'Spread',
            'rapid': 'Rapid',
            'laser': 'Laser'
        }
        weapon_color = {
            'normal': COLOR_WHITE,
            'spread': (255, 150, 50),
            'rapid': (50, 200, 255),
            'laser': (255, 50, 200)
        }
        w_name = weapon_names.get(player.weapon_type, 'Normal')
        w_color = weapon_color.get(player.weapon_type, COLOR_WHITE)
        self._draw_text(surface, f"Weapon: {w_name}", 20, 55, w_color, 'small', center=False)

        # 武器升级倒计时条
        if player.weapon_type != 'normal' and player.weapon_timer > 0:
            bar_width = 100
            bar_height = 6
            ratio = max(0, min(1, player.weapon_timer / 10000))
            pygame.draw.rect(surface, (60, 60, 60), (20, 78, bar_width, bar_height))
            pygame.draw.rect(surface, w_color, (20, 78, int(bar_width * ratio), bar_height))

    def _draw_heart(self, size, full):
        """绘制心形"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = COLOR_RED if full else (80, 40, 40)
        # 简化的方形心
        pygame.draw.rect(surf, color, (size//4, size//4, size//2, size//2))
        pygame.draw.circle(surf, color, (size//4, size//4), size//4)
        pygame.draw.circle(surf, color, (size*3//4, size//4), size//4)
        if full:
            pygame.draw.circle(surf, (255, 150, 150), (size//3, size//3), 2)
        return surf

    def draw_title_screen(self, surface, blink=True):
        """绘制开始画面"""
        # 背景渐变
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + ratio * 30)
            g = int(20 + ratio * 20)
            b = int(40 + ratio * 40)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 标题
        self._draw_text(surface, "CONTRA CLONE", SCREEN_WIDTH//2, 150, COLOR_RED, 'large', center=True)

        # 副标题
        self._draw_text(surface, "CONTRA-STYLE SHOOTER", SCREEN_WIDTH//2, 220, COLOR_YELLOW, 'medium', center=True)

        # 操作说明
        controls = [
            "WASD / Arrows = Move",
            "W / Up = Jump / Aim Up",
            "S / Down = Crouch",
            "J / Z = Shoot",
        ]
        for i, text in enumerate(controls):
            self._draw_text(surface, text, SCREEN_WIDTH//2, 320 + i * 30, COLOR_WHITE, 'small', center=True)

        # 闪烁提示
        if blink:
            self._draw_text(surface, "Press ENTER to Start", SCREEN_WIDTH//2, 480, COLOR_GREEN, 'medium', center=True)

        # 装饰士兵
        self._draw_title_soldier(surface, 150, 420, True)
        self._draw_title_soldier(surface, SCREEN_WIDTH - 180, 420, False)

    def draw_game_over(self, surface, score, blink=True):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        self._draw_text(surface, "GAME OVER", SCREEN_WIDTH//2, 200, COLOR_RED, 'large', center=True)
        self._draw_text(surface, f"Final Score: {score}", SCREEN_WIDTH//2, 290, COLOR_YELLOW, 'medium', center=True)

        if blink:
            self._draw_text(surface, "Press ENTER to Restart", SCREEN_WIDTH//2, 380, COLOR_GREEN, 'medium', center=True)

    def draw_pause(self, surface):
        """绘制暂停画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        self._draw_text(surface, "PAUSED", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40, COLOR_WHITE, 'large', center=True)

    def _draw_title_soldier(self, surface, x, y, facing_right):
        """绘制标题画面的装饰士兵"""
        w, h = 32, 48
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        uniform = (0, 80, 160) if facing_right else (180, 40, 40)
        skin = (255, 220, 180)
        pygame.draw.rect(s, uniform, (8, 16, 16, 20))
        pygame.draw.rect(s, skin, (10, 4, 12, 14))
        if facing_right:
            pygame.draw.rect(s, (60, 60, 60), (22, 20, 12, 4))
        else:
            pygame.draw.rect(s, (60, 60, 60), (-2, 20, 12, 4))
        surface.blit(s, (x, y))
