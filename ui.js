const tg = window.Telegram?.WebApp;
let playerName = "ANON";
if (tg) {
    tg.ready();
    tg.expand();
    const user = tg.initDataUnsafe?.user;
    if (user?.username) playerName = user.username.toUpperCase().slice(0, 10);
    else if (user?.first_name) playerName = user.first_name.toUpperCase().slice(0, 10);
}

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;

const gameOverImg = new Image();
let gameOverImgLoaded = false;
gameOverImg.onload = () => { gameOverImgLoaded = true; };
gameOverImg.src = "gameover.png";

const COLORS = {
    bg: "#1a1c2c", white: "#ffffff", cyan: "#00e5ff", yellow: "#ffd740",
    red: "#ff3b30", green: "#69f0ae", pink: "#ff69b4", blueBox: "#0000aa",
    leather: "#7b3f1d", leatherDark: "#4a2511"
};

const MEME_TYPES = [
    { type: "GOOD", lines: ["ГОДНОТА"], color: COLORS.green, pts: 100, weight: 30, extraSpeed: 0 },
    { type: "GOOD", lines: ["КЛАССИКА"], color: COLORS.cyan, pts: 150, weight: 25, extraSpeed: 0 },
    { type: "GOLD", lines: ["ЗОЛОТОЙ", "ФОНД"], color: COLORS.yellow, pts: 300, weight: 12, extraSpeed: 95 },
    { type: "BAD",  lines: ["БАЯН 2012"], color: COLORS.red, pts: -25, weight: 18, extraSpeed: 0 },
    { type: "BAD",  lines: ["КРИНЖ"], color: COLORS.red, pts: -25, weight: 18, extraSpeed: 0 },
    { type: "HEAL", lines: ["+КОФЕ", "HP"], color: COLORS.pink, pts: 25, weight: 7, extraSpeed: 95 }
];

function loadRecords() {
    try {
        const raw = localStorage.getItem("memelord_top5");
        return raw ? JSON.parse(raw) : [];
    } catch { return []; }
}

let records = loadRecords();
let bestScore = records.length > 0 ? records.at(0).score : 0;

function addRecord(newScore) {
    records = loadRecords();
    if (newScore <= 0) return;
    records.forEach(r => r.isNew = false);
    records.push({ name: playerName, score: newScore, isNew: true });
    records.sort((a, b) => b.score - a.score);
    records = records.slice(0, 5);
    localStorage.setItem("memelord_top5", JSON.stringify(records.map(r => ({ name: r.name, score: r.score }))));
    bestScore = records.at(0).score;
}

function drawPlayer(player, ox, oy) {
    const px = player.x + ox, py = player.y + oy;
    ctx.fillStyle = COLORS.leatherDark; ctx.fillRect(px - 10, py + 10, player.w + 20, player.h - 10);
    ctx.fillStyle = COLORS.leather; ctx.fillRect(px, py, player.w, player.h);
    ctx.fillStyle = "#e6b48c"; ctx.fillRect(px + 30, py - 22, 30, 24);
    ctx.fillStyle = "#1e1e23"; ctx.fillRect(px + 28, py - 26, 34, 8); ctx.fillRect(px + 30, py - 8, 30, 10);
    ctx.fillStyle = COLORS.cyan; ctx.fillRect(px + 32, py - 16, 10, 6); ctx.fillRect(px + 48, py - 16, 10, 6);
    ctx.fillStyle = "#14141e"; ctx.fillRect(px + 20, py + 18, 50, 32);
    ctx.fillStyle = COLORS.cyan; ctx.fillRect(px + 22, py + 16, 46, 3);
}

function drawStartModal() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.78)";
    ctx.fillRect(0, 0, W, H);

    const bw = 436, bh = 410;
    const bx = (W - bw) / 2, by = (H - bh) / 2;
    ctx.fillStyle = COLORS.blueBox; ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = COLORS.white; ctx.lineWidth = 4; ctx.strokeRect(bx, by, bw, bh);
    ctx.lineWidth = 2; ctx.strokeRect(bx + 8, by + 8, bw - 16, bh - 16);

    ctx.textAlign = "center"; ctx.fillStyle = COLORS.yellow; ctx.font = "bold 24px 'Courier New'";
    ctx.fillText("MEMELORD: 8-BIT EDITION", W / 2, by + 40);

    const rules = [
        ["СМЫСЛ ИГРЫ:", COLORS.white],
        ["* Лови ГОДНОТУ и ЗОЛОТОЙ ФОНД.", COLORS.green],
        ["* Избегай БАЯНОВ и КРИНЖА (-25 HP).", COLORS.red],
        ["* Лови редкий +КОФЕ для лечения.", COLORS.pink],
        ["* Бей баяны МОЛОТКОМ (+50 очков),", COLORS.cyan],
        ["  но не зацепи годноту (штраф)!", COLORS.cyan],
        ["", COLORS.white],
        ["УПРАВЛЕНИЕ:", COLORS.yellow],
        ["Палец / Стрелки — двигать кресло", COLORS.white],
        ["Тап / ПРОБЕЛ     — банхаммер", COLORS.white],
        ["M                — вкл/выкл звук", COLORS.white]
    ];

    ctx.textAlign = "left"; ctx.font = "bold 15px 'Courier New'";
    let cy = by + 80;
    for (const [txt, col] of rules) {
        if (txt) { ctx.fillStyle = col; ctx.fillText(txt, bx + 24, cy); }
        cy += 24;
    }

    if (Math.floor(performance.now() / 450) % 2 === 0) {
        ctx.textAlign = "center"; ctx.fillStyle = COLORS.yellow; ctx.font = "bold 17px 'Courier New'";
        ctx.fillText(">> НАЖМИ / ПРОБЕЛ ДЛЯ СТАРТА <<", W / 2, by + bh - 26);
    }
}

function drawGameOverScreen(score) {
    if (gameOverImgLoaded) ctx.drawImage(gameOverImg, 0, 0, W, H);
    else { ctx.fillStyle = "rgba(0, 0, 0, 0.85)"; ctx.fillRect(0, 0, W, H); }

    const boxH = 245, boxY = H - boxH - 12;
    ctx.fillStyle = COLORS.blueBox; ctx.fillRect(12, boxY, W - 24, boxH);
    ctx.strokeStyle = COLORS.white; ctx.lineWidth = 4; ctx.strokeRect(12, boxY, W - 24, boxH);
    ctx.lineWidth = 2; ctx.strokeRect(18, boxY + 6, W - 36, boxH - 12);

    ctx.textAlign = "center"; ctx.fillStyle = COLORS.red; ctx.font = "bold 18px 'Courier New'";
    ctx.fillText(`ПЕРЕДОЗ БАЯНАМИ!  СЧЕТ: ${score}`, W / 2, boxY + 28);

    ctx.fillStyle = COLORS.cyan; ctx.font = "bold 15px 'Courier New'";
    ctx.fillText("--- ТОП-5 МЕМ-ЛОРДОВ ---", W / 2, boxY + 54);

    ctx.textAlign = "left"; ctx.font = "bold 14px 'Courier New'";
    let cy = boxY + 80;
    if (records.length === 0) {
        ctx.textAlign = "center"; ctx.fillStyle = COLORS.white;
        ctx.fillText("Пока нет рекордов. Набери > 0 очков!", W / 2, cy + 20);
    } else {
        records.forEach((rec, i) => {
            ctx.fillStyle = rec.isNew ? COLORS.yellow : (i === 0 ? COLORS.green : COLORS.white);
            const tag = rec.isNew ? " NEW!" : "";
            ctx.fillText(`${i + 1}. ${rec.name.padEnd(10, " ")} ${String(rec.score).padStart(6, "0")}${tag}`, 34, cy);
            cy += 24;
        });
    }

    ctx.textAlign = "center"; ctx.fillStyle = COLORS.yellow; ctx.font = "bold 14px 'Courier New'";
    ctx.fillText(">> Нажми / ПРОБЕЛ для рестарта <<", W / 2, boxY + boxH - 18);
}
