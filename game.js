let player = { x: W / 2 - 45, y: H - 155, w: 90, h: 70, speed: 460 };
let items = [], hammers = [], particles = [];
let score = 0, hp = 100, spawnTimer = 0, shootCooldown = 0, shakeTimer = 0;
let statusText = "* Ожидание запуска сессии...";
let gameStarted = false, gameOver = false;
let keys = {}, pointerX = null, isPointerDown = false;

function startNewGame() {
    ensureAudio();
    score = 0; hp = 100; bgmStep = 0; bgmTimer = 0;
    items = []; hammers = []; particles = [];
    gameStarted = true; gameOver = false;
    statusText = "* Сессия началась! Лови годноту, бань баяны!";
}

function throwBanhammer() {
    if (shootCooldown > 0 || gameOver || !gameStarted) return;
    shootCooldown = 0.35;
    hammers.push({ x: player.x + player.w / 2, y: player.y - 25, speed: 580, angle: 0 });
    play8BitSound(380, 160, 0.08, "triangle");
}

window.addEventListener("keydown", e => {
    keys[e.code] = true;
    if (e.code === "KeyM") {
        musicOn = !musicOn;
        statusText = musicOn ? "* 8-битная музыка включена!" : "* Музыка выключена.";
    } else if ((!gameStarted || gameOver) && (e.code === "Space" || e.code === "Enter")) {
        e.preventDefault();
        startNewGame();
    } else if (gameStarted && !gameOver && !e.repeat && (e.code === "Space" || e.code === "ArrowUp" || e.code === "KeyW")) {
    e.preventDefault();
    throwBanhammer();
    }
});
window.addEventListener("keyup", e => { keys[e.code] = false; });

function getCanvasCoords(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (clientX - rect.left) * (W / rect.width),
        y: (clientY - rect.top) * (H / rect.height)
    };
}

function isInsideBanBtn(pos) {
    return pos.x >= banBtn.x && pos.x <= banBtn.x + banBtn.w &&
           pos.y >= banBtn.y && pos.y <= banBtn.y + banBtn.h;
}

canvas.addEventListener("touchstart", e => {
    if (!gameStarted || gameOver) { startNewGame(); return; }
    for (let i = 0; i < e.changedTouches.length; i++) {
        const pos = getCanvasCoords(e.changedTouches.item(i).clientX, e.changedTouches.item(i).clientY);
        if (isInsideBanBtn(pos)) {
            throwBanhammer();
        } else {
            pointerX = pos.x;
        }
    }
}, { passive: true });

canvas.addEventListener("touchmove", e => {
    for (let i = 0; i < e.changedTouches.length; i++) {
        const pos = getCanvasCoords(e.changedTouches.item(i).clientX, e.changedTouches.item(i).clientY);
        if (!isInsideBanBtn(pos)) pointerX = pos.x;
    }
}, { passive: true });

canvas.addEventListener("touchend", e => {
    if (e.touches.length === 0) pointerX = null;
});

canvas.addEventListener("mousedown", e => {
    if (!gameStarted || gameOver) { startNewGame(); return; }
    const pos = getCanvasCoords(e.clientX, e.clientY);
    if (isInsideBanBtn(pos)) throwBanhammer();
    else pointerX = pos.x;
});

canvas.addEventListener("mousemove", e => {
    if (e.buttons === 1) {
        const pos = getCanvasCoords(e.clientX, e.clientY);
        if (!isInsideBanBtn(pos)) pointerX = pos.x;
    }
});

canvas.addEventListener("mouseup", () => { pointerX = null; });

function spawnItem() {
    const total = MEME_TYPES.reduce((s, it) => s + it.weight, 0);
    let r = Math.random() * total, tpl = MEME_TYPES.at(0);
    for (const it of MEME_TYPES) { if (r < it.weight) { tpl = it; break; } r -= it.weight; }

    ctx.font = "bold 16px 'Courier New'";
    const maxW = Math.max(...tpl.lines.map(l => ctx.measureText(l).width));
    const boxW = Math.max(96, maxW + 24), boxH = tpl.lines.length > 1 ? 48 : 36;
    const x = 20 + Math.random() * (W - boxW - 40);
    const speed = 210 + Math.random() * 120 + tpl.extraSpeed + score * 0.035;
    items.push({ x, y: 75, w: boxW, h: boxH, lines: tpl.lines, cleanLabel: tpl.lines.join(" "), color: tpl.color, type: tpl.type, pts: tpl.pts, speed });
}

function spawnExplosion(x, y, color) {
    for (let i = 0; i < 14; i++) {
        const a = Math.random() * Math.PI * 2, spd = 60 + Math.random() * 180;
        particles.push({ x, y, vx: Math.cos(a) * spd, vy: Math.sin(a) * spd, life: 0.35, color });
    }
}

let lastTime = performance.now();
function loop(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;
    updateMusic(dt, gameStarted, gameOver, score, hp);

    if (gameStarted && !gameOver) {
        if (shootCooldown > 0) shootCooldown -= dt;
        if (keys["ArrowLeft"] || keys["KeyA"]) player.x -= player.speed * dt;
        if (keys["ArrowRight"] || keys["KeyD"]) player.x += player.speed * dt;
        if (pointerX !== null) player.x += (pointerX - player.w / 2 - player.x) * Math.min(1, 15 * dt);
        player.x = Math.max(18, Math.min(W - player.w - 18, player.x));

        spawnTimer += dt;
        if (spawnTimer >= Math.max(0.36, 0.85 - score / 12000)) { spawnTimer = 0; spawnItem(); }

        for (let hi = hammers.length - 1; hi >= 0; hi--) {
            const h = hammers.at(hi);
            h.y -= h.speed * dt; h.angle += 15 * dt;
            let hit = false;
            for (let ii = items.length - 1; ii >= 0; ii--) {
                const it = items.at(ii);
                if (h.x + 12 > it.x && h.x - 12 < it.x + it.w && h.y + 12 > it.y && h.y - 12 < it.y + it.h) {
                    hit = true;
                    spawnExplosion(it.x + it.w / 2, it.y + it.h / 2, it.color);
                    if (it.type === "BAD") {
                        score += 50; play8BitSound(180, 540, 0.14);
                        // if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred("medium");
                        statusText = `* БАНХАММЕР! ${it.cleanLabel} в бане (+50)!`;
                    } else if (it.type === "HEAL") {
                        play8BitSound(220, 75, 0.2);
                        statusText = "* Ой! Разбил кофе молотком! Обидно...";
                    } else {
                        const penalty = Math.floor(it.pts / 2);
                        score = Math.max(0, score - penalty); play8BitSound(220, 75, 0.2);
                        statusText = `* МИССКЛИК! Сбил ${it.cleanLabel} (-${penalty})!`;
                    }
                    items.splice(ii, 1);
                    break;
                }
            }
            if (hit || h.y < 65) hammers.splice(hi, 1);
        }

        for (let i = items.length - 1; i >= 0; i--) {
            const it = items.at(i);
            it.y += it.speed * dt;
            if (it.x < player.x + player.w + 5 && it.x + it.w > player.x - 5 && it.y < player.y + player.h && it.y + it.h > player.y - 20) {
                if (it.type === "BAD") {
                    hp += it.pts; shakeTimer = 0.25; play8BitSound(220, 75, 0.25);
                    // if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred("heavy");
                    statusText = `* ОЙ! Попался ${it.cleanLabel}!`;
                    if (hp <= 0) {
                        hp = 0;
                        gameOver = true;
                        setTimeout(() => addRecord(score), 100);
                    }

                } else if (it.type === "HEAL") {
                    const oldHp = hp; hp = Math.min(100, hp + it.pts); play8BitSound(440, 1100, 0.25);
                    // if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");
                    if (hp > oldHp) statusText = `* Кофе! +${hp - oldHp} HP иронии!`;
                    else { score += 100; statusText = "* Максимум HP! +100 бонусных очков!"; }
                } else {
                    score += it.pts; play8BitSound(it.type === "GOLD" ? 660 : 520, it.type === "GOLD" ? 1320 : 880, 0.15);
                    // if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred("light");
                    statusText = `* ${it.cleanLabel} (+${it.pts} очков)!`;
                }
                items.splice(i, 1);
            } else if (it.y > H - 70) items.splice(i, 1);
        }
    }

    for (let pi = particles.length - 1; pi >= 0; pi--) {
        const p = particles.at(pi);
        p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt;
        if (p.life <= 0) particles.splice(pi, 1);
    }

    let ox = 0, oy = 0;
    if (shakeTimer > 0) { shakeTimer -= dt; ox = (Math.random() - 0.5) * 12; oy = (Math.random() - 0.5) * 12; }

    ctx.fillStyle = COLORS.bg; ctx.fillRect(0, 0, W, H);
    ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    for (const it of items) {
        const rx = it.x + ox, ry = it.y + oy;
        ctx.fillStyle = "#0f0f19"; ctx.fillRect(rx, ry, it.w, it.h);
        ctx.strokeStyle = it.color; ctx.lineWidth = 3; ctx.strokeRect(rx, ry, it.w, it.h);
        ctx.fillStyle = it.color;
        if (it.lines.length === 1) ctx.fillText(it.lines.at(0), rx + it.w / 2, ry + it.h / 2);
        else { ctx.fillText(it.lines.at(0), rx + it.w / 2, ry + it.h / 2 - 9); ctx.fillText(it.lines.at(1), rx + it.w / 2, ry + it.h / 2 + 9); }
    }

    for (const h of hammers) {
        ctx.save(); ctx.translate(h.x + ox, h.y + oy); ctx.rotate(h.angle);
        ctx.fillStyle = "#d77643"; ctx.fillRect(-3, -4, 6, 20);
        ctx.fillStyle = "#8b9bb4"; ctx.fillRect(-14, -14, 28, 12);
        ctx.fillStyle = COLORS.red; ctx.fillRect(-12, -10, 24, 4);
        ctx.restore();
    }

    for (const p of particles) { ctx.fillStyle = p.color; ctx.fillRect(p.x + ox - 3, p.y + oy - 3, 6, 6); }
    drawPlayer(player, ox, oy);
   
    if (gameStarted && !gameOver) {
        drawBanButton(shootCooldown);
    }

    // HUD
    ctx.fillStyle = "#000000"; ctx.fillRect(12, 12, W - 24, 52);
    ctx.strokeStyle = COLORS.white; ctx.lineWidth = 3; ctx.strokeRect(12, 12, W - 24, 52);
    ctx.fillStyle = "#500000"; ctx.fillRect(24, 24, 110, 26);
    ctx.fillStyle = hp <= 25 ? COLORS.red : COLORS.cyan; ctx.fillRect(24, 24, 1.1 * hp, 26);
    ctx.strokeRect(24, 24, 110, 26);

    ctx.fillStyle = COLORS.white; ctx.textAlign = "left"; ctx.font = "bold 16px 'Courier New'";
    const lvl = 1 + Math.floor(score / 500);
    ctx.fillText(`LVL ${lvl}  SCORE:${String(score).padStart(5, "0")}  BEST:${String(bestScore).padStart(5, "0")}`, 146, 38);

    ctx.fillStyle = COLORS.blueBox; ctx.fillRect(12, H - 62, W - 24, 48);
    ctx.strokeStyle = COLORS.white; ctx.strokeRect(12, H - 62, W - 24, 48);
    ctx.fillStyle = COLORS.white; ctx.font = "bold 14px 'Courier New'";
    ctx.fillText(statusText, 22, H - 38);

    if (!gameStarted) drawStartModal();
    if (gameOver) drawGameOverScreen(score);

    ctx.fillStyle = "rgba(0, 0, 0, 0.25)";
    for (let y = 0; y < H; y += 4) ctx.fillRect(0, y, W, 1);

    requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
