"""
摄像机系统 - 平滑横向跟随
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_THRESHOLD, LEVEL_WIDTH


class Camera:
    """2D 横向滚动摄像机"""
    def __init__(self):
        self.x = 0
        self.target_x = 0
        self.smoothness = 0.1
        self.shake_intensity = 0
        self.shake_timer = 0

    def follow(self, target_rect):
        """跟随目标（玩家），带平滑插值"""
        target_center = target_rect.centerx
        # 理想位置：让目标在 SCROLL_THRESHOLD 附近
        desired = target_center - SCROLL_THRESHOLD
        self.target_x = desired

        # 平滑移动
        self.x += (self.target_x - self.x) * self.smoothness

        # 限制在关卡范围内
        self.x = max(0, min(self.x, LEVEL_WIDTH - SCREEN_WIDTH))

    def shake(self, intensity=8, duration=200):
        """屏幕震动效果"""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def update(self, dt):
        """更新震动"""
        if self.shake_timer > 0:
            self.shake_timer -= dt * 1000
            if self.shake_timer < 0:
                self.shake_timer = 0
                self.shake_intensity = 0

    def apply(self, rect):
        """将世界坐标转换为屏幕坐标"""
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = pygame.time.get_ticks() % 2 * self.shake_intensity * 2 - self.shake_intensity
            shake_y = (pygame.time.get_ticks() // 3) % 2 * self.shake_intensity * 2 - self.shake_intensity
        return (rect.x - self.x + shake_x, rect.y + shake_y)

    def apply_pos(self, x, y):
        """将世界坐标点转换为屏幕坐标"""
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = pygame.time.get_ticks() % 2 * self.shake_intensity * 2 - self.shake_intensity
            shake_y = (pygame.time.get_ticks() // 3) % 2 * self.shake_intensity * 2 - self.shake_intensity
        return (x - self.x + shake_x, y + shake_y)

    def get_rect(self):
        """获取当前摄像机视野矩形（世界坐标）"""
        return pygame.Rect(self.x, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
