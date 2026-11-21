const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function ensureAudio() {
    if (!audioCtx) audioCtx = new AudioCtx();
    if (audioCtx.state === "suspended") audioCtx.resume();
}

function play8BitSound(fStart, fEnd, durationSec, type = "square", vol = 0.08) {
    ensureAudio();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(fStart, audioCtx.currentTime);
    osc.frequency.linearRampToValueAtTime(fEnd, audioCtx.currentTime + durationSec);
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + durationSec);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + durationSec);
}

const TENSE_NOTES = [
    110.00, 110.00, 116.54, 110.00,
    130.81, 123.47, 110.00, 82.41,
    98.00,  98.00,  103.83, 98.00,
    116.54, 110.00, 87.31,  82.41
];

let musicOn = true;
let bgmTimer = 0;
let bgmStep = 0;

function updateMusic(dt, gameStarted, gameOver, score, hp) {
    if (!musicOn || gameOver || !audioCtx) return;
    bgmTimer += dt;

    let stepInterval = 0.28;
    if (gameStarted) {
        const dangerBoost = hp <= 25 ? 0.03 : 0.0;
        stepInterval = Math.max(0.10, 0.24 - (score / 25000) - dangerBoost);
    }

    if (bgmTimer >= stepInterval) {
        bgmTimer = 0;
        const freq = TENSE_NOTES.at(bgmStep);
        play8BitSound(freq, freq * 0.98, 0.10, "square", 0.035);
        bgmStep = (bgmStep + 1) % TENSE_NOTES.length;
    }
}
