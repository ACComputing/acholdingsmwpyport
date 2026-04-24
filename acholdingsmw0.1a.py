#!/usr/bin/env python3.14
# Ultra Mario World by AC
# Python 3.14 + pygame. Sprites are generated in code.
# Features: goalpost flag, level progression, no external files.

import sys
import pygame

PYTHON_TARGET = (3, 14)
GAME_TITLE = "Ultra Mario World by AC"

WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 1.05
GROUND_Y = 576
TILE = 48
WORLD_NAME = "1-1"
LEVEL_TIME = 300
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
        wanted = ".".join(str(p) for p in PYTHON_TARGET)
        got = ".".join(str(p) for p in sys.version_info[:3])
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
    surface.blit(font.render(text, True, color), pos)

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
            {"r":(224,48,48),"b":(40,96,224),"s":(248,184,120),"h":(112,64,32),
             "w":WHITE,"y":(255,216,64),"n":(104,56,32)}, SPRITE_PIXEL_SCALE)
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
            {"r":(224,48,48),"b":(40,96,224),"s":(248,184,120),"h":(112,64,32),
             "w":WHITE,"y":(255,216,64),"n":(104,56,32)}, SPRITE_PIXEL_SCALE)
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
            {"r":(224,48,48),"b":(40,96,224),"s":(248,184,120),"h":(112,64,32),
             "w":WHITE,"y":(255,216,64),"n":(104,56,32)}, SPRITE_PIXEL_SCALE)
        self.player_climb = make_sprite(
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
                ".bbbbbbbbbbbb...",
                ".nnnnnn..nnnn...",
                ".nnnnnn....nnn..",
                "..nnnn......nn..",
                "................",
                "................",
                "................",
            ),
            {"r":(224,48,48),"b":(40,96,224),"s":(248,184,120),"h":(112,64,32),
             "w":WHITE,"y":(255,216,64),"n":(104,56,32)}, SPRITE_PIXEL_SCALE)
        self.player_slide = make_sprite(
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
                ".bbbbbb..bbbb...",
                "nnnn......nnnn..",
                "................",
                "................",
                "................",
                "................",
                "................",
            ),
            {"r":(224,48,48),"b":(40,96,224),"s":(248,184,120),"h":(112,64,32),
             "w":WHITE,"y":(255,216,64),"n":(104,56,32)}, SPRITE_PIXEL_SCALE)

        self.enemy_walk = make_sprite(
            ("..oooooo..",".oooooooo.","oooooooooo","oowoowoowo","oowoowoowo",
             "oooooooooo",".ooobbooo.","..obbbbo..",".nnn..nnn.","nnn....nnn",
             "..........",".........."),
            {"o":(176,92,48),"w":WHITE,"b":BLACK,"n":(78,44,28)}, 4)
        self.koopa = make_sprite(
            ("...gggg...","..gggggg..",".ggssssg..","gggssssgg.","gggyyyygg.",
             ".gyyyyyy..","..yyyyyy..",".ggrrrrgg.","ggrrrrrrgg",".ggrrrrgg.",
             "..nn..nn..",".nn....nn.",".........."),
            {"g":(48,184,80),"s":(250,236,140),"y":(244,190,78),"r":(226,72,60),"n":(94,58,34)},4)
        self.question = make_sprite(
            ("yyyyyyyyyyyyyyyy","yooooooooooooooy","yoYYYYYYYYYYYYoy","yoYYYmmmmYYYYYoy",
             "yoYYmYYYYmYYYYoy","yoYYYYYYmmYYYYoy","yoYYYYYmmYYYYYoy","yoYYYYmmYYYYYYoy",
             "yoYYYYmmYYYYYYoy","yoYYYYYYYYYYYYoy","yoYYYYmmYYYYYYoy","yoYYYYmmYYYYYYoy",
             "yoYYYYYYYYYYYYoy","yoYYYYYYYYYYYYoy","yooooooooooooooy","yyyyyyyyyyyyyyyy"),
            {"y":(128,72,16),"o":(224,136,32),"Y":(255,216,72),"m":(112,64,16)}, WORLD_PIXEL_SCALE)
        self.brick = make_sprite(
            ("bbbbbbbbbbbbbbbb","boooooooooooooob","bollllllllllllob","bollllllllllllob",
             "bollssllllssllob","bolllssllsslllob","bollllssssllllob","bolllllsslllllob",
             "bolllllsslllllob","bollllssssllllob","bolllssllsslllob","bollssllllssllob",
             "bollllllllllllob","boooooooooooooob","bssssssssssssssb","bbbbbbbbbbbbbbbb"),
            {"b":(112,56,24),"o":(184,88,32),"l":(232,144,56),"s":(136,64,24)}, WORLD_PIXEL_SCALE)
        self.used = make_sprite(
            ("cccccccccccccccc","cddddddddddddddc","cdccccccccccccdc","cdcsssssssssscdc",
             "cdcssccccsscccdc","cdcssccccsscccdc","cdccccccccccccdc","cdccssssssssccdc",
             "cdccssssssssccdc","cdccccccccccccdc","cdcssccccsscccdc","cdcssccccsscccdc",
             "cdccccccccccccdc","cdccccccccccccdc","cddddddddddddddc","cccccccccccccccc"),
            {"c":(136,88,56),"d":(184,128,72),"s":(92,56,36)}, WORLD_PIXEL_SCALE)
        self.pipe_top = make_sprite(
            ("..gggggggggggg..",".gLLLLLLLLLLLLg.","gLllllllllllllLg","gLllGGGGGGGGllLg",
             "gLllGGGGGGGGllLg","gLllllllllllllLg",".gLLLLLLLLLLLLg.","..gggggggggggg..",
             "...gGGGGGGGGg...","...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...",
             "...gGLLLLLLGg...","...gGLLLLLLGg...","...gGGGGGGGGg...","...gggggggggg..."),
            {"g":(16,104,40),"L":(112,232,96),"l":(160,248,128),"G":(40,176,72)}, WORLD_PIXEL_SCALE)
        self.pipe_body = make_sprite(
            ("...gggggggggg...","...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...",
             "...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...",
             "...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...","...gGLLLLLLGg...",
             "...gGLLLLLLGg...","...gGLLLLLLGg...","...gGGGGGGGGg...","...gggggggggg..."),
            {"g":(16,104,40),"L":(112,232,96),"G":(40,176,72)}, WORLD_PIXEL_SCALE)
        self.ground = make_sprite(
            ("gggggggggggggggg","gGGGGGGGGGGGGGGg","gggggggggggggggg","dddddddddddddddd",
             "dDddDddDddDddDdd","ddDddDddDddDddDd","drrrrdrrrrdrrrrd","ddDddDddDddDddDd",
             "dDddDddDddDddDdd","drrrrdrrrrdrrrrd","ddDddDddDddDddDd","dDddDddDddDddDdd",
             "drrrrdrrrrdrrrrd","ddDddDddDddDddDd","dDddDddDddDddDdd","dddddddddddddddd"),
            {"g":(32,144,56),"G":(96,224,88),"d":(176,96,48),"D":(216,128,64),"r":(104,60,36)}, WORLD_PIXEL_SCALE)
        self.cloud = make_sprite(
            ("................","......wwww......","....wwWWWWww....","...wWWWWWWWWw...",
             "..wWWWWWWWWWWw..","wwWWWWWWWWWWWWww","wWWWWWWWWWWWWWWw","wwWWWWWWWWWWWWww",
             "..wWWWWWWWWWWw..","...wwwwwwwwww...","................","................"),
            {"w":(224,248,248),"W":WHITE},4)
        self.hill = make_sprite(
            ("................",".......gg.......","......gGGg......",".....gGGGGg.....",
             "....gGGGGGGg....","...gGGGllGGGg...","..gGGGGllGGGGg..",".gGGGGGGGGGGGGg.",
             "gGGGllGGGGllGGGg","gGGGllGGGGllGGGg","gGGGGGGGGGGGGGGg","gggggggggggggggg"),
            {"g":(40,152,64),"G":(104,216,96),"l":(32,112,56)},10)
        self.bush = make_sprite(
            ("................","....gggg........","..ggGGGGgg......",".gGGGGGGGGg.....",
             "gGGGllGGGGGg....","gGGGllGGGGGGgg..","gGGGGGGllGGGGGg.",".ggGGGGllGGGGGGg",
             "..ggGGGGGGGGGGg.","....gggggggggg..","................","................"),
            {"g":(24,128,48),"G":(80,200,72),"l":(16,92,40)},4)
        self.coin = make_sprite(
            ("..yyyy..",".yYYYYy.","yYYYYYYy","yYYyyYYy","yYYyyYYy","yYYYYYYy",".yYYYYy.","..yyyy.."),
            {"y":(202,132,22),"Y":(255,224,72)}, HUD_PIXEL_SCALE)
        # Goalpost flag parts
        self.flag_pole = make_sprite(
            ("....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb....",
             "....bb...."),
            {"b":(160,160,160)}, 4)
        self.flag_ball = make_sprite(
            ("..gg..",
             ".gggg.",
             "gggggg",
             ".gggg.",
             "..gg.."),
            {"g":(0,255,0)}, 4)
        self.flag_banner = make_sprite(
            ("rrrrrrr",
             "rrrrrrr",
             "rrrrrrr",
             "rrrrrrr",
             "rrrrrrr"),
            {"r":(255,0,0)}, 4)

        # Cache flipped sprites
        self.player_idle_flipped = pygame.transform.flip(self.player_idle, True, False)
        self.player_run_flipped = pygame.transform.flip(self.player_run, True, False)
        self.player_jump_flipped = pygame.transform.flip(self.player_jump, True, False)
        self.player_climb_flipped = pygame.transform.flip(self.player_climb, True, False)
        self.player_slide_flipped = pygame.transform.flip(self.player_slide, True, False)
        self.enemy_walk_flipped = pygame.transform.flip(self.enemy_walk, True, False)
        self.koopa_flipped = pygame.transform.flip(self.koopa, True, False)


class Flag:
    """Goalpost flag at end of level."""
    def __init__(self, x, ground_y):
        self.x = x
        self.base_y = ground_y
        self.pole_height = 6 * TILE  # height of pole from ground up
        self.top_y = ground_y - self.pole_height
        self.flag_y = self.top_y + TILE  # initial flag position
        self.reached = False
        self.slide_progress = 0.0  # 0 to 1 for flag lowering animation
        self.mario_on_pole = False
        # pole rect for collision
        self.rect = pygame.Rect(x + 12, self.top_y, 8, self.pole_height)

    def check_collision(self, mario):
        """Return True if Mario touches the pole."""
        if self.reached:
            return False
        if mario.rect.colliderect(self.rect):
            return True
        return False

    def start_flag_sequence(self, mario):
        """Lock Mario into flag grab state."""
        self.reached = True
        self.mario_on_pole = True
        # Set Mario's state variables for flag sequence
        mario.flag_grabbing = True
        mario.vx = 0
        mario.vy = 0
        # Position Mario at pole
        mario.x = self.x + 4
        mario.y = max(mario.y, self.top_y)
        mario.rect.topleft = (round(mario.x), round(mario.y))
        # Determine points by height
        height_ratio = (self.base_y - mario.rect.bottom) / self.pole_height
        if height_ratio > 0.8:
            mario.flag_points = 5000
        elif height_ratio > 0.5:
            mario.flag_points = 2000
        elif height_ratio > 0.2:
            mario.flag_points = 800
        else:
            mario.flag_points = 100
        mario.coins += mario.flag_points // 100  # bonus coins

    def update(self, mario, dt):
        """Animate flag lowering and Mario sliding."""
        if not self.reached:
            return
        # Progress slide
        if mario.flag_grabbing:
            if self.slide_progress < 1.0:
                self.slide_progress += dt * 1.5  # speed of flag descent
                if self.slide_progress >= 1.0:
                    self.slide_progress = 1.0
                    mario.flag_grabbing = False  # flag fully down, Mario walks off
                    mario.on_ground = True
                    mario.rect.bottom = self.base_y
                    mario.y = self.base_y - mario.rect.height
            # Move flag down
            self.flag_y = self.top_y + (self.pole_height - TILE) * self.slide_progress
            # Move Mario down with flag if still grabbing
            if mario.flag_grabbing:
                mario.y = self.flag_y - mario.rect.height // 2
                mario.rect.y = round(mario.y)
        # After flag done, Mario can move again (handled in Mario class)

    def draw(self, surface, sprites, camera):
        """Draw pole, ball, and flag."""
        pole_x = round(self.x - camera.x)
        # Draw pole
        for i in range(0, self.pole_height, TILE):
            surface.blit(sprites.flag_pole, (pole_x + 4, self.top_y + i))
        # Draw ball on top
        ball = sprites.flag_ball
        surface.blit(ball, (pole_x + 4 - (ball.get_width()-8)//2, self.top_y - ball.get_height()//2))
        # Draw flag banner
        banner = sprites.flag_banner
        banner_width = banner.get_width()
        if self.reached:
            # flag lowered
            flag_draw_y = self.flag_y
        else:
            flag_draw_y = self.top_y + TILE
        surface.blit(banner, (pole_x + 4 + 8, flag_draw_y - banner.get_height()//2))
        # Draw flag pole top ornament maybe not needed


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
        # Flag sequence state
        self.flag_grabbing = False
        self.flag_points = 0

    def update(self, platforms, enemies, flag, dt):
        keys = pygame.key.get_pressed()
        # If flag grabbing, don't process normal movement
        if self.flag_grabbing:
            self.invincible -= dt
            return

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

        # Check flag collision only if not already grabbing
        if not self.flag_grabbing and flag is not None and flag.check_collision(self):
            flag.start_flag_sequence(self)

        # Enemy collision
        for enemy in enemies:
            if enemy.dead or not self.rect.colliderect(enemy.rect):
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
        check_rect = self.rect.inflate(abs(dx)*2, abs(dy)*2)
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
        self.flag_grabbing = False  # reset flag state

    def draw(self, surface, camera):
        if self.invincible > 0 and int(self.invincible * 18) % 2 == 0:
            return
        # Determine sprite based on state
        if self.flag_grabbing:
            # While flag is lowering (slide_progress < 1.0) use climb or slide
            # We'll use player_slide for sliding down, but for simplicity use player_climb when moving down
            # Actually we can just use player_slide when sliding down.
            # But we only have climb and slide; we'll use slide if vy > 0 else idle.
            sprite = self.sprites.player_slide if self.vy >= 0 else self.sprites.player_climb
        elif not self.on_ground:
            sprite = self.sprites.player_jump
        elif abs(self.vx) > 1.2:
            sprite = self.sprites.player_run
        else:
            sprite = self.sprites.player_idle

        if not self.facing_right:
            if sprite == self.sprites.player_idle:
                sprite = self.sprites.player_idle_flipped
            elif sprite == self.sprites.player_run:
                sprite = self.sprites.player_run_flipped
            elif sprite == self.sprites.player_jump:
                sprite = self.sprites.player_jump_flipped
            elif sprite == self.sprites.player_climb:
                sprite = self.sprites.player_climb_flipped
            elif sprite == self.sprites.player_slide:
                sprite = self.sprites.player_slide_flipped

        draw_x = round(self.rect.centerx - camera.x - sprite.get_width()/2)
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
        for block in platforms:
            if block.solid and abs(self.rect.centerx - block.rect.centerx) < TILE*2:
                if self.rect.colliderect(block.rect):
                    self.x -= self.vx
                    self.vx *= -1
                    self.rect.x = round(self.x)
                    break

    def draw(self, surface, camera):
        if self.dead:
            return
        if self.kind == "goomba":
            sprite = self.sprites.enemy_walk_flipped if self.vx > 0 else self.sprites.enemy_walk
        else:
            sprite = self.sprites.koopa_flipped if self.vx > 0 else self.sprites.koopa
        draw_x = round(self.rect.centerx - camera.x - sprite.get_width()/2)
        draw_y = round(self.rect.bottom - sprite.get_height())
        surface.blit(sprite, (draw_x, draw_y))


class BackgroundRenderer:
    def __init__(self, sprites):
        self.sky_surface = self._create_sky()
        self.ground_surface = self._create_ground()
        self.cloud_pos = [(120,96),(500,78),(980,118)]
        self.hill_pos = [(80,GROUND_Y-120),(420,GROUND_Y-120),(760,GROUND_Y-120),(1140,GROUND_Y-120)]
        self.bush_x = [260,660,1080]
        self.sprites = sprites

    def _create_sky(self):
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y/HEIGHT
            col = (int(SKY_BLUE[0]+(SKY_LOW[0]-SKY_BLUE[0])*t),
                   int(SKY_BLUE[1]+(SKY_LOW[1]-SKY_BLUE[1])*t),
                   int(SKY_BLUE[2]+(SKY_LOW[2]-SKY_BLUE[2])*t))
            pygame.draw.line(surf, col, (0,y), (WIDTH,y))
        return surf.convert()

    def _create_ground(self):
        surf = pygame.Surface((TILE, HEIGHT-GROUND_Y+TILE))
        surf.fill(DIRT)
        pygame.draw.rect(surf, DIRT_DARK, (0,0,TILE,TILE),2)
        pygame.draw.rect(surf, GROUND_DARK, (0,0,TILE,8))
        pygame.draw.rect(surf, (216,128,64), (12,10,8,8))
        pygame.draw.rect(surf, (216,128,64), (28,28,12,6))
        return surf.convert()

    def draw(self, surface, camera):
        surface.blit(self.sky_surface, (0,0))
        period = 1300
        for x,y in self.cloud_pos:
            sx = x - (camera.x*0.16)%period
            for off in (0,period):
                surface.blit(self.sprites.cloud, (round(sx+off), y))
        period = 1500
        for x,y in self.hill_pos:
            sx = x - (camera.x*0.30)%period
            for off in (0,period):
                surface.blit(self.sprites.hill, (round(sx+off), y))
        period = 1300
        bh = self.sprites.bush.get_height()
        for x in self.bush_x:
            sx = x - (camera.x*0.42)%period
            for off in (0,period):
                surface.blit(self.sprites.bush, (round(sx+off), GROUND_Y-bh))
        pygame.draw.rect(surface, GROUND_GREEN, (0, GROUND_Y, WIDTH, TILE))
        cam_off = int(camera.x) % TILE
        for x in range(-cam_off, WIDTH+TILE, TILE):
            surface.blit(self.ground_surface, (x, GROUND_Y))


def build_level(level_num):
    """Build level layout based on level number (1-based)."""
    blocks = []
    # Ground blocks (always present)
    ground_blocks = 95
    for i in range(ground_blocks):
        blocks.append(Block(i*TILE, GROUND_Y, "ground"))

    # Different block arrangements per level
    if level_num == 1:
        special = [
            (384,432,"question"),(528,384,"brick"),(576,384,"question"),
            (624,384,"brick"),(864,432,"brick"),(912,432,"brick"),
            (960,432,"question"),(1248,336,"brick"),(1296,336,"question"),
            (1632,432,"brick"),(1680,384,"brick"),(1728,336,"question"),
            (2160,384,"brick"),(2208,384,"brick"),(2256,384,"question"),
            (2832,336,"brick"),(2880,336,"question")
        ]
        pipes = [1152, 1968, 2544, 3408]
    else:
        # Variation for subsequent levels
        special = [
            (400,384,"question"),(500,384,"brick"),(600,384,"question"),
            (800,432,"brick"),(1000,384,"question"),(1200,336,"brick"),
            (1400,432,"brick"),(1600,384,"question"),(1800,336,"brick"),
            (2000,384,"brick"),(2200,336,"question"),(2400,384,"brick"),
            (2600,432,"brick"),(2800,384,"question"),(3000,336,"brick")
        ]
        pipes = [700, 1500, 2300, 3100]

    for x,y,kind in special:
        blocks.append(Block(x, y, kind))
    for x in pipes:
        blocks.append(Block(x, GROUND_Y - TILE, "pipe_body"))
        blocks.append(Block(x, GROUND_Y - TILE*2, "pipe_top"))

    level_width = ground_blocks * TILE
    return blocks, level_width


def get_enemies(level_num, sprites):
    """Return enemy list for a given level."""
    if level_num == 1:
        return [
            Enemy(760, GROUND_Y-48, "goomba", sprites),
            Enemy(1420, GROUND_Y-52, "koopa", sprites),
            Enemy(1900, GROUND_Y-48, "goomba", sprites),
            Enemy(2350, GROUND_Y-52, "koopa", sprites),
            Enemy(3060, GROUND_Y-48, "goomba", sprites),
        ]
    else:
        return [
            Enemy(650, GROUND_Y-48, "goomba", sprites),
            Enemy(900, GROUND_Y-52, "koopa", sprites),
            Enemy(1300, GROUND_Y-48, "goomba", sprites),
            Enemy(1700, GROUND_Y-52, "koopa", sprites),
            Enemy(2100, GROUND_Y-48, "goomba", sprites),
            Enemy(2700, GROUND_Y-52, "koopa", sprites),
        ]


def main():
    require_runtime()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption(GAME_TITLE)
    game_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big = pygame.font.Font(None, 64)

    sprites = SpriteBank()
    background = BackgroundRenderer(sprites)

    level_num = 1
    global WORLD_NAME
    WORLD_NAME = f"1-{level_num}"

    blocks, level_width = build_level(level_num)
    enemies = get_enemies(level_num, sprites)
    flag = Flag(level_width - 3*TILE, GROUND_Y)  # goalpost near end of level

    mario = Mario(sprites)
    camera = Camera()
    level_start = pygame.time.get_ticks()

    running = True
    victory_timer = 0  # timer to transition after flag grabbed

    while running:
        dt = min(clock.tick(FPS)/1000.0, 1/20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Update game logic
        mario.update(blocks, enemies, flag, dt)
        for enemy in enemies:
            enemy.update(blocks)
        if flag is not None:
            flag.update(mario, dt)
        camera.follow(mario.x, level_width)

        # Check if flag sequence finished and Mario can walk off
        if flag is not None and flag.reached and not mario.flag_grabbing:
            # Start victory timer to show score, then next level
            victory_timer += dt
            if victory_timer > 3.0:
                # Move to next level
                level_num += 1
                WORLD_NAME = f"1-{level_num}"
                blocks, level_width = build_level(level_num)
                enemies = get_enemies(level_num, sprites)
                flag = Flag(level_width - 3*TILE, GROUND_Y)  # new flag
                mario.__init__(sprites)  # reset Mario
                camera = Camera()
                level_start = pygame.time.get_ticks()
                victory_timer = 0
        else:
            victory_timer = 0

        # Draw
        background.draw(game_surface, camera)

        cam_left = camera.x - TILE*2
        cam_right = camera.x + WIDTH + TILE*2
        for block in blocks:
            if cam_left <= block.x <= cam_right:
                block.draw(game_surface, sprites, camera)
        for enemy in enemies:
            if cam_left <= enemy.x <= cam_right:
                enemy.draw(game_surface, camera)
        if flag is not None:
            flag.draw(game_surface, sprites, camera)
        mario.draw(game_surface, camera)

        elapsed = (pygame.time.get_ticks() - level_start) / 1000.0
        draw_smw_hud(game_surface, font, sprites, mario, elapsed)

        if mario.lives <= 0:
            draw_text(game_surface, big, "GAME OVER", (WIDTH//2-145, HEIGHT//2-40), (255,80,80))
        elif victory_timer > 0 and not mario.flag_grabbing:
            # Show points gained
            if mario.flag_points > 0:
                pts_text = f"{mario.flag_points} POINTS!"
                draw_text(game_surface, big, pts_text, (WIDTH//2-120, HEIGHT//2-60), (255,255,0))
            draw_text(game_surface, font, "COURSE CLEAR!", (WIDTH//2-90, HEIGHT//2), (255,255,255))

        screen.blit(game_surface, (0,0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()