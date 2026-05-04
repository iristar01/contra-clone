"""
粒子效果系统
"""
import pygame
import random
from config import *


class Particle(pygame.sprite.Sprite):
    """单个粒子"""
    def __init__(self, x, y, color, speed_range=(1, 5), size_range=(2, 6), lifetime=500):
        super().__init__()
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.spawn_time = pygame.time.get_ticks()
        
        size = random.randint(*size_range)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = random.uniform(0, 360)
        speed = random.uniform(*speed_range)
        self.vx = speed * pygame.math.Vector2(1, 0).rotate(angle).x
        self.vy = speed * pygame.math.Vector2(1, 0).rotate(angle).y
        self.gravity = 0.1
    
    def update(self, dt=1/60):
        """更新粒子"""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            self.kill()
            return
        
        # 更新位置
        self.vy += self.gravity
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # 淡出效果
        alpha = int(255 * (1 - elapsed / self.lifetime))
        if alpha < 0:
            alpha = 0
        self.image.set_alpha(alpha)


class Explosion(pygame.sprite.Sprite):
    """爆炸效果"""
    def __init__(self, x, y, size=30):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size
        self.lifetime = 400
        self.spawn_time = pygame.time.get_ticks()
        
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self, dt=1/60):
        """更新爆炸动画"""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            self.kill()
            return
        
        progress = elapsed / self.lifetime
        current_size = int(self.max_size * (1 - progress * 0.5))
        alpha = int(255 * (1 - progress))
        
        self.image = pygame.Surface((current_size*2, current_size*2), pygame.SRCALPHA)
        
        # 绘制多层爆炸效果
        colors = [COLOR_YELLOW, COLOR_RED, COLOR_WHITE]
        for i, color in enumerate(colors):
            r = current_size - i * 5
            if r > 0:
                pygame.draw.circle(self.image, (*color[:3], alpha), 
                                 (current_size, current_size), r)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def draw(self, surface, camera_x=0):
        """绘制爆炸"""
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class ParticleManager:
    """粒子效果管理器"""
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
    
    def add_particles(self, x, y, color, count=10, speed_range=(1, 5), size_range=(2, 6)):
        """添加粒子效果"""
        for _ in range(count):
            particle = Particle(x, y, color, speed_range, size_range)
            self.particles.add(particle)
    
    def add_explosion(self, x, y, size=30):
        """添加爆炸效果"""
        explosion = Explosion(x, y, size)
        self.explosions.add(explosion)
        # 爆炸时同时产生粒子
        self.add_particles(x, y, COLOR_YELLOW, 15, (2, 8), (3, 8))
        self.add_particles(x, y, COLOR_RED, 10, (1, 5), (2, 5))
    
    def add_hit_effect(self, x, y, color=COLOR_WHITE):
        """添加受击效果"""
        self.add_particles(x, y, color, 8, (1, 4), (2, 5))
    
    def add_muzzle_flash(self, x, y, direction_x):
        """添加枪口火焰"""
        offset = 10 if direction_x > 0 else -10
        self.add_particles(x + offset, y, COLOR_YELLOW, 5, (2, 6), (2, 4))
    
    def update(self, dt=1/60):
        """更新所有效果"""
        self.particles.update(dt)
        self.explosions.update(dt)
    
    def draw(self, surface, camera_x=0):
        """绘制所有效果"""
        for particle in self.particles:
            surface.blit(particle.image, (particle.rect.x - camera_x, particle.rect.y))
        for explosion in self.explosions:
            explosion.draw(surface, camera_x)
    
    def clear(self):
        """清空所有效果"""
        self.particles.empty()
        self.explosions.empty()
