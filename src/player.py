"""
玩家角色 - 魂斗罗式操控
"""
import pygame
import math
from config import *
from bullet import BulletManager
from particles import ParticleManager


class Player(pygame.sprite.Sprite):
    """玩家类"""
    def __init__(self, x, y):
        super().__init__()
        self.start_pos = (x, y)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.facing_right = True
        self.crouching = False
        self.jumping = False
        self.on_ground = False

        # 物理
        self.vx = 0
        self.vy = 0
        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = PLAYER_GRAVITY

        # 状态
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.alive = True
        self.invincible = False
        self.invincible_timer = 0
        self.blink_interval = 100

        # 射击
        self.last_shot = 0
        self.fire_rate = PLAYER_FIRE_RATE
        self.weapon_type = 'normal'  # normal, spread, rapid, laser
        self.weapon_timer = 0  # 武器升级倒计时

        # 动画
        self.anim_timer = 0
        self.anim_frame = 0
        self.running = False

    def _draw_player(self):
        """程序化绘制玩家角色（像素士兵风格）"""
        self.image.fill((0, 0, 0, 0))
        w, h = self.width, self.height
        facing = 1 if self.facing_right else -1

        # 身体颜色
        skin = (255, 220, 180)
        uniform = (0, 80, 160)
        uniform_dark = (0, 50, 120)
        belt = (80, 50, 20)
        boots = (60, 40, 20)
        helmet = (0, 60, 120)

        if self.crouching:
            # 蹲下姿态
            # 腿部（蜷缩）
            pygame.draw.rect(self.image, boots, (4, h-12, 10, 12))
            pygame.draw.rect(self.image, boots, (w-14, h-12, 10, 12))
            # 躯干
            pygame.draw.rect(self.image, uniform, (2, h-28, w-4, 18))
            pygame.draw.rect(self.image, belt, (2, h-18, w-4, 4))
            # 头部
            pygame.draw.rect(self.image, skin, (6, h-38, w-12, 12))
            # 头盔
            pygame.draw.rect(self.image, helmet, (4, h-42, w-8, 6))
            # 手臂持枪
            arm_y = h - 30
            pygame.draw.rect(self.image, skin, (w//2 - 2, arm_y, 8, 6))
            # 枪
            gun_x = w - 4 if self.facing_right else 4
            pygame.draw.rect(self.image, (60, 60, 60), (gun_x - 2, arm_y - 2, 14, 6))
            pygame.draw.rect(self.image, (80, 80, 80), (gun_x + 10, arm_y - 1, 4, 4))
        else:
            # 站立/跑动姿态
            # 腿部
            leg_offset = 0
            if self.running and self.on_ground:
                leg_offset = math.sin(pygame.time.get_ticks() / 80) * 4

            # 左腿
            pygame.draw.rect(self.image, boots, (6, h-10, 6, 10))
            pygame.draw.rect(self.image, uniform_dark, (6, h-24, 6, 16))
            # 右腿（带动画）
            pygame.draw.rect(self.image, boots, (w-14 + leg_offset, h-10, 6, 10))
            pygame.draw.rect(self.image, uniform_dark, (w-14 + leg_offset, h-24, 6, 16))

            # 躯干
            pygame.draw.rect(self.image, uniform, (4, h-38, w-8, 18))
            # 肌肉/背心细节
            pygame.draw.rect(self.image, (0, 100, 180), (8, h-36, w-16, 8))
            # 腰带
            pygame.draw.rect(self.image, belt, (4, h-24, w-8, 4))
            # 弹药带
            for i in range(3):
                pygame.draw.circle(self.image, (100, 80, 40), (10 + i*8, h-28), 2)

            # 头部
            head_y = h - 48
            pygame.draw.rect(self.image, skin, (8, head_y, w-16, 14))
            # 头盔
            pygame.draw.rect(self.image, helmet, (6, head_y - 4, w-12, 6))
            pygame.draw.rect(self.image, (0, 40, 80), (6, head_y + 2, w-12, 2))
            # 眼睛
            eye_x = w - 10 if self.facing_right else 10
            pygame.draw.rect(self.image, COLOR_BLACK, (eye_x - 3, head_y + 6, 3, 3))
            # 嘴巴
            mouth_x = w - 12 if self.facing_right else 8
            pygame.draw.rect(self.image, (200, 120, 100), (mouth_x, head_y + 11, 4, 1))

            # 手臂和枪
            arm_y = h - 32
            if self.facing_right:
                pygame.draw.rect(self.image, skin, (w-8, arm_y, 8, 6))
                # 枪
                pygame.draw.rect(self.image, (60, 60, 60), (w-2, arm_y - 2, 14, 6))
                pygame.draw.rect(self.image, (100, 100, 100), (w+8, arm_y - 1, 4, 4))  # 枪口
                pygame.draw.rect(self.image, (80, 80, 80), (w-2, arm_y + 4, 6, 3))  # 弹匣
            else:
                pygame.draw.rect(self.image, skin, (0, arm_y, 8, 6))
                pygame.draw.rect(self.image, (60, 60, 60), (-12, arm_y - 2, 14, 6))
                pygame.draw.rect(self.image, (100, 100, 100), (-14, arm_y - 1, 4, 4))
                pygame.draw.rect(self.image, (80, 80, 80), (-4, arm_y + 4, 6, 3))

        # 无敌闪烁
        if self.invincible and (pygame.time.get_ticks() // self.blink_interval) % 2 == 0:
            # 添加白色覆盖层
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 120))
            self.image.blit(flash, (0, 0))

    def update(self, keys, platforms, walls, dt):
        """更新玩家状态"""
        if not self.alive:
            return

        # 输入处理
        self.vx = 0
        self.running = False
        self.crouching = False

        # 左右移动
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.facing_right = False
            self.running = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.facing_right = True

        # 蹲下
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.on_ground:
            self.crouching = True
            self.vx = 0
            self.running = False

        # 跳跃（Space 或 W/Up 单独按时；W+J 组合是向上射击，不跳跃）
        jump_pressed = keys[pygame.K_SPACE] or (keys[pygame.K_w] or keys[pygame.K_UP])
        shooting_up = (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_j] or keys[pygame.K_z])
        if jump_pressed and self.on_ground and not self.crouching and not shooting_up:
            self.vy = -self.jump_power
            self.jumping = True
            self.on_ground = False

        # 重力
        self.vy += self.gravity
        if self.vy > 15:
            self.vy = 15

        # 水平移动 + 碰撞
        self.rect.x += self.vx
        self._handle_collision(walls, platforms, horizontal=True)

        # 垂直移动 + 碰撞
        self.rect.y += self.vy
        self.on_ground = False
        self._handle_collision(walls, platforms, horizontal=False)

        # 边界限制
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

        # 无敌时间
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > PLAYER_INVINCIBLE_TIME:
                self.invincible = False

        # 武器升级倒计时
        if self.weapon_type != 'normal' and self.weapon_timer > 0:
            self.weapon_timer -= dt * 1000
            if self.weapon_timer <= 0:
                self.weapon_type = 'normal'
                self.weapon_timer = 0

        # 掉落检测
        if self.rect.top > SCREEN_HEIGHT + 100:
            self.take_damage(1)
            self.rect.midbottom = self.start_pos
            self.vy = 0

        self._draw_player()

    def _handle_collision(self, walls, platforms, horizontal):
        """处理碰撞"""
        # 与墙壁碰撞
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if horizontal:
                    if self.vx > 0:
                        self.rect.right = wall.rect.left
                    elif self.vx < 0:
                        self.rect.left = wall.rect.right
                    self.vx = 0
                else:
                    if self.vy > 0:
                        self.rect.bottom = wall.rect.top
                        self.vy = 0
                        self.on_ground = True
                        self.jumping = False
                    elif self.vy < 0:
                        self.rect.top = wall.rect.bottom
                        self.vy = 0

        # 与平台碰撞（只在下落时，且可以跳下）
        if not horizontal and self.vy >= 0:
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    # 检查是从上方落下
                    if self.rect.bottom <= plat.rect.centery + self.vy + 2:
                        self.rect.bottom = plat.rect.top
                        self.vy = 0
                        self.on_ground = True
                        self.jumping = False

    def shoot(self, bullet_manager, particles):
        """射击"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot < self.fire_rate:
            return

        self.last_shot = current_time

        # 确定射击方向
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        elif self.crouching:
            dy = 0  # 蹲下时只能水平射
        else:
            dy = 0

        # 水平方向
        if self.facing_right:
            dx = 1
        else:
            dx = -1

        # 如果按了上键，垂直射击
        if dy != 0:
            dx = 0

        # 枪口位置
        if self.crouching:
            muzzle_x = self.rect.centerx + (14 if self.facing_right else -14)
            muzzle_y = self.rect.centery + 4
        elif dy < 0:
            muzzle_x = self.rect.centerx
            muzzle_y = self.rect.top - 4
        else:
            muzzle_x = self.rect.centerx + (16 if self.facing_right else -16)
            muzzle_y = self.rect.centery - 4

        # 根据武器类型发射
        if self.weapon_type == 'spread':
            # 扇形射击
            angles = [0, -0.3, 0.3] if dy == 0 else [0, -0.2, 0.2]
            for angle in angles:
                ndx = dx * math.cos(angle) - dy * math.sin(angle)
                ndy = dx * math.sin(angle) + dy * math.cos(angle)
                bullet_manager.add_bullet(muzzle_x, muzzle_y, ndx, ndy,
                                         PLAYER_BULLET_SPEED, 1, True, 'spread')
        elif self.weapon_type == 'rapid':
            bullet_manager.add_bullet(muzzle_x, muzzle_y, dx, dy,
                                     PLAYER_BULLET_SPEED * 1.3, 1, True, 'rapid')
        elif self.weapon_type == 'laser':
            bullet_manager.add_bullet(muzzle_x, muzzle_y, dx, dy,
                                     PLAYER_BULLET_SPEED * 1.5, 3, True, 'laser')
        else:
            bullet_manager.add_bullet(muzzle_x, muzzle_y, dx, dy,
                                     PLAYER_BULLET_SPEED, 1, True, 'normal')

        # 枪口火焰
        particles.add_muzzle_flash(muzzle_x, muzzle_y, 1 if dx >= 0 else -1)

    def take_damage(self, damage):
        """受伤"""
        if not self.alive or self.invincible:
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
        else:
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            # 受击击退
            self.vy = -5
            self.vx = -4 if self.facing_right else 4

    def respawn(self):
        """重生"""
        self.alive = True
        self.health = self.max_health
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        self.rect.midbottom = self.start_pos
        self.vx = 0
        self.vy = 0
        self.weapon_type = 'normal'

    def upgrade_weapon(self, weapon_type, duration=10000):
        """升级武器"""
        self.weapon_type = weapon_type
        self.weapon_timer = duration

    def draw(self, surface, camera_x):
        """绘制玩家"""
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
