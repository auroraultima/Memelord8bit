import pygame
import random
import sys
from assets import (
    WIDTH, HEIGHT, BG_COLOR, WHITE, CYAN, RED, BLUE_BOX,
    load_resources, create_card_surface
)
from entities import MEME_TYPES, WEIGHTS, spawn_explosion, draw_player, draw_start_modal
from leaderboard import (
    load_records, qualifies_for_top, add_record,
    draw_name_input_modal, draw_gameover_leaderboard
)

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MEMELORD: 8-BIT EDITION (pygame-ce)")
clock = pygame.time.Clock()

sounds, fonts, hammer_surf, scanlines, gameover_img = load_resources()

music_on = True
bgm_timer = 0.0
bgm_step = 0

records = load_records()
best_score = next(iter(records))["score"] if records else 0

player_rect = pygame.FRect(WIDTH // 2 - 45, HEIGHT - 130, 90, 70)
player_speed = 520.0

items, hammers, particles = [], [], []
spawn_timer = 0.0
shoot_cooldown = 0.0
score = 0
hp = 100
shake_timer = 0.0
status_text = "* Ожидание запуска сессии..."
game_started = False
game_over = False
entering_name = False
player_name_input = ""

def start_new_game():
    global score, hp, game_started, game_over, entering_name, status_text, bgm_step, bgm_timer
    score, hp = 0, 100
    bgm_step, bgm_timer = 0, 0.0
    game_started = True
    game_over = False
    entering_name = False
    items.clear()
    hammers.clear()
    particles.clear()
    status_text = "* Сессия началась! Лови годноту, бань баяны!"

def throw_banhammer():
    global shoot_cooldown
    if shoot_cooldown > 0 or game_over or not game_started:
        return
    shoot_cooldown = 0.35
    hammers.append({"x": player_rect.centerx, "y": player_rect.top - 20, "speed": 620.0, "angle": 0.0})
    sounds["throw"].play()

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if entering_name:
                if event.key == pygame.K_RETURN:
                    records = add_record(player_name_input, score)
                    if records:
                        best_score = next(iter(records))["score"]
                    entering_name = False
                    sounds["gold"].play()
                elif event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                elif len(player_name_input) < 10 and event.unicode.isprintable():
                    player_name_input += event.unicode.upper()
            else:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m:
                    music_on = not music_on
                elif not game_started and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    start_new_game()
                elif game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    start_new_game()
                elif game_started and not game_over and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    throw_banhammer()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not entering_name:
            if not game_started or game_over:
                start_new_game()
            else:
                throw_banhammer()

    if music_on and not game_over:
        bgm_timer += dt
        if not game_started:
            step_interval = 0.28
        else:
            danger_boost = 0.03 if hp <= 25 else 0.0
            step_interval = max(0.10, 0.24 - (score / 25000.0) - danger_boost)

        if bgm_timer >= step_interval:
            bgm_timer = 0.0
            notes = sounds["bgm_notes"]
            notes[bgm_step].play()
            bgm_step = (bgm_step + 1) % len(notes)

    keys = pygame.key.get_pressed()
    if game_started and not game_over:
        if shoot_cooldown > 0:
            shoot_cooldown -= dt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += player_speed * dt
        player_rect.clamp_ip(pygame.FRect(20, 0, WIDTH - 40, HEIGHT))

        spawn_timer += dt
        if spawn_timer >= max(0.35, 0.85 - (score / 12000)):
            spawn_timer = 0.0
            m_type, label, color, pts, _ = next(iter(random.choices(MEME_TYPES, weights=WEIGHTS, k=1)))
            card_surf = create_card_surface(label, color, fonts["small"])
            bw, bh = card_surf.get_size()
            ix = random.randint(40, WIDTH - bw - 40)
            speed = random.uniform(220.0, 350.0) + (95.0 if m_type in ("GOLD", "HEAL") else 0.0) + score * 0.04
            items.append({
                "rect": pygame.FRect(ix, 65, bw, bh), "surf": card_surf,
                "type": m_type, "color": color, "clean_label": label.replace("\n", " "),
                "pts": pts, "speed": speed
            })

        for h in tuple(hammers):
            h["y"] -= h["speed"] * dt
            h["angle"] = (h["angle"] + 720.0 * dt) % 360
            h_rect = pygame.FRect(h["x"] - 14, h["y"] - 14, 28, 28)
            hit = False
            for item in tuple(items):
                if h_rect.colliderect(item["rect"]):
                    hit = True
                    spawn_explosion(particles, item["rect"].centerx, item["rect"].centery, item["color"])
                    if item["type"] == "BAD":
                        score += 50
                        sounds["ban"].play()
                        status_text = f"* БАНХАММЕР! {item['clean_label']} в бане (+50)!"
                    elif item["type"] == "HEAL":
                        sounds["bad"].play()
                        status_text = "* Ой! Разбил кофе молотком! Обидно..."
                    else:
                        penalty = item["pts"] // 2
                        score = max(0, score - penalty)
                        sounds["bad"].play()
                        status_text = f"* МИССКЛИК! Сбил {item['clean_label']} (-{penalty} очков)!"
                    items.remove(item)
                    break
            if hit or h["y"] < 60:
                hammers.remove(h)

        hitbox = player_rect.inflate(10, 20)
        for item in tuple(items):
            item["rect"].y += item["speed"] * dt
            if hitbox.colliderect(item["rect"]):
                if item["type"] == "BAD":
                    hp += item["pts"]
                    shake_timer = 0.25
                    sounds["bad"].play()
                    status_text = f"* ОЙ! Попался {item['clean_label']}!"
                    if hp <= 0:
                        hp, game_over = 0, True
                        if qualifies_for_top(score):
                            entering_name = True
                elif item["type"] == "HEAL":
                    old_hp = hp
                    hp = min(100, hp + item["pts"])
                    sounds["heal"].play()
                    if hp > old_hp:
                        status_text = f"* Глоток кофе! +{hp - old_hp} HP иронии!"
                    else:
                        score += 100
                        status_text = "* Максимум HP! +100 бонусных очков за кофе!"
                else:
                    score += item["pts"]
                    sounds["gold" if item["type"] == "GOLD" else "good"].play()
                    status_text = f"* Поймано: {item['clean_label']} (+{item['pts']})!"
                items.remove(item)
            elif item["rect"].y > HEIGHT - 60:
                items.remove(item)

    for p in tuple(particles):
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["life"] -= dt
        if p["life"] <= 0:
            particles.remove(p)

    ox = random.randint(-6, 6) if shake_timer > 0 else 0
    oy = random.randint(-6, 6) if shake_timer > 0 else 0
    if shake_timer > 0:
        shake_timer -= dt

    screen.fill(BG_COLOR)

    for item in items:
        screen.blit(item["surf"], item["rect"].move(ox, oy))
    for h in hammers:
        rot = pygame.transform.rotate(hammer_surf, h["angle"])
        screen.blit(rot, rot.get_rect(center=(int(h["x"] + ox), int(h["y"] + oy))))
    for p in particles:
        pygame.draw.rect(screen, p["color"], (int(p["x"] + ox - 3), int(p["y"] + oy - 3), 6, 6))

    draw_player(screen, player_rect, ox, oy)

    # HUD
    pygame.draw.rect(screen, (0, 0, 0), (15, 12, WIDTH - 30, 44))
    pygame.draw.rect(screen, WHITE, (15, 12, WIDTH - 30, 44), 3)
    pygame.draw.rect(screen, (80, 0, 0), (30, 22, 140, 24))
    pygame.draw.rect(screen, RED if hp <= 25 else CYAN, (30, 22, int(1.4 * hp), 24))
    pygame.draw.rect(screen, WHITE, (30, 22, 140, 24), 2)

    lvl = 1 + score // 500
    screen.blit(fonts["hud"].render(f"LVL {lvl}  SCORE: {score:06d}  BEST: {best_score:06d}", True, WHITE), (185, 24))

    pygame.draw.rect(screen, BLUE_BOX, (15, HEIGHT - 55, WIDTH - 30, 42))
    pygame.draw.rect(screen, WHITE, (15, HEIGHT - 55, WIDTH - 30, 42), 3)
    screen.blit(fonts["small"].render(status_text, True, WHITE), (30, HEIGHT - 42))

    if not game_started:
        draw_start_modal(screen, fonts)

    if game_over:
        if gameover_img:
            screen.blit(gameover_img, (0, 0))
        else:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 185))
            screen.blit(ov, (0, 0))

        if entering_name:
            draw_name_input_modal(screen, fonts, score, player_name_input)
        else:
            draw_gameover_leaderboard(screen, fonts, score, records)

    screen.blit(scanlines, (0, 0))
    pygame.display.flip()
