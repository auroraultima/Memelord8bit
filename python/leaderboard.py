import json
import os
import pygame
from assets import WIDTH, HEIGHT, WHITE, YELLOW, RED, CYAN, GREEN, BLUE_BOX

RECORDS_FILE = "records.json"

def load_records():
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[:5]
        except Exception:
            pass
    return []

def qualifies_for_top(score):
    if score <= 0:
        return False
    records = load_records()
    if len(records) < 5:
        return True
    return score > records[-1]["score"]

def add_record(name, score):
    records = load_records()
    clean_name = name.strip().upper()[:10] or "ANON"

    for r in records:
        r["is_new"] = False

    records.append({"name": clean_name, "score": score, "is_new": True})
    records.sort(key=lambda x: x["score"], reverse=True)
    records = records[:5]

    to_save = [{"name": r.get("name", "ANON"), "score": r["score"]} for r in records]
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)

    return records

def draw_name_input_modal(surface, fonts, score, current_name):
    box_w, box_h = 540, 210
    bx = (WIDTH - box_w) // 2
    by = HEIGHT - box_h - 20

    pygame.draw.rect(surface, BLUE_BOX, (bx, by, box_w, box_h))
    pygame.draw.rect(surface, WHITE, (bx, by, box_w, box_h), 4)
    pygame.draw.rect(surface, WHITE, (bx + 6, by + 6, box_w - 12, box_h - 12), 2)

    t1 = fonts["hud"].render(f"НОВЫЙ РЕКОРД В ТОП-5!  СЧЕТ: {score}", True, YELLOW)
    t2 = fonts["small"].render("ВВЕДИ СВОЙ НИКНЕЙМ (ДО 10 БУКВ):", True, CYAN)
    surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, by + 22))
    surface.blit(t2, (WIDTH // 2 - t2.get_width() // 2, by + 58))

    # Поле ввода с мигающим курсором
    cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
    display_text = f"[ {current_name}{cursor} ]"
    inp_surf = fonts["big"].render(display_text, True, GREEN)
    surface.blit(inp_surf, (WIDTH // 2 - inp_surf.get_width() // 2, by + 95))

    hint = fonts["small"].render("Нажми ENTER для сохранения", True, WHITE)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, by + box_h - 36))

def draw_gameover_leaderboard(surface, fonts, score, records):
    box_w, box_h = 560, 245
    bx = (WIDTH - box_w) // 2
    by = HEIGHT - box_h - 15

    pygame.draw.rect(surface, BLUE_BOX, (bx, by, box_w, box_h))
    pygame.draw.rect(surface, WHITE, (bx, by, box_w, box_h), 4)
    pygame.draw.rect(surface, WHITE, (bx + 6, by + 6, box_w - 12, box_h - 12), 2)

    t1 = fonts["hud"].render(f"ПЕРЕДОЗ БАЯНАМИ!   ВАШ СЧЕТ: {score}", True, RED)
    surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, by + 16))

    sub = fonts["small"].render("--- ТОП-5 МЕМ-ЛОРДОВ ---", True, CYAN)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, by + 46))

    curr_y = by + 72
    if not records:
        empty_txt = fonts["small"].render("Пока нет рекордов. Набери больше 0 очков!", True, WHITE)
        surface.blit(empty_txt, (WIDTH // 2 - empty_txt.get_width() // 2, curr_y + 20))
    else:
        for idx, rec in enumerate(records, start=1):
            is_new = rec.get("is_new", False)
            color = YELLOW if is_new else (GREEN if idx == 1 else WHITE)
            tag = " <-- NEW!" if is_new else ""
            name_str = rec.get("name", "ANON").ljust(10)
            row_str = f"{idx}.  {name_str}   {rec['score']:06d} ОЧК.{tag}"
            row_surf = fonts["small"].render(row_str, True, color)
            surface.blit(row_surf, (bx + 45, curr_y))
            curr_y += 24

    prompt = fonts["small"].render(">> ПРОБЕЛ или КЛИК для новой сессии <<", True, YELLOW)
    surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, by + box_h - 32))
