"""
敌人系统 - 多种敌人类型
"""
import pygame
import random
import math
from config import *


class Enemy(pygame.sprite.Sprite):
    """基础敌人类"""
    def __init__(self, x, y, enemy_type='soldier'):
        super().__init__()
        self.enemy_type = enemy_type
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.facing_right = False

        # 物理
        self.vx = 0
        self.vy = 0
        self.on_ground = False

        # 状态
        self.health = 1
        self.alive = True
        self.death_timer = 0

        # AI
        self.patrol_start = x
        self.patrol_range = 150
        self.detection_range = 300
        self.shoot_range = 250
        self.last_shot = 0
        self.fire_rate = ENEMY_FIRE_RATE + random.randint(-500, 500)
        self.move_speed = ENEMY_SPEED

        # 动画
        self.anim_timer = 0
        self.anim_frame = 0

        # 根据类型设置属性
        self._setup_type()
        self._draw()

    def _setup_type(self):
        """根据类型设置属性"""
        if self.enemy_type == 'soldier':
            self.health = 1
            self.move_speed = ENEMY_SPEED
            self.fire_rate = ENEMY_FIRE_RATE
            self.patrol_range = 150
        elif self.enemy_type == 'heavy':
            self.health = 3
            self.move_speed = ENEMY_SPEED * 0.6
            self.fire_rate = ENEMY_FIRE_RATE * 0.7
            self.patrol_range = 100
            self.width = 40
            self.height = 52
        elif self.enemy_type == 'sniper':
            self.health = 1
            self.move_speed = ENEMY_SPEED * 0.3
            self.fire_rate = ENEMY_FIRE_RATE * 1.5
            self.patrol_range = 60
            self.detection_range = 450
            self.shoot_range = 400
        elif self.enemy_type == 'runner':
            self.health = 1
            self.move_speed = ENEMY_SPEED * 1.8
            self.fire_rate = ENEMY_FIRE_RATE * 1.3
            self.patrol_range = 250

    def _draw(self):
        """绘制敌人"""
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        w, h = self.width, self.height

        if self.enemy_type == 'soldier':
            self._draw_soldier(w, h)
        elif self.enemy_type == 'heavy':
            self._draw_heavy(w, h)
        elif self.enemy_type == 'sniper':
            self._draw_sniper(w, h)
        elif self.enemy_type == 'runner':
            self._draw_runner(w, h)

        # 死亡闪烁
        if not self.alive:
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 180))
            self.image.blit(flash, (0, 0))

    def _draw_soldier(self, w, h):
        """普通士兵"""
        skin = (255, 200, 150)
        uniform = (180, 40, 40)
        uniform_dark = (130, 30, 30)
        boots = (50, 30, 10)

        facing = 1 if self.facing_right else -1

        # 腿
        pygame.draw.rect(self.image, boots, (6, h-10, 6, 10))
        pygame.draw.rect(self.image, boots, (w-12, h-10, 6, 10))
        pygame.draw.rect(self.image, uniform_dark, (6, h-24, 6, 16))
        pygame.draw.rect(self.image, uniform_dark, (w-12, h-24, 6, 16))

        # 躯干
        pygame.draw.rect(self.image, uniform, (4, h-36, w-8, 16))
        # 肩章
        pygame.draw.rect(self.image, (200, 180, 50), (4, h-36, 6, 4))
        pygame.draw.rect(self.image, (200, 180, 50), (w-10, h-36, 6, 4))

        # 头
        pygame.draw.rect(self.image, skin, (8, h-46, w-16, 12))
        # 头盔
        pygame.draw.rect(self.image, (100, 30, 30), (6, h-50, w-12, 6))
        pygame.draw.rect(self.image, (150, 50, 50), (6, h-50, w-12, 2))
        # 眼睛
        eye_x = w-10 if self.facing_right else 8
        pygame.draw.rect(self.image, COLOR_BLACK, (eye_x, h-42, 3, 3))

        # 枪
        arm_y = h - 32
        if self.facing_right:
            pygame.draw.rect(self.image, skin, (w-8, arm_y, 8, 6))
            pygame.draw.rect(self.image, (60, 60, 60), (w-2, arm_y-2, 12, 5))
        else:
            pygame.draw.rect(self.image, skin, (0, arm_y, 8, 6))
            pygame.draw.rect(self.image, (60, 60, 60), (-10, arm_y-2, 12, 5))

    def _draw_heavy(self, w, h):
        """重装士兵（更大更壮）"""
        skin = (255, 200, 150)
        armor = (80, 80, 90)
        armor_light = (110, 110, 120)
        boots = (40, 40, 50)

        # 腿
        pygame.draw.rect(self.image, boots, (6, h-12, 8, 12))
        pygame.draw.rect(self.image, boots, (w-14, h-12, 8, 12))

        # 躯干（装甲）
        pygame.draw.rect(self.image, armor, (2, h-40, w-4, 22))
        pygame.draw.rect(self.image, armor_light, (6, h-38, w-12, 10))
        # 装甲板细节
        pygame.draw.rect(self.image, (60, 60, 70), (8, h-34, 8, 6))
        pygame.draw.rect(self.image, (60, 60, 70), (w-16, h-34, 8, 6))

        # 头
        pygame.draw.rect(self.image, skin, (10, h-50, w-20, 12))
        # 头盔
        pygame.draw.rect(self.image, (60, 60, 70), (8, h-54, w-16, 6))
        pygame.draw.rect(self.image, (40, 40, 50), (8, h-54, w-16, 2))
        # 护目镜
        pygame.draw.rect(self.image, (50, 200, 50), (w//2 - 6, h-48, 12, 4))

        # 重武器
        arm_y = h - 36
        if self.facing_right:
            pygame.draw.rect(self.image, armor_light, (w-10, arm_y, 10, 8))
            pygame.draw.rect(self.image, (50, 50, 50), (w-2, arm_y-4, 16, 8))
            pygame.draw.rect(self.image, (80, 80, 80), (w+10, arm_y-2, 6, 4))
        else:
            pygame.draw.rect(self.image, armor_light, (0, arm_y, 10, 8))
            pygame.draw.rect(self.image, (50, 50, 50), (-14, arm_y-4, 16, 8))
            pygame.draw.rect(self.image, (80, 80, 80), (-16, arm_y-2, 6, 4))

    def _draw_sniper(self, w, h):
        """狙击手（瘦长，带长枪）"""
        skin = (255, 200, 150)
        uniform = (60, 100, 60)
        boots = (30, 50, 30)

        # 腿
        pygame.draw.rect(self.image, boots, (8, h-10, 5, 10))
        pygame.draw.rect(self.image, boots, (w-13, h-10, 5, 10))
        pygame.draw.rect(self.image, uniform, (8, h-24, 5, 16))
        pygame.draw.rect(self.image, uniform, (w-13, h-24, 5, 16))

        # 躯干
        pygame.draw.rect(self.image, uniform, (6, h-38, w-12, 16))
        # 伪装网
        for i in range(3):
            pygame.draw.rect(self.image, (40, 80, 40), (8 + i*8, h-36, 4, 4))

        # 头
        pygame.draw.rect(self.image, skin, (10, h-48, w-20, 12))
        # 贝雷帽
        pygame.draw.rect(self.image, (80, 60, 40), (8, h-52, w-16, 6))
        pygame.draw.rect(self.image, (60, 40, 20), (w-14, h-54, 8, 4))

        # 狙击枪（很长）
        arm_y = h - 32
        if self.facing_right:
            pygame.draw.rect(self.image, skin, (w-8, arm_y, 8, 5))
            pygame.draw.rect(self.image, (40, 40, 30), (w-2, arm_y-3, 22, 5))
            pygame.draw.rect(self.image, (60, 60, 50), (w+18, arm_y-2, 4, 3))
            # 瞄准镜
            pygame.draw.rect(self.image, (100, 100, 120), (w+6, arm_y-7, 8, 4))
        else:
            pygame.draw.rect(self.image, skin, (0, arm_y, 8, 5))
            pygame.draw.rect(self.image, (40, 40, 30), (-20, arm_y-3, 22, 5))
            pygame.draw.rect(self.image, (60, 60, 50), (-22, arm_y-2, 4, 3))
            pygame.draw.rect(self.image, (100, 100, 120), (-12, arm_y-7, 8, 4))

    def _draw_runner(self, w, h):
        """奔跑者（快速，前倾）"""
        skin = (255, 200, 150)
        uniform = (180, 100, 20)
        boots = (80, 50, 10)

        # 腿（奔跑姿态）
        offset = math.sin(pygame.time.get_ticks() / 50) * 3
        pygame.draw.rect(self.image, boots, (6, h-10, 6, 10))
        pygame.draw.rect(self.image, boots, (w-12+offset, h-10, 6, 10))

        # 躯干
        pygame.draw.rect(self.image, uniform, (4, h-36, w-8, 16))
        # 前倾效果通过头部位置体现

        # 头
        head_offset = 2 if self.facing_right else -2
        pygame.draw.rect(self.image, skin, (8+head_offset, h-46, w-16, 12))
        # 头巾
        pygame.draw.rect(self.image, (180, 80, 20), (6+head_offset, h-50, w-12, 6))
        pygame.draw.rect(self.image, (200, 100, 30), (w-12+head_offset, h-50, 8, 6))

        # 短枪
        arm_y = h - 32
        if self.facing_right:
            pygame.draw.rect(self.image, skin, (w-8, arm_y, 8, 6))
            pygame.draw.rect(self.image, (60, 60, 60), (w-2, arm_y-2, 10, 5))
        else:
            pygame.draw.rect(self.image, skin, (0, arm_y, 8, 6))
            pygame.draw.rect(self.image, (60, 60, 60), (-8, arm_y-2, 10, 5))

    def update(self, player, walls, platforms, dt):
        """更新敌人AI"""
        if not self.alive:
            self.death_timer += dt * 1000
            if self.death_timer > 300:
                self.kill()
            return

        # 重力
        self.vy += GRAVITY
        if self.vy > 15:
            self.vy = 15

        # AI 行为
        dist_to_player = abs(player.rect.centerx - self.rect.centerx)
        player_in_range = dist_to_player < self.detection_range
        player_in_shoot = dist_to_player < self.shoot_range
        player_is_right = player.rect.centerx > self.rect.centerx

        if player_in_range and player.alive:
            # 追踪玩家
            if player_is_right:
                self.facing_right = True
                if dist_to_player > 80:
                    self.vx = self.move_speed
                else:
                    self.vx = 0
            else:
                self.facing_right = False
                if dist_to_player > 80:
                    self.vx = -self.move_speed
                else:
                    self.vx = 0
        else:
            # 巡逻
            patrol_dist = self.rect.centerx - self.patrol_start
            if abs(patrol_dist) > self.patrol_range:
                self.facing_right = not self.facing_right
                self.vx = self.move_speed if self.facing_right else -self.move_speed
            else:
                self.vx = self.move_speed if self.facing_right else -self.move_speed

        # 移动 + 碰撞
        self.rect.x += self.vx
        self._handle_collision(walls, platforms, horizontal=True)

        self.rect.y += self.vy
        self.on_ground = False
        self._handle_collision(walls, platforms, horizontal=False)

        # 边界
        if self.rect.left < 0 or self.rect.right > LEVEL_WIDTH:
            self.facing_right = not self.facing_right
            self.vx = -self.vx

        self._draw()

    def _handle_collision(self, walls, platforms, horizontal):
        """处理碰撞"""
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if horizontal:
                    if self.vx > 0:
                        self.rect.right = wall.rect.left
                    elif self.vx < 0:
                        self.rect.left = wall.rect.right
                    self.vx = -self.vx
                    self.facing_right = not self.facing_right
                else:
                    if self.vy > 0:
                        self.rect.bottom = wall.rect.top
                        self.vy = 0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.rect.top = wall.rect.bottom
                        self.vy = 0

        if not horizontal and self.vy >= 0:
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.rect.bottom <= plat.rect.centery + self.vy + 2:
                        self.rect.bottom = plat.rect.top
                        self.vy = 0
                        self.on_ground = True

    def shoot(self, bullet_manager):
        """敌人射击"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot < self.fire_rate:
            return None

        self.last_shot = current_time

        # 计算朝向玩家的方向
        dx = 1 if self.facing_right else -1
        dy = 0

        # 狙击手有一定概率瞄高一些
        if self.enemy_type == 'sniper' and random.random() < 0.3:
            dy = -0.3

        muzzle_x = self.rect.centerx + (14 if self.facing_right else -14)
        muzzle_y = self.rect.centery - 4

        bullet_manager.add_bullet(muzzle_x, muzzle_y, dx, dy,
                                 ENEMY_BULLET_SPEED, 1, False)
        return (muzzle_x, muzzle_y)

    def take_damage(self, damage):
        """受伤"""
        if not self.alive:
            return False

        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.vx = 0
            self.vy = -3
            return True  # 死亡
        return False

    def draw(self, surface, camera_x):
        """绘制敌人"""
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class EnemyManager:
    """敌人管理器"""
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.last_spawn = 0
        self.spawn_interval = ENEMY_SPAWN_INTERVAL
        self.score = 0

    def spawn(self, spawn_points, player_x):
        """在远离玩家的位置生成敌人"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn < self.spawn_interval:
            return

        self.last_spawn = current_time

        # 筛选远离玩家的生成点
        valid_points = [(x, y) for x, y in spawn_points
                       if abs(x - player_x) > 400 and abs(x - player_x) < 1200]

        if not valid_points:
            return

        x, y = random.choice(valid_points)

        # 根据分数/时间生成不同类型
        r = random.random()
        if r < 0.5:
            enemy = Enemy(x, y, 'soldier')
        elif r < 0.75:
            enemy = Enemy(x, y, 'runner')
        elif r < 0.9:
            enemy = Enemy(x, y, 'sniper')
        else:
            enemy = Enemy(x, y, 'heavy')

        self.enemies.add(enemy)

    def update(self, player, walls, platforms, bullet_manager, particles, dt):
        """更新所有敌人"""
        for enemy in self.enemies:
            enemy.update(player, walls, platforms, dt)

            # 射击逻辑
            if enemy.alive and player.alive:
                dist = abs(player.rect.centerx - enemy.rect.centerx)
                if dist < enemy.shoot_range:
                    muzzle = enemy.shoot(bullet_manager)
                    if muzzle:
                        particles.add_muzzle_flash(muzzle[0], muzzle[1],
                                                   1 if enemy.facing_right else -1)

    def draw(self, surface, camera_x):
        """绘制所有敌人"""
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)

    def clear(self):
        """清空敌人"""
        self.enemies.empty()
