"""
魂斗罗风格射击游戏 - 主程序
支持键盘 + 触屏虚拟手柄
"""
import pygame
import random
import sys
import asyncio

from config import *
from camera import Camera
from level import Level
from player import Player
from enemy import Enemy, EnemyManager
from bullet import BulletManager
from particles import ParticleManager
from powerup import PowerUpManager
from ui import UI


class Game:
    """游戏主类"""
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except (NotImplementedError, pygame.error):
            pass

        # 窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("魂斗罗风格射击 - Contra Clone")
        self.clock = pygame.time.Clock()

        # 游戏状态: menu, playing, paused, gameover
        self.state = 'menu'
        self.running = True

        # 子系统
        self.camera = Camera()
        self.level = None
        self.player = None
        self.enemy_manager = None
        self.bullet_manager = None
        self.particles = None
        self.powerup_manager = None
        self.ui = UI()

        # 游戏数据
        self.score = 0
        self.wave = 1
        self.spawn_points = []

        # 闪烁计时
        self.blink_timer = 0

        # ========== 虚拟手柄 ==========
        self.virtual_keys = {}  # pygame.K_xxx -> bool
        self._init_virtual_buttons()
        self.mouse_pos = (0, 0)
        self.prev_mouse_down = False

    def _init_virtual_buttons(self):
        """初始化虚拟按钮配置"""
        r = 36  # 按钮半径
        # 左下角方向键
        self.buttons = {
            'left':  {'key': pygame.K_LEFT,  'x': 70,  'y': 530, 'r': r, 'label': '←'},
            'right': {'key': pygame.K_RIGHT, 'x': 170, 'y': 530, 'r': r, 'label': '→'},
            'up':    {'key': pygame.K_UP,    'x': 120, 'y': 480, 'r': r, 'label': '↑'},
            'down':  {'key': pygame.K_DOWN,  'x': 120, 'y': 580, 'r': r, 'label': '↓'},
            'jump':  {'key': pygame.K_SPACE, 'x': 620, 'y': 530, 'r': r + 4, 'label': '跳'},
            'shoot': {'key': pygame.K_j,     'x': 730, 'y': 530, 'r': r + 4, 'label': '射'},
            'start': {'key': pygame.K_RETURN,'x': SCREEN_WIDTH // 2, 'y': 480, 'r': 50, 'label': '开始'},
        }
        # 预渲染按钮表面
        for name, btn in self.buttons.items():
            btn['pressed'] = False

    def _get_keys(self):
        """合并物理键盘 + 虚拟按键，返回兼容 pygame.key.get_pressed() 的序列"""
        keys = list(pygame.key.get_pressed())
        for k, pressed in self.virtual_keys.items():
            if pressed and 0 <= k < len(keys):
                keys[k] = True
        return keys

    def _check_button_press(self, pos):
        """检测触摸位置是否在某个按钮内"""
        x, y = pos
        for name, btn in self.buttons.items():
            dx = x - btn['x']
            dy = y - btn['y']
            if dx * dx + dy * dy <= btn['r'] * btn['r']:
                return name
        return None

    def start_game(self):
        """开始新游戏"""
        self.level = Level()
        self.player = Player(200, SCREEN_HEIGHT - TILE_SIZE)
        self.enemy_manager = EnemyManager()
        self.bullet_manager = BulletManager()
        self.particles = ParticleManager()
        self.powerup_manager = PowerUpManager()
        self.score = 0
        self.wave = 1
        self.spawn_points = self.level.get_spawn_points()
        self.state = 'playing'

        # 初始生成几个敌人
        for _ in range(3):
            self.enemy_manager.spawn(self.spawn_points, self.player.rect.centerx)
        # 初始生成一个道具
        self.powerup_manager.spawn(400, SCREEN_HEIGHT - TILE_SIZE - 50, 'spread')

    def handle_events(self):
        """处理输入事件（仅处理键盘和退出，触摸用轮询）"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing':
                        self.state = 'paused'
                    elif self.state == 'paused':
                        self.state = 'playing'
                    elif self.state == 'menu':
                        self.running = False

                if event.key == pygame.K_RETURN:
                    if self.state == 'menu':
                        self.start_game()
                    elif self.state == 'gameover':
                        self.start_game()

            # 跟踪鼠标位置（用于轮询）
            if event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION:
                if event.type == pygame.FINGERMOTION:
                    self.mouse_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                else:
                    self.mouse_pos = event.pos

        # 持续按键检测（物理键盘 + 虚拟按键合并）
        keys = self._get_keys()

        if self.state == 'playing' and self.player and self.player.alive:
            if keys[pygame.K_j] or keys[pygame.K_z]:
                self.player.shoot(self.bullet_manager, self.particles)

    def _poll_touch_input(self):
        """轮询鼠标/触摸状态（pygbag 移动端更可靠）"""
        mouse_down = pygame.mouse.get_pressed()[0]
        self.mouse_pos = pygame.mouse.get_pos()

        if self.state in ('menu', 'gameover'):
            # 菜单/结束画面：点击即开始
            if mouse_down and not self.prev_mouse_down:
                self.start_game()
            self.prev_mouse_down = mouse_down
            return

        if self.state == 'playing':
            if mouse_down:
                btn_name = self._check_button_press(self.mouse_pos)
                if btn_name:
                    btn = self.buttons[btn_name]
                    btn['pressed'] = True
                    self.virtual_keys[btn['key']] = True
                # 如果按在非按钮区域，保留之前的按键状态（避免误触）
            else:
                # 松开时清空所有虚拟按键
                for btn in self.buttons.values():
                    btn['pressed'] = False
                    self.virtual_keys[btn['key']] = False

        self.prev_mouse_down = mouse_down

    def update(self, dt):
        """更新游戏逻辑"""
        # 轮询触摸输入（每帧都执行）
        self._poll_touch_input()

        if self.state != 'playing':
            return

        keys = self._get_keys()

        # 更新玩家
        if self.player.alive:
            self.player.update(keys, self.level.platforms, self.level.walls, dt)
            self.camera.follow(self.player.rect)
        else:
            if keys[pygame.K_RETURN]:
                self.state = 'gameover'

        self.camera.update(dt)

        # 更新子弹
        self.bullet_manager.update(dt)

        # 更新敌人
        self.enemy_manager.update(
            self.player, self.level.walls, self.level.platforms,
            self.bullet_manager, self.particles, dt
        )

        # 更新道具
        self.powerup_manager.update(self.player, self.level.platforms, self.level.walls, dt)

        # 敌人生成
        self.enemy_manager.spawn(self.spawn_points, self.player.rect.centerx)

        # 更新粒子
        self.particles.update(dt)

        # 碰撞检测
        self._check_collisions()

        # 波次提升
        if self.score > self.wave * 500:
            self.wave += 1
            self.enemy_manager.spawn_interval = max(1000, ENEMY_SPAWN_INTERVAL - self.wave * 200)

        # 无敌时间闪烁
        self.blink_timer += dt * 1000

    def _check_collisions(self):
        """碰撞检测"""
        # 1. 玩家子弹击中敌人
        for bullet in self.bullet_manager.get_player_bullets():
            for enemy in self.enemy_manager.enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    self.particles.add_hit_effect(enemy.rect.centerx, enemy.rect.centery)
                    died = enemy.take_damage(bullet.damage)
                    if died:
                        self.particles.add_explosion(enemy.rect.centerx, enemy.rect.centery, 25)
                        self.score += self._get_enemy_score(enemy.enemy_type)
                        self.camera.shake(5, 150)
                        if random.random() < 0.15:
                            self.powerup_manager.spawn(enemy.rect.centerx, enemy.rect.centery)
                    break

        # 2. 敌人子弹击中玩家
        for bullet in self.bullet_manager.get_enemy_bullets():
            if self.player.alive and bullet.rect.colliderect(self.player.rect):
                bullet.kill()
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.camera.shake(8, 200)
                if not self.player.alive:
                    self.particles.add_explosion(self.player.rect.centerx, self.player.rect.centery, 35)
                break

        # 3. 玩家与敌人碰撞
        for enemy in self.enemy_manager.enemies:
            if enemy.alive and self.player.alive and self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.camera.shake(6, 150)
                enemy.vx = -enemy.vx * 2
                enemy.facing_right = not enemy.facing_right
                break

        # 4. 玩家碰到陷阱
        for hazard in self.level.hazards:
            if self.player.alive and self.player.rect.colliderect(hazard.rect):
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.player.vy = -8
                self.player.vx = -5 if self.player.facing_right else 5
                break

        # 5. 子弹超出关卡边界
        for bullet in self.bullet_manager.bullets:
            if bullet.rect.right < 0 or bullet.rect.left > LEVEL_WIDTH or bullet.rect.top > SCREEN_HEIGHT + 50:
                bullet.kill()

    def _get_enemy_score(self, enemy_type):
        """获取敌人类型对应的分数"""
        scores = {
            'soldier': 100,
            'runner': 150,
            'sniper': 200,
            'heavy': 300
        }
        return scores.get(enemy_type, 100)

    def _draw_virtual_buttons(self):
        """绘制虚拟手柄按钮"""
        # 只在需要的场景显示对应按钮
        show_dpad = self.state in ('playing', 'paused')
        show_action = self.state in ('playing', 'paused')
        show_start = self.state in ('menu', 'gameover')

        for name, btn in self.buttons.items():
            if name == 'start' and not show_start:
                continue
            if name in ('left', 'right', 'up', 'down') and not show_dpad:
                continue
            if name in ('jump', 'shoot') and not show_action:
                continue

            x, y, r = btn['x'], btn['y'], btn['r']
            pressed = btn['pressed']

            # 按钮底色
            alpha = 180 if pressed else 120
            color_base = (60, 60, 80, alpha) if not pressed else (100, 100, 140, alpha)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_base, (r, r), r)
            pygame.draw.circle(surf, (255, 255, 255, 60), (r, r), r, 2)

            # 按钮文字
            if self.ui.font_available:
                font_size = 24 if name in ('jump', 'shoot') else 20
                try:
                    font = pygame.font.SysFont("simhei", font_size, bold=True)
                except:
                    font = pygame.font.Font(None, font_size)
                label = font.render(btn['label'], True, COLOR_WHITE)
                lx = r - label.get_width() // 2
                ly = r - label.get_height() // 2
                surf.blit(label, (lx, ly))
            else:
                # 无字体时画简单标识
                pygame.draw.rect(surf, COLOR_WHITE, (r - 6, r - 2, 12, 4))
                if name == 'up':
                    pygame.draw.rect(surf, COLOR_WHITE, (r - 2, r - 6, 4, 12))
                elif name == 'down':
                    pygame.draw.rect(surf, COLOR_WHITE, (r - 2, r - 2, 4, 12))
                elif name == 'left':
                    pygame.draw.rect(surf, COLOR_WHITE, (r - 6, r - 2, 12, 4))
                    pygame.draw.rect(surf, COLOR_WHITE, (r - 6, r - 6, 4, 12))
                elif name == 'right':
                    pygame.draw.rect(surf, COLOR_WHITE, (r - 6, r - 2, 12, 4))
                    pygame.draw.rect(surf, COLOR_WHITE, (r + 2, r - 6, 4, 12))

            self.screen.blit(surf, (x - r, y - r))

    def draw(self):
        """绘制画面"""
        if self.state == 'menu':
            self.ui.draw_title_screen(self.screen, blink=(int(self.blink_timer / 500) % 2 == 0))
            self._draw_virtual_buttons()
            pygame.display.flip()
            return

        if self.state == 'gameover':
            self._draw_game()
            self.ui.draw_game_over(self.screen, self.score,
                                   blink=(int(self.blink_timer / 500) % 2 == 0))
            self._draw_virtual_buttons()
            pygame.display.flip()
            return

        # 正常游戏绘制
        self._draw_game()

        if self.state == 'paused':
            self.ui.draw_pause(self.screen)

        self._draw_virtual_buttons()
        pygame.display.flip()

    def _draw_game(self):
        """绘制游戏世界"""
        # 背景
        self.level.draw_background(self.screen, self.camera.x)

        # 装饰物（远景）
        for dec in self.level.decorations:
            if dec.parallax < 1.0:
                dec.draw(self.screen, self.camera.x)

        # 实体瓦片
        for tile in self.level.tiles:
            screen_x = tile.rect.x - self.camera.x
            if -TILE_SIZE <= screen_x <= SCREEN_WIDTH:
                self.screen.blit(tile.image, (screen_x, tile.rect.y))

        # 前景装饰
        for dec in self.level.decorations:
            if dec.parallax == 1.0:
                screen_x = dec.rect.x - self.camera.x
                if -100 <= screen_x <= SCREEN_WIDTH:
                    self.screen.blit(dec.image, (screen_x, dec.rect.y))

        # 敌人
        self.enemy_manager.draw(self.screen, self.camera.x)

        # 子弹
        self.bullet_manager.draw(self.screen, self.camera.x)

        # 玩家
        if self.player and self.player.alive:
            self.player.draw(self.screen, self.camera.x)

        # 道具
        self.powerup_manager.draw(self.screen, self.camera.x)

        # 粒子效果
        self.particles.draw(self.screen, self.camera.x)

        # HUD
        if self.player:
            self.ui.draw_hud(self.screen, self.player, self.score, self.wave)

    async def run(self):
        """主循环（async 以支持浏览器）"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.blink_timer += dt * 1000

            self.handle_events()
            self.update(dt)
            self.draw()

            await asyncio.sleep(0)

        pygame.quit()


async def main():
    """异步入口"""
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
