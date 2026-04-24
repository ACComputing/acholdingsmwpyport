#!/usr/bin/env python3.14
# Ultra Mario World by AC
# Python 3.14 + pygame. Sprites are generated in code.
# Optimized for 60 FPS SNES-like performance

import sys
import pygame
from math import sin, cos


PYTHON_TARGET = (3, 14)
GAME_TITLE = "Ultra Mario World by AC"

WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 1.05
GROUND_Y = 576
TILE = 48
WORLD_NAME = "1-1"
LEVEL_TIME = 300
SMW_FILE_ASSETS = False
WORLD_PIXEL_SCALE = 3
SPRITE_PIXEL_SCALE = 3
HUD_PIXEL_SCALE = 4

SKY_BLUE = (104, 184, 248)
SKY_LOW = (128, 200, 248)
GROUND_GREEN = (64, 200, 80)
GROUND_DARK = (32, 120, 56)
DIRT = (176, 96, 48)
DIRT_DARK = (96, 56, 32)
WHITE = (255, 255, 255)
BLACK = (8, 8, 10)


def require_runtime():
    if sys.version_info < PYTHON_TARGET:
        wanted = ".".join(str(part) for part in PYTHON_TARGET)
        got = ".".join(str(part) for part in sys.version_info[:3])
        raise RuntimeError(f"{GAME_TITLE} requires Python {wanted}+ (got {got}).")


def clamp(value, low, high):
    return max(low, min(high, value))


def make_sprite(pattern, palette, scale=4):
    width = max(len(row) for row in pattern)
    height = len(pattern)
    surface = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, code in enumerate(row):
            if code == ".":
                continue
            color = palette[code]
            pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))
    return surface.convert_alpha()


def draw_text(surface, font, text, pos, color=WHITE, shadow=True):
    x, y = pos
    if shadow:
        shadow_surf = font.render(text, True, BLACK)
        surface.blit(shadow_surf, (x + 2, y + 2))
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, pos)


def draw_smw_hud(surface, font, sprites, mario, elapsed):
    time_left = max(0, LEVEL_TIME - int(elapsed))
    score = mario.coins * 100 + max(0, int(mario.x // 10))

    draw_text(surface, font, "MARIO", (42, 18))
    draw_text(surface, font, f"{score:06d}", (42, 46))

    surface.blit(sprites.coin, (266, 40))
    draw_text(surface, font, f"x{mario.coins:02d}", (308, 46))

    draw_text(surface, font, "WORLD", (538, 18))
    draw_text(surface, font, WORLD_NAME, (566, 46))

    draw_text(surface, font, "TIME", (792, 18))
    draw_text(surface, font, f"{time_left:03d}", (804, 46))

    draw_text(surface, font, "MARIO", (1030, 18))
    draw_text(surface, font, f"x {mario.lives}", (1064, 46))


class SpriteBank:
    def __init__(self):
        # Pre-scale all sprites during initialization
        self._init_player_sprites()
        self._init_enemy_sprites()
        self._init_block_sprites()
        self._init_world_sprites()
        self._init_hud_sprites()
        
        # Cache flipped versions
        self._cache_flipped_sprites()

    def _init_player_sprites(self):
        self.player_idle = make_sprite(
            (
                "................",
                ".....rrrrrr.....",
                "...rrrrrrrrrr...",
                "...hhhhsssh.....",
                "..hshssssshhh...",
                "..hshhsssshhhh..",
                "..hhsssssssh....",
                "....ssssss......",
                "...rrrrrrrr.....",
                "..rrbrrrbrrr....",
                ".rrrbbbbbbrrr...",
                ".wwwbbyybbwww...",
                ".wwbbbbbbbbww...",
                "..bbbbbbbbbb....",
                "..bbbb..bbbb....",
                ".nnnn....nnnn...",
                ".nnnn....nnnn...",
                "................",
                "................",
                "................",
            ),
            {
                "r": (224, 48, 48),
                "b": (40, 96, 224),
                "s": (248, 184, 120),
                "h": (112, 64, 32),
                "w": WHITE,
                "y": (255, 216, 64),
                "n": (104, 56, 32),
            },
            SPRITE_PIXEL_SCALE,
        )
        self.player_run = make_sprite(
            (
                "................",
                ".....rrrrrr.....",
                "...rrrrrrrrrr...",
                "...hhhhsssh.....",
                "..hshssssshhh...",
                "..hshhsssshhhh..",
                "..hhsssssssh....",
                "....ssssss......",
                ".wwrrrrrrrrww...",
                ".wwwbrrrbrwww...",
                "..wwbbbbbbrrr...",
                "...rbbyybbrr....",
                "...bbbbbbbbww...",
                "..bbbbbbbbbw....",
                ".bbbb...bbbb....",
                "nnnn.....bbbb...",
                "nnnn......nnnn..",
                "................",
                "................",
                "................",
            ),
            {
                "r": (224, 48, 48),
                "b": (40, 96, 224),
                "s": (248, 184, 120),
                "h": (112, 64, 32),
                "w": WHITE,
                "y": (255, 216, 64),
                "n": (104, 56, 32),
            },
            SPRITE_PIXEL_SCALE,
        )
        self.player_jump = make_sprite(
            (
                "................",
                ".....rrrrrr.....",
                "...rrrrrrrrrr...",
                "...hhhhsssh.....",
                "..hshssssshhh...",
                "..hshhsssshhhh..",
                "..hhsssssssh....",
                "....ssssss......",
                ".wwrrrrrrrrww...",
                ".wwwrrrrrrwww...",
                "..wwbbbbbbrr....",
                "...bbbbyybb.....",
                "..bbbbbbbbbb....",
                ".bbbb....bbbb...",
                ".nnnn....nnnn...",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
            {
                "r": (224, 48, 48),
                "b": (40, 96, 224),
                "s": (248, 184, 120),
                "h": (112, 64, 32),
                "w": WHITE,
                "y": (255, 216, 64),
                "n": (104, 56, 32),
            },
            SPRITE_PIXEL_SCALE,
        )

    def _init_enemy_sprites(self):
        self.enemy_walk = make_sprite(
            (
                "..oooooo..",
                ".oooooooo.",
                "oooooooooo",
                "oowoowoowo",
                "oowoowoowo",
                "oooooooooo",
                ".ooobbooo.",
                "..obbbbo..",
                ".nnn..nnn.",
                "nnn....nnn",
                "..........",
                "..........",
            ),
            {
                "o": (176, 92, 48),
                "w": WHITE,
                "b": BLACK,
                "n": (78, 44, 28),
            },
            4,
        )
        self.koopa = make_sprite(
            (
                "...gggg...",
                "..gggggg..",
                ".ggssssg..",
                "gggssssgg.",
                "gggyyyygg.",
                ".gyyyyyy..",
                "..yyyyyy..",
                ".ggrrrrgg.",
                "ggrrrrrrgg",
                ".ggrrrrgg.",
                "..nn..nn..",
                ".nn....nn.",
                "..........",
            ),
            {
                "g": (48, 184, 80),
                "s": (250, 236, 140),
                "y": (244, 190, 78),
                "r": (226, 72, 60),
                "n": (94, 58, 34),
            },
            4,
        )

    def _init_block_sprites(self):
        self.question = make_sprite(
            (
                "yyyyyyyyyyyyyyyy",
                "yooooooooooooooy",
                "yoYYYYYYYYYYYYoy",
                "yoYYYmmmmYYYYYoy",
                "yoYYmYYYYmYYYYoy",
                "yoYYYYYYmmYYYYoy",
                "yoYYYYYmmYYYYYoy",
                "yoYYYYmmYYYYYYoy",
                "yoYYYYmmYYYYYYoy",
                "yoYYYYYYYYYYYYoy",
                "yoYYYYmmYYYYYYoy",
                "yoYYYYmmYYYYYYoy",
                "yoYYYYYYYYYYYYoy",
                "yoYYYYYYYYYYYYoy",
                "yooooooooooooooy",
                "yyyyyyyyyyyyyyyy",
            ),
            {
                "y": (128, 72, 16),
                "o": (224, 136, 32),
                "Y": (255, 216, 72),
                "m": (112, 64, 16),
            },
            WORLD_PIXEL_SCALE,
        )
        self.brick = make_sprite(
            (
                "bbbbbbbbbbbbbbbb",
                "boooooooooooooob",
                "bollllllllllllob",
                "bollllllllllllob",
                "bollssllllssllob",
                "bolllssllsslllob",
                "bollllssssllllob",
                "bolllllsslllllob",
                "bolllllsslllllob",
                "bollllssssllllob",
                "bolllssllsslllob",
                "bollssllllssllob",
                "bollllllllllllob",
                "boooooooooooooob",
                "bssssssssssssssb",
                "bbbbbbbbbbbbbbbb",
            ),
            {
                "b": (112, 56, 24),
                "o": (184, 88, 32),
                "l": (232, 144, 56),
                "s": (136, 64, 24),
            },
            WORLD_PIXEL_SCALE,
        )
        self.used = make_sprite(
            (
                "cccccccccccccccc",
                "cddddddddddddddc",
                "cdccccccccccccdc",
                "cdcsssssssssscdc",
                "cdcssccccsscccdc",
                "cdcssccccsscccdc",
                "cdccccccccccccdc",
                "cdccssssssssccdc",
                "cdccssssssssccdc",
                "cdccccccccccccdc",
                "cdcssccccsscccdc",
                "cdcssccccsscccdc",
                "cdccccccccccccdc",
                "cdccccccccccccdc",
                "cddddddddddddddc",
                "cccccccccccccccc",
            ),
            {
                "c": (136, 88, 56),
                "d": (184, 128, 72),
                "s": (92, 56, 36),
            },
            WORLD_PIXEL_SCALE,
        )

    def _init_world_sprites(self):
        self.pipe_top = make_sprite(
            (
                "..gggggggggggg..",
                ".gLLLLLLLLLLLLg.",
                "gLllllllllllllLg",
                "gLllGGGGGGGGllLg",
                "gLllGGGGGGGGllLg",
                "gLllllllllllllLg",
                ".gLLLLLLLLLLLLg.",
                "..gggggggggggg..",
                "...gGGGGGGGGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGGGGGGGGg...",
                "...gggggggggg...",
            ),
            {
                "g": (16, 104, 40),
                "L": (112, 232, 96),
                "l": (160, 248, 128),
                "G": (40, 176, 72),
            },
            WORLD_PIXEL_SCALE,
        )
        self.pipe_body = make_sprite(
            (
                "...gggggggggg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGLLLLLLGg...",
                "...gGGGGGGGGg...",
                "...gggggggggg...",
            ),
            {
                "g": (16, 104, 40),
                "L": (112, 232, 96),
                "G": (40, 176, 72),
            },
            WORLD_PIXEL_SCALE,
        )
        self.ground = make_sprite(
            (
                "gggggggggggggggg",
                "gGGGGGGGGGGGGGGg",
                "gggggggggggggggg",
                "dddddddddddddddd",
                "dDddDddDddDddDdd",
                "ddDddDddDddDddDd",
                "drrrrdrrrrdrrrrd",
                "ddDddDddDddDddDd",
                "dDddDddDddDddDdd",
                "drrrrdrrrrdrrrrd",
                "ddDddDddDddDddDd",
                "dDddDddDddDddDdd",
                "drrrrdrrrrdrrrrd",
                "ddDddDddDddDddDd",
                "dDddDddDddDddDdd",
                "dddddddddddddddd",
            ),
            {
                "g": (32, 144, 56),
                "G": (96, 224, 88),
                "d": (176, 96, 48),
                "D": (216, 128, 64),
                "r": (104, 60, 36),
            },
            WORLD_PIXEL_SCALE,
        )
        self.cloud = make_sprite(
            (
                "................",
                "......wwww......",
                "....wwWWWWww....",
                "...wWWWWWWWWw...",
                "..wWWWWWWWWWWw..",
                "wwWWWWWWWWWWWWww",
                "wWWWWWWWWWWWWWWw",
                "wwWWWWWWWWWWWWww",
                "..wWWWWWWWWWWw..",
                "...wwwwwwwwww...",
                "................",
                "................",
            ),
            {"w": (224, 248, 248), "W": WHITE},
            4,
        )
        self.hill = make_sprite(
            (
                "................",
                ".......gg.......",
                "......gGGg......",
                ".....gGGGGg.....",
                "....gGGGGGGg....",
                "...gGGGllGGGg...",
                "..gGGGGllGGGGg..",
                ".gGGGGGGGGGGGGg.",
                "gGGGllGGGGllGGGg",
                "gGGGllGGGGllGGGg",
                "gGGGGGGGGGGGGGGg",
                "gggggggggggggggg",
            ),
            {
                "g": (40, 152, 64),
                "G": (104, 216, 96),
                "l": (32, 112, 56),
            },
            10,
        )
        self.bush = make_sprite(
            (
                "................",
                "....gggg........",
                "..ggGGGGgg......",
                ".gGGGGGGGGg.....",
                "gGGGllGGGGGg....",
                "gGGGllGGGGGGgg..",
                "gGGGGGGllGGGGGg.",
                ".ggGGGGllGGGGGGg",
                "..ggGGGGGGGGGGg.",
                "....gggggggggg..",
                "................",
                "................",
            ),
            {
                "g": (24, 128, 48),
                "G": (80, 200, 72),
                "l": (16, 92, 40),
            },
            4,
        )

    def _init_hud_sprites(self):
        self.coin = make_sprite(
            (
                "..yyyy..",
                ".yYYYYy.",
                "yYYYYYYy",
                "yYYyyYYy",
                "yYYyyYYy",
                "yYYYYYYy",
                ".yYYYYy.",
                "..yyyy..",
            ),
            {"y": (202, 132, 22), "Y": (255, 224, 72)},
            HUD_PIXEL_SCALE,
        )

    def _cache_flipped_sprites(self):
        """Pre-cache horizontally flipped versions of all directional sprites"""
        self.player_idle_flipped = pygame.transform.flip(self.player_idle, True, False)
        self.player_run_flipped = pygame.transform.flip(self.player_run, True, False)
        self.player_jump_flipped = pygame.transform.flip(self.player_jump, True, False)
        self.enemy_walk_flipped = pygame.transform.flip(self.enemy_walk, True, False)
        self.koopa_flipped = pygame.transform.flip(self.koopa, True, False)


class Camera:
    def __init__(self):
        self.x = 0

    def follow(self, target_x, level_width):
        wanted = target_x - WIDTH * 0.42
        self.x += (wanted - self.x) * 0.12
        self.x = clamp(self.x, 0, max(0, level_width - WIDTH))


class Mario:
    def __init__(self, sprites):
        self.sprites = sprites
        self.x = 150.0
        self.y = GROUND_Y - 64.0
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.on_ground = False
        self.coins = 0
        self.lives = 3
        self.invincible = 0.0
        self.rect = pygame.Rect(self.x, self.y, 48, 64)

    def update(self, platforms, enemies, dt):
        keys = pygame.key.get_pressed()
        move = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        top_speed = 8.5 if run else 6.0

        if move:
            self.vx += move * (0.75 if run else 0.55)
            self.facing_right = move > 0
        else:
            self.vx *= 0.78 if self.on_ground else 0.94
        self.vx = clamp(self.vx, -top_speed, top_speed)

        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        if jump_pressed and self.on_ground:
            self.vy = -18.5 if run else -16.8
            self.on_ground = False

        self.vy = clamp(self.vy + GRAVITY, -22, 18)
        self.move_axis(self.vx, 0, platforms)
        self.move_axis(0, self.vy, platforms)

        if self.y > HEIGHT + 200:
            self.hurt(reset=True)

        # Optimize enemy collision - only check nearby enemies
        for enemy in enemies:
            if enemy.dead:
                continue
            # Quick distance check before rect collision
            if abs(self.rect.centerx - enemy.rect.centerx) > 100:
                continue
            if not self.rect.colliderect(enemy.rect):
                continue
            if self.vy > 1 and self.rect.bottom - enemy.rect.top < 22:
                enemy.dead = True
                self.vy = -11.5
                self.coins += 1
            else:
                self.hurt()

        if self.invincible > 0:
            self.invincible -= dt

    def move_axis(self, dx, dy, platforms):
        self.x += dx
        self.y += dy
        self.rect.topleft = (round(self.x), round(self.y))
        self.on_ground = False if dy else self.on_ground
        
        # Optimize: only check blocks near the player
        check_rect = self.rect.inflate(abs(dx) * 2, abs(dy) * 2)
        
        for block in platforms:
            if not block.solid or not check_rect.colliderect(block.rect):
                continue
            if not self.rect.colliderect(block.rect):
                continue
                
            if dx > 0:
                self.rect.right = block.rect.left
                self.x = self.rect.x
                self.vx = 0
            elif dx < 0:
                self.rect.left = block.rect.right
                self.x = self.rect.x
                self.vx = 0
            elif dy > 0:
                self.rect.bottom = block.rect.top
                self.y = self.rect.y
                self.vy = 0
                self.on_ground = True
            elif dy < 0:
                self.rect.top = block.rect.bottom
                self.y = self.rect.y
                self.vy = 0
                if block.kind == "question" and not block.used:
                    block.used = True
                    self.coins += 1

    def hurt(self, reset=False):
        if self.invincible > 0 and not reset:
            return
        self.lives = max(0, self.lives - 1)
        self.x = 150.0
        self.y = GROUND_Y - 64.0
        self.vx = 0.0
        self.vy = 0.0
        self.invincible = 1.4
        self.rect.topleft = (round(self.x), round(self.y))

    def draw(self, surface, camera):
        if self.invincible > 0 and int(self.invincible * 18) % 2 == 0:
            return
        
        # Use pre-cached flipped sprites
        if not self.on_ground:
            sprite = self.sprites.player_jump if self.facing_right else self.sprites.player_jump_flipped
        elif abs(self.vx) > 1.2:
            sprite = self.sprites.player_run if self.facing_right else self.sprites.player_run_flipped
        else:
            sprite = self.sprites.player_idle if self.facing_right else self.sprites.player_idle_flipped
            
        draw_x = round(self.rect.centerx - camera.x - sprite.get_width() / 2)
        draw_y = round(self.rect.bottom - sprite.get_height())
        surface.blit(sprite, (draw_x, draw_y))


class Block:
    def __init__(self, x, y, kind="brick", solid=True):
        self.x = x
        self.y = y
        self.kind = kind
        self.solid = solid
        self.used = False
        self.rect = pygame.Rect(x, y, TILE, TILE)

    def draw(self, surface, sprites, camera):
        x = round(self.x - camera.x)
        if self.kind == "question" and not self.used:
            surface.blit(sprites.question, (x, self.y))
        elif self.kind == "pipe_top":
            surface.blit(sprites.pipe_top, (x, self.y))
        elif self.kind == "pipe_body":
            surface.blit(sprites.pipe_body, (x, self.y))
        elif self.kind == "ground":
            surface.blit(sprites.ground, (x, self.y))
        elif self.kind == "used":
            surface.blit(sprites.used, (x, self.y))
        else:
            surface.blit(sprites.used if self.used else sprites.brick, (x, self.y))


class Enemy:
    def __init__(self, x, y, kind, sprites):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.sprites = sprites
        self.vx = -1.6 if kind == "goomba" else -2.1
        self.dead = False
        self.rect = pygame.Rect(x, y, 48, 48 if kind == "goomba" else 52)

    def update(self, platforms):
        if self.dead:
            return
        self.x += self.vx
        self.rect.x = round(self.x)
        
        # Quick bounds check for nearby blocks
        for block in platforms:
            if block.solid and abs(self.rect.centerx - block.rect.centerx) < TILE * 2:
                if self.rect.colliderect(block.rect):
                    self.x -= self.vx
                    self.vx *= -1
                    self.rect.x = round(self.x)
                    break

    def draw(self, surface, camera):
        if self.dead:
            return
        # Use pre-cached sprites
        if self.kind == "goomba":
            sprite = self.sprites.enemy_walk_flipped if self.vx > 0 else self.sprites.enemy_walk
        else:
            sprite = self.sprites.koopa_flipped if self.vx > 0 else self.sprites.koopa
            
        draw_x = round(self.rect.centerx - camera.x - sprite.get_width() / 2)
        draw_y = round(self.rect.bottom - sprite.get_height())
        surface.blit(sprite, (draw_x, draw_y))


def build_level():
    blocks = []
    # Pre-allocate list for better performance
    blocks = [None] * 95  # Ground blocks
    
    for i in range(95):
        blocks[i] = Block(i * TILE, GROUND_Y, "ground")

    # Special blocks
    special_blocks = [
        (384, 432, "question"), (528, 384, "brick"), (576, 384, "question"),
        (624, 384, "brick"), (864, 432, "brick"), (912, 432, "brick"),
        (960, 432, "question"), (1248, 336, "brick"), (1296, 336, "question"),
        (1632, 432, "brick"), (1680, 384, "brick"), (1728, 336, "question"),
        (2160, 384, "brick"), (2208, 384, "brick"), (2256, 384, "question"),
        (2832, 336, "brick"), (2880, 336, "question"),
    ]
    
    for x, y, kind in special_blocks:
        blocks.append(Block(x, y, kind))

    # Pipe pairs
    for x in (1152, 1968, 2544, 3408):
        blocks.append(Block(x, GROUND_Y - TILE, "pipe_body"))
        blocks.append(Block(x, GROUND_Y - TILE * 2, "pipe_top"))

    level_width = 95 * TILE
    return blocks, level_width


class BackgroundRenderer:
    """Pre-renders static background elements for performance"""
    
    def __init__(self, sprites):
        self.sky_surface = self._create_sky_surface()
        self.ground_surface = self._create_ground_surface()
        self.cloud_positions = [(120, 96), (500, 78), (980, 118)]
        self.hill_positions = [
            (80, GROUND_Y - 120), (420, GROUND_Y - 120),
            (760, GROUND_Y - 120), (1140, GROUND_Y - 120)
        ]
        self.bush_x_positions = [260, 660, 1080]
        self.sprites = sprites
        
    def _create_sky_surface(self):
        """Pre-render the sky gradient"""
        surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (
                int(SKY_BLUE[0] + (SKY_LOW[0] - SKY_BLUE[0]) * t),
                int(SKY_BLUE[1] + (SKY_LOW[1] - SKY_BLUE[1]) * t),
                int(SKY_BLUE[2] + (SKY_LOW[2] - SKY_BLUE[2]) * t),
            )
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))
        return surface.convert()
        
    def _create_ground_surface(self):
        """Pre-render the underground area"""
        surface = pygame.Surface((TILE, HEIGHT - GROUND_Y + TILE))
        surface.fill(DIRT)
        # Add dirt details
        pygame.draw.rect(surface, DIRT_DARK, (0, 0, TILE, TILE), 2)
        pygame.draw.rect(surface, GROUND_DARK, (0, 0, TILE, 8))
        pygame.draw.rect(surface, (216, 128, 64), (12, 10, 8, 8))
        pygame.draw.rect(surface, (216, 128, 64), (28, 28, 12, 6))
        return surface.convert()
        
    def draw(self, surface, camera):
        # Draw pre-rendered sky
        surface.blit(self.sky_surface, (0, 0))
        
        # Draw clouds with parallax
        cloud_period = 1300
        for x, y in self.cloud_positions:
            sx = x - (camera.x * 0.16) % cloud_period
            for offset in (0, cloud_period):
                surface.blit(self.sprites.cloud, (round(sx + offset), y))
        
        # Draw hills with parallax
        hill_period = 1500
        for x, y in self.hill_positions:
            sx = x - (camera.x * 0.30) % hill_period
            for offset in (0, hill_period):
                surface.blit(self.sprites.hill, (round(sx + offset), y))
        
        # Draw bushes with parallax
        bush_period = 1300
        bush_h = self.sprites.bush.get_height()
        for x in self.bush_x_positions:
            sx = x - (camera.x * 0.42) % bush_period
            for offset in (0, bush_period):
                surface.blit(self.sprites.bush, (round(sx + offset), GROUND_Y - bush_h))
        
        # Draw ground top
        pygame.draw.rect(surface, GROUND_GREEN, (0, GROUND_Y, WIDTH, TILE))
        
        # Draw underground efficiently
        cam_offset = int(camera.x) % TILE
        for x in range(-cam_offset, WIDTH + TILE, TILE):
            surface.blit(self.ground_surface, (x, GROUND_Y))


def main():
    require_runtime()
    pygame.init()
    
    # Set up display with hardware acceleration if available
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption(GAME_TITLE)
    
    # Use a display surface with per-pixel alpha for better performance
    game_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big = pygame.font.Font(None, 64)

    sprites = SpriteBank()
    background = BackgroundRenderer(sprites)
    blocks, level_width = build_level()
    
    enemies = [
        Enemy(760, GROUND_Y - 48, "goomba", sprites),
        Enemy(1420, GROUND_Y - 52, "koopa", sprites),
        Enemy(1900, GROUND_Y - 48, "goomba", sprites),
        Enemy(2350, GROUND_Y - 52, "koopa", sprites),
        Enemy(3060, GROUND_Y - 48, "goomba", sprites),
    ]
    
    mario = Mario(sprites)
    camera = Camera()
    level_start = pygame.time.get_ticks()

    # Pre-calculate visible range buffer
    visible_buffer = TILE * 2

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 1 / 20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Update game logic
        mario.update(blocks, enemies, dt)
        for enemy in enemies:
            enemy.update(blocks)
        camera.follow(mario.x, level_width)

        # Draw everything
        background.draw(game_surface, camera)
        
        # Calculate visible range
        cam_left = camera.x - visible_buffer
        cam_right = camera.x + WIDTH + visible_buffer
        
        # Draw visible blocks
        for block in blocks:
            if cam_left <= block.x <= cam_right:
                block.draw(game_surface, sprites, camera)
        
        # Draw visible enemies
        for enemy in enemies:
            if cam_left <= enemy.x <= cam_right:
                enemy.draw(game_surface, camera)
        
        mario.draw(game_surface, camera)

        # Draw HUD
        elapsed = (pygame.time.get_ticks() - level_start) / 1000.0
        draw_smw_hud(game_surface, font, sprites, mario, elapsed)
        
        if mario.lives <= 0:
            draw_text(game_surface, big, "GAME OVER", (WIDTH // 2 - 145, HEIGHT // 2 - 40), (255, 80, 80))

        # Blit everything to screen at once
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()