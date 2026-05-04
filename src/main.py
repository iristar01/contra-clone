"""
魂斗罗风格射击游戏 - 主程序
支持键盘 + 触屏虚拟手柄 + JavaScript 桥接输入
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

# 检测是否在浏览器环境（pygbag）
try:
    import platform as _platform
    BROWSER_MODE = True
except ImportError:
    BROWSER_MODE = False


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
        self.virtual_keys = {}
        self._init_virtual_buttons()
        self.mouse_pos = (0, 0)
        self.prev_mouse_down = False

        # ========== JS 触摸状态缓存 ==========
        self.js_touch_available = False
        self._check_js_touch()

    def _check_js_touch(self):
        """检测 JavaScript 触摸是否可用"""
        if not BROWSER_MODE:
            return
        try:
            _ = _platform.window.gameTouchState
            self.js_touch_available = True
            print("JS touch available")
        except Exception:
            self.js_touch_available = False
            print("JS touch not available")

    def _get_js_touch(self):
        """从 JavaScript 读取触摸状态"""
        if not self.js_touch_available:
            return "none", (0, 0)
        try:
            state = str(_platform.window.gameTouchState)
            x = int(_platform.window.gameTouchX)
            y = int(_platform.window.gameTouchY)
            return state, (x, y)
        except Exception:
            return "none", (0, 0)

    def _init_virtual_buttons(self):
        """初始化虚拟按钮配置"""
        r = 40  # 按钮半径（加大方便触摸）
        self.buttons = {
            'left':  {'key': pygame.K_LEFT,  'x': 75,  'y': 520, 'r': r, 'label': '←'},
            'right': {'key': pygame.K_RIGHT, 'x': 175, 'y': 520, 'r': r, 'label': '→'},
            'up':    {'key': pygame.K_UP,    'x': 125, 'y': 460, 'r': r, 'label': '↑'},
            'down':  {'key': pygame.K_DOWN,  'x': 125, 'y': 580, 'r': r, 'label': '↓'},
            'jump':  {'key': pygame.K_SPACE, 'x': 600, 'y': 520, 'r': r + 6, 'label': '跳'},
            'shoot': {'key': pygame.K_j,     'x': 720, 'y': 520, 'r': r + 6, 'label': '射'},
            'start': {'key': pygame.K_RETURN,'x': SCREEN_WIDTH // 2, 'y': 420, 'r': 60, 'label': '开始'},
        }
        for btn in self.buttons.values():
            btn['pressed'] = False

    def _get_keys(self):
        """合并物理键盘 + 虚拟按键"""
        keys = list(pygame.key.get_pressed())
        for k, pressed in self.virtual_keys.items():
            if pressed and 0 <= k < len(keys):
                keys[k] = True
        return keys

    def _check_button_press(self, pos):
        """检测触摸位置是否在按钮内"""
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

        for _ in range(3):
            self.enemy_manager.spawn(self.spawn_points, self.player.rect.centerx)
        self.powerup_manager.spawn(400, SCREEN_HEIGHT - TILE_SIZE - 50, 'spread')

    def handle_events(self):
        """处理输入事件"""
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

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

        keys = self._get_keys()
        if self.state == 'playing' and self.player and self.player.alive:
            if keys[pygame.K_j] or keys[pygame.K_z]:
                self.player.shoot(self.bullet_manager, self.particles)

    def _poll_touch_input(self):
        """轮询触摸/鼠标输入"""
        # 优先使用 JavaScript 触摸（移动端浏览器更可靠）
        js_state, js_pos = self._get_js_touch()

        if js_state != "none":
            # 使用 JavaScript 触摸
            self.mouse_pos = js_pos
            mouse_down = (js_state == "down")
        else:
            # 回退到 pygame.mouse
            mouse_down = pygame.mouse.get_pressed()[0]
            self.mouse_pos = pygame.mouse.get_pos()

        # 菜单/结束画面
        if self.state in ('menu', 'gameover'):
            if mouse_down and not self.prev_mouse_down:
                self.start_game()
            self.prev_mouse_down = mouse_down
            return

        # 游戏画面
        if mouse_down:
            btn_name = self._check_button_press(self.mouse_pos)
            if btn_name:
                btn = self.buttons[btn_name]
                btn['pressed'] = True
                self.virtual_keys[btn['key']] = True
        else:
            for btn in self.buttons.values():
                btn['pressed'] = False
                self.virtual_keys[btn['key']] = False

        self.prev_mouse_down = mouse_down

    def update(self, dt):
        """更新游戏逻辑"""
        self._poll_touch_input()

        if self.state != 'playing':
            return

        keys = self._get_keys()

        if self.player.alive:
            self.player.update(keys, self.level.platforms, self.level.walls, dt)
            self.camera.follow(self.player.rect)
        else:
            if keys[pygame.K_RETURN]:
                self.state = 'gameover'

        self.camera.update(dt)
        self.bullet_manager.update(dt)
        self.enemy_manager.update(
            self.player, self.level.walls, self.level.platforms,
            self.bullet_manager, self.particles, dt
        )
        self.powerup_manager.update(self.player, self.level.platforms, self.level.walls, dt)
        self.enemy_manager.spawn(self.spawn_points, self.player.rect.centerx)
        self.particles.update(dt)
        self._check_collisions()

        if self.score > self.wave * 500:
            self.wave += 1
            self.enemy_manager.spawn_interval = max(1000, ENEMY_SPAWN_INTERVAL - self.wave * 200)

        self.blink_timer += dt * 1000

    def _check_collisions(self):
        """碰撞检测"""
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

        for bullet in self.bullet_manager.get_enemy_bullets():
            if self.player.alive and bullet.rect.colliderect(self.player.rect):
                bullet.kill()
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.camera.shake(8, 200)
                if not self.player.alive:
                    self.particles.add_explosion(self.player.rect.centerx, self.player.rect.centery, 35)
                break

        for enemy in self.enemy_manager.enemies:
            if enemy.alive and self.player.alive and self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.camera.shake(6, 150)
                enemy.vx = -enemy.vx * 2
                enemy.facing_right = not enemy.facing_right
                break

        for hazard in self.level.hazards:
            if self.player.alive and self.player.rect.colliderect(hazard.rect):
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                self.player.vy = -8
                self.player.vx = -5 if self.player.facing_right else 5
                break

        for bullet in self.bullet_manager.bullets:
            if bullet.rect.right < 0 or bullet.rect.left > LEVEL_WIDTH or bullet.rect.top > SCREEN_HEIGHT + 50:
                bullet.kill()

    def _get_enemy_score(self, enemy_type):
        scores = {
            'soldier': 100,
            'runner': 150,
            'sniper': 200,
            'heavy': 300
        }
        return scores.get(enemy_type, 100)

    def _draw_virtual_buttons(self):
        """绘制虚拟手柄按钮"""
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

            alpha = 200 if pressed else 130
            color_base = (50, 50, 70, alpha) if not pressed else (90, 90, 130, alpha)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_base, (r, r), r)
            pygame.draw.circle(surf, (255, 255, 255, 80), (r, r), r, 2)

            if self.ui.font_available:
                font_size = 26 if name in ('jump', 'shoot') else 22
                try:
                    font = pygame.font.SysFont("simhei", font_size, bold=True)
                except:
                    font = pygame.font.Font(None, font_size)
                label = font.render(btn['label'], True, COLOR_WHITE)
                lx = r - label.get_width() // 2
                ly = r - label.get_height() // 2
                surf.blit(label, (lx, ly))
            else:
                # 无字体时画简单箭头
                c = r
                if name == 'up':
                    pygame.draw.polygon(surf, COLOR_WHITE, [(c, c-8), (c-6, c+4), (c+6, c+4)])
                elif name == 'down':
                    pygame.draw.polygon(surf, COLOR_WHITE, [(c, c+8), (c-6, c-4), (c+6, c-4)])
                elif name == 'left':
                    pygame.draw.polygon(surf, COLOR_WHITE, [(c-8, c), (c+4, c-6), (c+4, c+6)])
                elif name == 'right':
                    pygame.draw.polygon(surf, COLOR_WHITE, [(c+8, c), (c-4, c-6), (c-4, c+6)])
                else:
                    pygame.draw.rect(surf, COLOR_WHITE, (c-6, c-2, 12, 4))

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

        self._draw_game()

        if self.state == 'paused':
            self.ui.draw_pause(self.screen)

        self._draw_virtual_buttons()
        pygame.display.flip()

    def _draw_game(self):
        """绘制游戏世界"""
        self.level.draw_background(self.screen, self.camera.x)

        for dec in self.level.decorations:
            if dec.parallax < 1.0:
                dec.draw(self.screen, self.camera.x)

        for tile in self.level.tiles:
            screen_x = tile.rect.x - self.camera.x
            if -TILE_SIZE <= screen_x <= SCREEN_WIDTH:
                self.screen.blit(tile.image, (screen_x, tile.rect.y))

        for dec in self.level.decorations:
            if dec.parallax == 1.0:
                screen_x = dec.rect.x - self.camera.x
                if -100 <= screen_x <= SCREEN_WIDTH:
                    self.screen.blit(dec.image, (screen_x, dec.rect.y))

        self.enemy_manager.draw(self.screen, self.camera.x)
        self.bullet_manager.draw(self.screen, self.camera.x)

        if self.player and self.player.alive:
            self.player.draw(self.screen, self.camera.x)

        self.powerup_manager.draw(self.screen, self.camera.x)
        self.particles.draw(self.screen, self.camera.x)

        if self.player:
            self.ui.draw_hud(self.screen, self.player, self.score, self.wave)

    async def run(self):
        """主循环"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.blink_timer += dt * 1000

            self.handle_events()
            self.update(dt)
            self.draw()

            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
