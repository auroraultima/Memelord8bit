import pygame
import random
import math
from assets import WIDTH, HEIGHT, WHITE, CYAN, YELLOW, RED, GREEN, PINK_HEAL, BLUE_BOX, LEATHER, LEATHER_DARK

MEME_TYPES = (
    ("GOOD", "ГОДНОТА", GREEN, 100, 30),
    ("GOOD", "КЛАССИКА", CYAN, 150, 25),
    ("GOLD", "ЗОЛОТОЙ\nФОНД", YELLOW, 300, 12),
    ("BAD", "БАЯН 2012", RED, -25, 18),
    ("BAD", "КРИНЖ", RED, -25, 18),
    ("HEAL", "+КОФЕ\nHP", PINK_HEAL, 25, 7),
)
WEIGHTS = tuple(w for _, _, _, _, w in MEME_TYPES)

def spawn_explosion(particles, cx, cy, color):
    for _ in range(14):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(70.0, 220.0)
        particles.append({
            "x": cx, "y": cy,
            "vx": math.cos(angle) * spd,
            "vy": math.sin(angle) * spd,
            "life": random.uniform(0.25, 0.45),
            "color": color
        })

def draw_player(surface, rect, ox=0, oy=0):
    x, y = int(rect.x + ox), int(rect.y + oy)
    w, h = int(rect.width), int(rect.height)
    pygame.draw.rect(surface, LEATHER_DARK, (x - 10, y + 10, w + 20, h - 10), border_radius=6)
    pygame.draw.rect(surface, LEATHER, (x, y, w, h), border_radius=6)
    pygame.draw.rect(surface, (230, 180, 140), (x + 30, y - 22, 30, 24))
    pygame.draw.rect(surface, (30, 30, 35), (x + 28, y - 26, 34, 8))
    pygame.draw.rect(surface, (30, 30, 35), (x + 30, y - 8, 30, 10))
    pygame.draw.rect(surface, CYAN, (x + 32, y - 16, 10, 6))
    pygame.draw.rect(surface, CYAN, (x + 48, y - 16, 10, 6))
    pygame.draw.rect(surface, (20, 20, 30), (x + 20, y + 18, 50, 32), border_radius=4)
    pygame.draw.rect(surface, CYAN, (x + 22, y + 16, 46, 3))

def draw_start_modal(surface, fonts):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    surface.blit(overlay, (0, 0))

    # Синее RPG-окно по центру
    box_w, box_h = 620, 380
    bx, by = (WIDTH - box_w) // 2, (HEIGHT - box_h) // 2
    pygame.draw.rect(surface, BLUE_BOX, (bx, by, box_w, box_h))
    pygame.draw.rect(surface, WHITE, (bx, by, box_w, box_h), 4)
    pygame.draw.rect(surface, WHITE, (bx + 8, by + 8, box_w - 16, box_h - 16), 2)

    title = fonts["big"].render("MEMELORD: 8-BIT EDITION", True, YELLOW)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, by + 26))

    rules = (
        ("СМЫСЛ ИГРЫ:", WHITE),
        ("* Лови ГОДНОТУ, КЛАССИКУ и ЗОЛОТОЙ ФОНД.", GREEN),
        ("* Избегай БАЯНОВ и КРИНЖА (-25 HP иронии).", RED),
        ("* Лови редкий +КОФЕ для восстановления HP.", PINK_HEAL),
        ("* Бей баяны БАНХАММЕРОМ (+50), но не зацепи свои!", CYAN),
        ("", WHITE),
        ("УПРАВЛЕНИЕ:", YELLOW),
        ("A / D или Стрелки  — двигать кресло", WHITE),
        ("ПРОБЕЛ / ЛКМ       — кинуть банхаммер", WHITE),
        ("M — музыка | ESC — выход", WHITE),
    )

    curr_y = by + 78
    for text, color in rules:
        if text:
            line_surf = fonts["small"].render(text, True, color)
            surface.blit(line_surf, (bx + 32, curr_y))
        curr_y += 23

    # Мигающая подсказка старта
    if (pygame.time.get_ticks() // 450) % 2 == 0:
        prompt = fonts["hud"].render(">> НАЖМИ ПРОБЕЛ ИЛИ КЛИКНИ ДЛЯ СТАРТА <<", True, YELLOW)
        surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, by + box_h - 46))
