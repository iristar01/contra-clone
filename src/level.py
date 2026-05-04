"""
关卡系统 - 瓦片地图、平台、装饰
"""
import pygame
import random
from config import *


class Tile(pygame.sprite.Sprite):
    """单个瓦片"""
    def __init__(self, x, y, tile_type, width=TILE_SIZE, height=TILE_SIZE):
        super().__init__()
        self.tile_type = tile_type
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._draw_tile()

    def _draw_tile(self):
        """程序化绘制瓦片美术"""
        w, h = self.width, self.height
        if self.tile_type == 'ground':
            # 泥土层
            pygame.draw.rect(self.image, (101, 67, 33), (0, 0, w, h))
            # 草地顶层
            pygame.draw.rect(self.image, COLOR_GRASS, (0, 0, w, 8))
            # 细节 - 随机小草
            for i in range(3):
                gx = random.randint(2, w-4)
                pygame.draw.line(self.image, (50, 120, 50), (gx, 4), (gx + random.randint(-2,2), -4), 2)
            # 泥土纹理
            for _ in range(5):
                dx = random.randint(2, w-4)
                dy = random.randint(10, h-2)
                pygame.draw.rect(self.image, (80, 50, 20), (dx, dy, 3, 2))

        elif self.tile_type == 'platform':
            # 木质/石质平台
            pygame.draw.rect(self.image, COLOR_PLATFORM, (0, 0, w, h))
            pygame.draw.rect(self.image, (130, 60, 30), (0, 0, w, 4))  # 高光
            pygame.draw.rect(self.image, (100, 50, 20), (0, h-4, w, 4))  # 阴影
            # 木纹
            for _ in range(2):
                lx = random.randint(2, w-2)
                pygame.draw.line(self.image, (140, 70, 35), (lx, 4), (lx, h-4), 1)

        elif self.tile_type == 'wall':
            # 石墙
            pygame.draw.rect(self.image, (120, 120, 120), (0, 0, w, h))
            pygame.draw.rect(self.image, (150, 150, 150), (0, 0, w, h), 1)
            # 石块纹理
            pygame.draw.rect(self.image, (100, 100, 100), (2, 2, w//2-2, h//2-2))
            pygame.draw.rect(self.image, (130, 130, 130), (w//2, h//2, w//2-2, h//2-2))

        elif self.tile_type == 'water':
            # 水面装饰（非实体）
            pygame.draw.rect(self.image, (30, 100, 180, 120), (0, 0, w, h))
            for i in range(3):
                wx = i * 12 + 4
                pygame.draw.ellipse(self.image, (60, 150, 220, 100), (wx, 8, 8, 4))

        elif self.tile_type == 'bridge':
            # 桥板
            pygame.draw.rect(self.image, (160, 120, 80), (0, 0, w, h))
            pygame.draw.rect(self.image, (120, 80, 40), (0, 0, w, 3))
            # 绳索/支撑
            pygame.draw.line(self.image, (80, 50, 20), (2, 0), (2, h), 2)
            pygame.draw.line(self.image, (80, 50, 20), (w-3, 0), (w-3, h), 2)

        elif self.tile_type == 'spike':
            # 尖刺陷阱
            pygame.draw.rect(self.image, (80, 80, 80), (0, h-8, w, 8))
            points = [(0, h-8), (w//2, 0), (w, h-8)]
            pygame.draw.polygon(self.image, COLOR_RED, points)
            pygame.draw.polygon(self.image, (180, 0, 0), points, 1)


class Decoration(pygame.sprite.Sprite):
    """装饰物（无碰撞）"""
    def __init__(self, x, y, dec_type):
        super().__init__()
        self.dec_type = dec_type
        if dec_type == 'tree':
            self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
            # 树干
            pygame.draw.rect(self.image, (101, 67, 33), (24, 40, 12, 40))
            # 树冠（多层）
            pygame.draw.circle(self.image, (20, 100, 20), (30, 35), 22)
            pygame.draw.circle(self.image, (34, 139, 34), (30, 25), 18)
            pygame.draw.circle(self.image, (50, 160, 50), (30, 15), 12)
        elif dec_type == 'bush':
            self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (34, 139, 34), (0, 10, 40, 20))
            pygame.draw.ellipse(self.image, (50, 160, 50), (5, 0, 30, 20))
        elif dec_type == 'rock':
            self.image = pygame.Surface((30, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (120, 120, 120), (0, 4, 30, 20))
            pygame.draw.ellipse(self.image, (150, 150, 150), (2, 0, 26, 16))
        elif dec_type == 'grass':
            self.image = pygame.Surface((20, 16), pygame.SRCALPHA)
            pygame.draw.line(self.image, (50, 140, 50), (4, 16), (2, 4), 2)
            pygame.draw.line(self.image, (60, 160, 60), (10, 16), (10, 0), 2)
            pygame.draw.line(self.image, (50, 140, 50), (16, 16), (18, 6), 2)
        elif dec_type == 'cloud':
            self.image = pygame.Surface((80, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 255, 255, 180), (0, 10, 80, 25))
            pygame.draw.ellipse(self.image, (255, 255, 255, 140), (10, 0, 50, 25))
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.parallax = 0.3 if dec_type == 'cloud' else 1.0

    def draw(self, surface, camera_x):
        """绘制装饰（支持视差）"""
        x = self.rect.x - camera_x * self.parallax
        # 云朵循环滚动
        if self.dec_type == 'cloud':
            x = x % (LEVEL_WIDTH + 200) - 100
        surface.blit(self.image, (x, self.rect.y))


class Level:
    """关卡管理器"""
    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()  # 只有平台（可跳下）
        self.walls = pygame.sprite.Group()      # 实体墙
        self.hazards = pygame.sprite.Group()    # 陷阱
        self.decorations = pygame.sprite.Group()
        self._generate_level()

    def _generate_level(self):
        """程序化生成关卡"""
        # 地面 - 连续的
        ground_y = SCREEN_HEIGHT - TILE_SIZE
        for x in range(0, LEVEL_WIDTH, TILE_SIZE):
            tile = Tile(x, ground_y, 'ground')
            self.tiles.add(tile)
            self.walls.add(tile)

        # 一些平台段（间隙和平台）
        platform_layout = [
            # (start_x, y, width_in_tiles)
            (8, ground_y - 120, 4),
            (16, ground_y - 200, 3),
            (22, ground_y - 120, 5),
            (32, ground_y - 160, 3),
            (40, ground_y - 240, 4),
            (50, ground_y - 140, 6),
            (62, ground_y - 200, 3),
            (70, ground_y - 120, 5),
            (82, ground_y - 180, 4),
        ]

        for start_col, y, width in platform_layout:
            x = start_col * TILE_SIZE
            for i in range(width):
                tile = Tile(x + i * TILE_SIZE, y, 'platform')
                self.tiles.add(tile)
                self.platforms.add(tile)

        # 墙壁/障碍物
        wall_positions = [
            (25, ground_y - TILE_SIZE, 2),   # x_tile, y, height_in_tiles
            (55, ground_y - TILE_SIZE, 3),
            (78, ground_y - TILE_SIZE, 2),
        ]
        for col, base_y, height in wall_positions:
            for h in range(height):
                tile = Tile(col * TILE_SIZE, base_y - h * TILE_SIZE, 'wall')
                self.tiles.add(tile)
                self.walls.add(tile)

        # 尖刺陷阱
        spike_positions = [15, 35, 60, 85]
        for col in spike_positions:
            tile = Tile(col * TILE_SIZE, ground_y - 16, 'spike', TILE_SIZE, 16)
            self.tiles.add(tile)
            self.hazards.add(tile)

        # 装饰物
        dec_layout = [
            # 树木
            (3, ground_y), (12, ground_y), (28, ground_y), (45, ground_y),
            (58, ground_y), (75, ground_y), (88, ground_y), (95, ground_y),
            # 灌木
            (7, ground_y), (20, ground_y), (38, ground_y), (52, ground_y),
            (68, ground_y), (80, ground_y),
            # 石头
            (10, ground_y), (30, ground_y), (48, ground_y), (72, ground_y),
            # 草
            (2, ground_y), (5, ground_y), (14, ground_y), (18, ground_y),
            (24, ground_y), (36, ground_y), (42, ground_y), (56, ground_y),
            (66, ground_y), (74, ground_y), (84, ground_y), (92, ground_y),
        ]
        for x, y in dec_layout:
            if x % 5 == 0:
                dec = Decoration(x, y, 'tree')
            elif x % 3 == 0:
                dec = Decoration(x, y, 'bush')
            elif x % 2 == 0:
                dec = Decoration(x, y, 'rock')
            else:
                dec = Decoration(x, y, 'grass')
            self.decorations.add(dec)

        # 云朵（背景）
        for i in range(20):
            x = random.randint(-100, LEVEL_WIDTH + 200)
            y = random.randint(30, 200)
            cloud = Decoration(x, y, 'cloud')
            self.decorations.add(cloud)

    def get_spawn_points(self):
        """获取敌人生成点"""
        points = []
        for tile in self.platforms:
            points.append((tile.rect.centerx, tile.rect.top - ENEMY_HEIGHT))
        # 地面上也生成一些
        for x in range(400, LEVEL_WIDTH - 200, 300):
            points.append((x, SCREEN_HEIGHT - TILE_SIZE - ENEMY_HEIGHT))
        return points

    def draw_background(self, surface, camera_x):
        """绘制天空背景"""
        # 天空渐变
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(135 - ratio * 60)
            g = int(206 - ratio * 80)
            b = int(235 - ratio * 50)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 远景山脉（视差）
        mountain_color = (60, 80, 100)
        for i in range(-1, 4):
            base_x = i * 400 - int(camera_x * 0.2) % 400
            points = [
                (base_x, SCREEN_HEIGHT),
                (base_x + 100, SCREEN_HEIGHT - 150),
                (base_x + 200, SCREEN_HEIGHT - 220),
                (base_x + 300, SCREEN_HEIGHT - 120),
                (base_x + 400, SCREEN_HEIGHT),
            ]
            pygame.draw.polygon(surface, mountain_color, points)

        # 远景山脉2层
        mountain_color2 = (80, 100, 120)
        for i in range(-1, 4):
            base_x = i * 350 - int(camera_x * 0.4) % 350
            points = [
                (base_x, SCREEN_HEIGHT),
                (base_x + 80, SCREEN_HEIGHT - 100),
                (base_x + 180, SCREEN_HEIGHT - 160),
                (base_x + 260, SCREEN_HEIGHT - 90),
                (base_x + 350, SCREEN_HEIGHT),
            ]
            pygame.draw.polygon(surface, mountain_color2, points)

    def draw(self, surface, camera_x):
        """绘制关卡"""
        # 背景装饰（视差）
        for dec in self.decorations:
            if dec.parallax < 1.0:
                dec.draw(surface, camera_x)

        # 实体瓦片
        for tile in self.tiles:
            screen_x = tile.rect.x - camera_x
            # 只绘制在屏幕内的
            if -TILE_SIZE <= screen_x <= SCREEN_WIDTH:
                surface.blit(tile.image, (screen_x, tile.rect.y))

        # 前景装饰
        for dec in self.decorations:
            if dec.parallax == 1.0:
                screen_x = dec.rect.x - camera_x
                if -100 <= screen_x <= SCREEN_WIDTH:
                    surface.blit(dec.image, (screen_x, dec.rect.y))
