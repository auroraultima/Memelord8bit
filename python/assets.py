import pygame
import math
import array
import os
import sys

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

WIDTH, HEIGHT = 800, 600

# 8-битная палитра
BG_COLOR = (26, 28, 44)
WHITE = (255, 255, 255)
CYAN = (0, 229, 255)
YELLOW = (255, 215, 64)
RED = (255, 59, 48)
GREEN = (105, 240, 174)
PINK_HEAL = (255, 105, 180)
BLUE_BOX = (0, 0, 170)
LEATHER = (123, 63, 29)
LEATHER_DARK = (74, 37, 17)

def make_8bit_sound(freq_start, freq_end, duration_ms, wave="square", volume=4000):
    sample_rate = 22050
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h", (0 for _ in range(n_samples)))
    for i in range(n_samples):
        t = i / n_samples
        freq = freq_start + (freq_end - freq_start) * t
        phase = 2 * math.pi * freq * (i / sample_rate)
        val = (1 if math.sin(phase) >= 0 else -1) if wave == "square" else math.sin(phase)
        buf[i] = int(val * (1.0 - t) * volume)
    return pygame.mixer.Sound(buffer=buf)

def make_tense_seq_sounds():
    # Тревожная минорная басовая линия с полутонами
    freqs = (
        110.00, 110.00, 116.54, 110.00,
        130.81, 123.47, 110.00, 82.41,
        98.00,  98.00,  103.83, 98.00,
        116.54, 110.00, 87.31,  82.41,
    )
    return tuple(make_8bit_sound(f, f * 0.98, 110, wave="square", volume=1450) for f in freqs)

def load_resources():
    sounds = {
        "good": make_8bit_sound(520, 880, 120),
        "gold": make_8bit_sound(660, 1320, 220),
        "heal": make_8bit_sound(440, 1100, 260),
        "bad": make_8bit_sound(220, 75, 250),
        "throw": make_8bit_sound(380, 160, 80, wave="triangle"),
        "ban": make_8bit_sound(180, 540, 140),
        "bgm_notes": make_tense_seq_sounds(),
    }

    fonts = {
        "big": pygame.font.SysFont("dejavusansmono,couriernew,monospace", 32, bold=True),
        "hud": pygame.font.SysFont("dejavusansmono,couriernew,monospace", 19, bold=True),
        "small": pygame.font.SysFont("dejavusansmono,couriernew,monospace", 15, bold=True),
    }

    # Спрайт банхаммера
    hammer_surf = pygame.Surface((34, 34), pygame.SRCALPHA)
    pygame.draw.rect(hammer_surf, (215, 118, 67), (14, 12, 6, 20))
    pygame.draw.rect(hammer_surf, (139, 155, 180), (3, 2, 28, 12))
    pygame.draw.rect(hammer_surf, WHITE, (3, 2, 28, 2))
    pygame.draw.rect(hammer_surf, RED, (5, 6, 24, 4))

    # Сканлайны
    scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(scanlines, (0, 0, 0, 95), (0, y), (WIDTH, y), 1)

    try:
        gameover_img = pygame.image.load(resource_path("gameover.png")).convert()
        gameover_img = pygame.transform.scale(gameover_img, (WIDTH, HEIGHT))
    except FileNotFoundError:
        gameover_img = None

    return sounds, fonts, hammer_surf, scanlines, gameover_img

def create_card_surface(label, color, font):
    lines = label.split("\n")
    rendered = tuple(font.render(line, True, color) for line in lines)
    max_w = max(s.get_width() for s in rendered)
    total_h = sum(s.get_height() for s in rendered) + 2 * (len(rendered) - 1)

    box_w = max(96, max_w + 22)
    box_h = max(34, total_h + 14)

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (15, 15, 25), (0, 0, box_w, box_h), border_radius=4)
    pygame.draw.rect(surf, color, (0, 0, box_w, box_h), 3, border_radius=4)

    curr_y = (box_h - total_h) // 2
    for s in rendered:
        surf.blit(s, s.get_rect(centerx=box_w // 2, top=curr_y))
        curr_y += s.get_height() + 2
    return surf
