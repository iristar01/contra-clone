"""
魂斗罗风格射击游戏 - 主程序
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
            pass  # mixer 不可用，静默跳过

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

        # 闪烁计时（用于UI闪烁效果）
        self.blink_timer = 0

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

        # 持续按键检测
        keys = pygame.key.get_pressed()

        if self.state == 'playing' and self.player and self.player.alive:
            # 射击（J 或 Z）
            if keys[pygame.K_j] or keys[pygame.K_z]:
                self.player.shoot(self.bullet_manager, self.particles)

    def update(self, dt):
        """更新游戏逻辑"""
        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()

        # 更新玩家
        if self.player.alive:
            self.player.update(keys, self.level.platforms, self.level.walls, dt)
            self.camera.follow(self.player.rect)
        else:
            # 玩家死亡，等待重启
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
                        # 概率掉落道具
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
                # 弹开敌人
                enemy.vx = -enemy.vx * 2
                enemy.facing_right = not enemy.facing_right
                break

        # 4. 玩家碰到陷阱
        for hazard in self.level.hazards:
            if self.player.alive and self.player.rect.colliderect(hazard.rect):
                self.player.take_damage(1)
                self.particles.add_hit_effect(self.player.rect.centerx, self.player.rect.centery, COLOR_RED)
                # 弹开
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

    def draw(self):
        """绘制画面"""
        if self.state == 'menu':
            self.ui.draw_title_screen(self.screen, blink=(int(self.blink_timer / 500) % 2 == 0))
            pygame.display.flip()
            return

        if self.state == 'gameover':
            # 先绘制游戏画面
            self._draw_game()
            self.ui.draw_game_over(self.screen, self.score,
                                   blink=(int(self.blink_timer / 500) % 2 == 0))
            pygame.display.flip()
            return

        # 正常游戏绘制
        self._draw_game()

        if self.state == 'paused':
            self.ui.draw_pause(self.screen)

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
            dt = self.clock.tick(FPS) / 1000.0  # 转换为秒
            self.blink_timer += dt * 1000

            self.handle_events()
            self.update(dt)
            self.draw()

            # 让出控制权给浏览器事件循环
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    """异步入口"""
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
