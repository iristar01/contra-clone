"""
子弹系统
"""
import pygame
from config import *


class Bullet(pygame.sprite.Sprite):
    """子弹类"""
    def __init__(self, x, y, direction_x, direction_y, speed, damage, is_player=True, bullet_type='normal'):
        super().__init__()
        self.is_player = is_player
        self.damage = damage
        self.bullet_type = bullet_type
        
        # 创建子弹图像
        if bullet_type == 'laser':
            # 激光是一条长线
            length = 24
            thickness = 4
            self.image = pygame.Surface((length, thickness), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 50, 200), (0, 0, length, thickness))
            pygame.draw.rect(self.image, (255, 200, 255), (2, 1, length-4, thickness-2))
            if direction_x < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            if direction_y != 0 and direction_x == 0:
                self.image = pygame.transform.rotate(self.image, -90 if direction_y < 0 else 90)
        else:
            size = 8 if is_player else 6
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            if bullet_type == 'rapid':
                color = (50, 200, 255)
                pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
                pygame.draw.circle(self.image, COLOR_WHITE, (size//2, size//2), size//4)
            elif bullet_type == 'spread':
                color = (255, 150, 50)
                pygame.draw.polygon(self.image, color, [(0, size//2), (size//2, 0), (size, size//2), (size//2, size)])
            else:
                color = COLOR_BULLET_PLAYER if is_player else COLOR_BULLET_ENEMY
                pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
                # 高光
                pygame.draw.circle(self.image, COLOR_WHITE, (size//3, size//3), size//4)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = direction_x * speed
        self.speed_y = direction_y * speed
        
        # 生存时间（毫秒）
        self.lifetime = 2000
        self.spawn_time = pygame.time.get_ticks()
    
    def update(self, dt=1/60):
        """更新子弹位置"""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 检查生存时间
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
    
    def draw(self, surface, camera_x=0):
        """绘制子弹（考虑摄像机偏移）"""
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class BulletManager:
    """子弹管理器"""
    def __init__(self):
        self.bullets = pygame.sprite.Group()
    
    def add_bullet(self, x, y, direction_x, direction_y, speed, damage, is_player=True, bullet_type='normal'):
        """添加子弹"""
        bullet = Bullet(x, y, direction_x, direction_y, speed, damage, is_player, bullet_type)
        self.bullets.add(bullet)
    
    def update(self, dt=1/60):
        """更新所有子弹"""
        self.bullets.update(dt)
    
    def draw(self, surface, camera_x=0):
        """绘制所有子弹"""
        for bullet in self.bullets:
            bullet.draw(surface, camera_x)
    
    def get_player_bullets(self):
        """获取玩家子弹"""
        return [b for b in self.bullets if b.is_player]
    
    def get_enemy_bullets(self):
        """获取敌人子弹"""
        return [b for b in self.bullets if not b.is_player]
    
    def clear(self):
        """清空所有子弹"""
        self.bullets.empty()
