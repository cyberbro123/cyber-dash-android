"""Cyber Dash - an original neon rhythm-platformer built with Pygame.

Install:  py -m pip install pygame
Run:     py cyber_dash.py

CONTROLS
--------
Menu:       G opens graphics settings; S opens the skin shop
Graphics:   1-4 quality; O glow; T particles; B moving background; F fullscreen
Cube:       SPACE / UP / W / left-click to jump
Flying Bot: Hold SPACE / UP / W / left mouse button to rise; release to fall
P:          Pause / resume
M:          Toggle music
R:          Restart after a crash
ESC:        Return to menu (or quit from menu)

SECRET COURSE
-------------
On the main menu, press C and type exactly: Syed Ayyan Ahmed
Then press ENTER. The developer course will be permanently unlocked.

Coins, best score, purchased skins, and the course unlock are saved in
cyber_dash_save.json beside this Python file. All sounds and graphics are
created by the game; no external assets are needed.
"""

import array
import json
import math
import os
import random
import sys

import pygame


# =============================================================================
# INITIALISATION
# =============================================================================
pygame.init()
WIDTH, HEIGHT = 960, 600
FPS = 60
GROUND_Y = 492
PLAYER_X = 155
PLAYER_SIZE = 40
def get_save_path():
    """Use app-private storage on Android and the script folder on desktop."""
    candidates = []
    android_private = os.environ.get("ANDROID_PRIVATE")
    if android_private:
        candidates.append(android_private)
    home_dir = os.path.expanduser("~")
    if home_dir:
        candidates.append(home_dir)
    candidates.append(os.path.dirname(os.path.abspath(__file__)))
    for folder in candidates:
        try:
            if folder and os.path.isdir(folder) and os.access(folder, os.W_OK):
                return os.path.join(folder, "cyber_dash_save.json")
        except OSError:
            continue
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_dash_save.json")


SAVE_PATH = get_save_path()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER DASH | Neon Rhythm Runner")
clock = pygame.time.Clock()

FONT_HUGE = pygame.font.Font(None, 88)
FONT_BIG = pygame.font.Font(None, 60)
FONT_MED = pygame.font.Font(None, 38)
FONT_SMALL = pygame.font.Font(None, 27)
FONT_TINY = pygame.font.Font(None, 21)

BG_TOP = (5, 8, 25)
BG_BOTTOM = (24, 10, 48)
WHITE = (239, 248, 255)
MUTED = (145, 170, 210)
CYAN = (38, 238, 255)
PINK = (255, 65, 174)
PURPLE = (157, 91, 255)
GOLD = (255, 207, 74)
DARK = (9, 15, 39)

MODES = ["EASY", "MEDIUM", "HARD", "EXTREME"]
MODE_SETTINGS = {
    "EASY":    {"speed": 5.1, "gap": (94, 116), "min_gap": 78, "gravity": 0.70, "jump": -15.3},
    "MEDIUM":  {"speed": 6.2, "gap": (78, 98),  "min_gap": 65, "gravity": 0.78, "jump": -15.6},
    "HARD":    {"speed": 7.3, "gap": (68, 86),  "min_gap": 57, "gravity": 0.82, "jump": -15.9},
    "EXTREME": {"speed": 8.4, "gap": (60, 76),  "min_gap": 51, "gravity": 0.86, "jump": -16.1},
}

SKINS = {
    "cyan":   {"name": "CYAN CORE",   "price": 0,   "color": (38, 238, 255), "edge": (205, 255, 255), "desc": "The original cyber cube"},
    "lava":   {"name": "LAVA BYTE",   "price": 35,  "color": (255, 83, 54), "edge": (255, 207, 135), "desc": "Hot neon energy"},
    "violet": {"name": "VIOLET X",    "price": 55,  "color": (164, 89, 255), "edge": (231, 190, 255), "desc": "Purple power"},
    "mint":   {"name": "MINT GLITCH", "price": 75,  "color": (75, 255, 173), "edge": (205, 255, 225), "desc": "Fresh digital style"},
    "gold":   {"name": "GOLD RUSH",   "price": 110, "color": (255, 202, 59), "edge": (255, 247, 185), "desc": "Shine on the grid"},
    "flybot": {"name": "FLYING ROBOT", "price": 145, "color": (255, 89, 190), "edge": (255, 220, 248), "desc": "Hold jump to fly!"},
}


def load_profile():
    defaults = {
        "coins": 0,
        "best": 0,
        "owned_skins": ["cyan"],
        "skin": "cyan",
        "dev_unlocked": False,
        "music_on": True,
        "sfx_on": True,
        "graphics": {
            "quality": "HIGH",
            "glow": True,
            "particles": True,
            "animated_background": True,
            "fullscreen": False,
        },
    }
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as file:
            loaded = json.load(file)
        if isinstance(loaded, dict):
            defaults.update(loaded)
    except (OSError, ValueError, TypeError):
        pass
    if defaults.get("skin") not in SKINS:
        defaults["skin"] = "cyan"
    owned = defaults.get("owned_skins", ["cyan"])
    if not isinstance(owned, list):
        owned = ["cyan"]
    defaults["owned_skins"] = list(dict.fromkeys([s for s in owned if s in SKINS] + ["cyan"]))
    defaults["coins"] = max(0, int(defaults.get("coins", 0)))
    defaults["best"] = max(0, int(defaults.get("best", 0)))
    if defaults["skin"] not in defaults["owned_skins"]:
        defaults["skin"] = "cyan"
    graphics = defaults.get("graphics", {})
    if not isinstance(graphics, dict):
        graphics = {}
    graphics_defaults = {"quality": "HIGH", "glow": True, "particles": True,
                         "animated_background": True, "fullscreen": False}
    graphics_defaults.update(graphics)
    if graphics_defaults.get("quality") not in ("LOW", "MEDIUM", "HIGH", "ULTRA"):
        graphics_defaults["quality"] = "HIGH"
    for key in ("glow", "particles", "animated_background", "fullscreen"):
        graphics_defaults[key] = bool(graphics_defaults.get(key, True))
    defaults["graphics"] = graphics_defaults
    return defaults


profile = load_profile()
if profile.get("graphics", {}).get("fullscreen"):
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | getattr(pygame, "SCALED", 0))
    except pygame.error:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)


def save_profile():
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as file:
            json.dump(profile, file, indent=2)
    except OSError:
        # The game can still be played if the folder is read-only.
        pass


# =============================================================================
# PROCEDURAL AUDIO - no sound files required
# =============================================================================
AUDIO_OK = False
SFX = {}
MUSIC_SOUND = None
music_channel = None


def make_tone(frequency, duration=0.12, volume=0.25, wave_type="sine", slide=0.0):
    """Return a short synthesized Sound. Safe to call only after mixer init."""
    sample_rate = 22050
    count = max(1, int(sample_rate * duration))
    samples = array.array("h")
    for i in range(count):
        t = i / sample_rate
        envelope = min(1.0, i / max(1, sample_rate * 0.012)) * max(0.0, 1.0 - i / count) ** 0.65
        freq = max(30.0, frequency + slide * (i / count))
        phase = 2.0 * math.pi * freq * t
        if wave_type == "square":
            value = 1.0 if math.sin(phase) >= 0 else -1.0
        elif wave_type == "triangle":
            value = 2.0 / math.pi * math.asin(math.sin(phase))
        else:
            value = math.sin(phase)
        samples.append(int(32767 * volume * envelope * value))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_music_loop():
    """Create an original, high-energy arcade EDM loop (not a game soundtrack copy)."""
    sample_rate = 22050
    bpm = 140
    beat_len = 60.0 / bpm
    duration = beat_len * 16  # four bars, seamless loop
    total = int(sample_rate * duration)
    samples = array.array("h")

    # Original F-minor / Db / Ab / Eb progression with a bright 16th-note lead.
    scale = [174.61, 207.65, 233.08, 261.63, 311.13, 349.23, 415.30, 466.16]
    melody = [0, 3, 5, 3, 1, 3, 6, 5, 0, 3, 7, 5, 2, 5, 6, 3,
              0, 3, 5, 7, 5, 3, 1, 3, 2, 5, 7, 5, 3, 1, 3, 5]
    roots = [87.31, 69.30, 103.83, 77.78]  # F2, Db2, Ab2, Eb2
    chord_notes = [
        (174.61, 207.65, 261.63),
        (138.59, 174.61, 207.65),
        (207.65, 261.63, 311.13),
        (155.56, 196.00, 233.08),
    ]

    for i in range(total):
        t = i / sample_rate
        beat_pos = t / beat_len
        beat_index = int(beat_pos) % 16
        beat_phase = beat_pos - int(beat_pos)
        eighth_phase = (t % (beat_len / 2)) / (beat_len / 2)
        bar = (beat_index // 4) % 4

        # Syncopated pluck lead, with a little detuned saw-like brightness.
        step_index = int(t / (beat_len / 2)) % len(melody)
        note = scale[melody[step_index]] * (2.0 if step_index % 8 >= 4 else 1.0)
        pluck_env = max(0.0, 1.0 - eighth_phase) ** 1.7
        lead = (math.sin(2 * math.pi * note * t)
                + 0.32 * math.sin(2 * math.pi * note * 2.01 * t)
                + 0.13 * math.sin(2 * math.pi * note * 3.0 * t)) * 0.105 * pluck_env

        # Sustained chord pad, gently pulsing each beat.
        chord = chord_notes[bar]
        pad_env = 0.72 + 0.28 * math.sin(2 * math.pi * beat_pos / 4.0)
        pad = sum(math.sin(2 * math.pi * f * t) for f in chord) * 0.025 * pad_env

        # Pumping sub-bass and a short electronic kick on each beat.
        root = roots[bar]
        bass_env = max(0.0, 1.0 - beat_phase) ** 0.7
        bass = math.sin(2 * math.pi * root * t) * 0.20 * bass_env
        kick_phase = t % beat_len
        kick_freq = 48.0 + 85.0 * max(0.0, 1.0 - kick_phase / 0.16)
        kick = math.sin(2 * math.pi * kick_freq * t) * max(0.0, 1.0 - kick_phase / 0.17) * 0.34

        # Snare/clap on beats 2 and 4; filtered noise hi-hats on eighth notes.
        snare_phase = (t % (beat_len * 2)) - beat_len
        snare_env = max(0.0, 1.0 - snare_phase / 0.13) if 0 <= snare_phase < 0.13 else 0.0
        noise = math.sin(2 * math.pi * (1400 + (i % 97) * 17) * t)
        snare = noise * snare_env * 0.12
        hat_phase = t % (beat_len / 2)
        hat_env = max(0.0, 1.0 - hat_phase / 0.035)
        hat = math.sin(2 * math.pi * 6500 * t) * hat_env * 0.035

        value = lead + pad + bass + kick + snare + hat
        # Tiny boundary fade keeps the loop from clicking.
        edge = min(1.0, i / 250.0, (total - 1 - i) / 250.0)
        value *= max(0.0, edge)
        samples.append(int(max(-1.0, min(1.0, value)) * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    AUDIO_OK = True
    SFX["jump"] = make_tone(520, 0.13, 0.22, "square", 280)
    SFX["land"] = make_tone(150, 0.09, 0.16, "triangle", -50)
    SFX["coin"] = make_tone(760, 0.20, 0.22, "sine", 480)
    SFX["crash"] = make_tone(180, 0.32, 0.26, "triangle", -120)
    SFX["unlock"] = make_tone(440, 0.55, 0.22, "sine", 720)
    SFX["buy"] = make_tone(620, 0.18, 0.20, "square", 240)
    MUSIC_SOUND = make_music_loop()
    music_channel = pygame.mixer.Channel(0)
    MUSIC_SOUND.set_volume(0.22)
    if profile.get("music_on", True):
        music_channel.play(MUSIC_SOUND, loops=-1)
except (pygame.error, OSError):
    AUDIO_OK = False


def play_sfx(name):
    if AUDIO_OK and profile.get("sfx_on", True) and name in SFX:
        try:
            SFX[name].play()
        except pygame.error:
            pass


def set_music(enabled):
    profile["music_on"] = bool(enabled)
    if AUDIO_OK and music_channel:
        if enabled:
            if not music_channel.get_busy():
                music_channel.play(MUSIC_SOUND, loops=-1)
        else:
            music_channel.stop()
    save_profile()


def apply_fullscreen(enabled):
    """Switch display mode while retaining the game's 960x600 logical canvas."""
    global screen
    flags = 0
    if enabled:
        flags = pygame.FULLSCREEN | getattr(pygame, "SCALED", 0)
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    except pygame.error:
        # Fall back to a regular window on systems without scaled fullscreen support.
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if enabled else 0)
    profile.setdefault("graphics", {})["fullscreen"] = bool(enabled)
    save_profile()


# =============================================================================
# DRAWING HELPERS
# =============================================================================
def clamp(value, low, high):
    return max(low, min(high, value))


def draw_glow(surface, color, center, radius, strength=3):
    graphics = profile.get("graphics", {})
    quality = graphics.get("quality", "HIGH")
    if not graphics.get("glow", True) or quality == "LOW":
        return
    if quality == "MEDIUM":
        strength = min(strength, 2)
    size = max(8, radius * 4)
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for layer in range(strength, 0, -1):
        r = max(1, int(radius * layer / strength))
        alpha = int(15 + 22 * (strength - layer + 1) / strength)
        pygame.draw.circle(glow, (*color, alpha), (cx, cy), r)
    surface.blit(glow, (int(center[0] - cx), int(center[1] - cy)))


def draw_text(text, font, color, center, shadow=True):
    if shadow:
        shade = font.render(str(text), True, (0, 0, 0))
        screen.blit(shade, shade.get_rect(center=(center[0] + 3, center[1] + 4)))
    image = font.render(str(text), True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_button(rect, label, color=CYAN, enabled=True, small=False):
    rect = pygame.Rect(rect)
    fill = (13, 28, 59) if enabled else (24, 27, 42)
    edge = color if enabled else (75, 85, 110)
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, edge, rect, 2, border_radius=10)
    font = FONT_SMALL if small else FONT_MED
    draw_text(label, font, edge if enabled else MUTED, rect.center, shadow=False)


def polygon_rect_collision(points, rect):
    rect_points = [(rect.left, rect.top), (rect.right, rect.top), (rect.right, rect.bottom), (rect.left, rect.bottom)]
    axes = [(1, 0), (0, 1)]
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        edge = (x2 - x1, y2 - y1)
        axes.append((-edge[1], edge[0]))
    for axis in axes:
        p_proj = [p[0] * axis[0] + p[1] * axis[1] for p in points]
        r_proj = [p[0] * axis[0] + p[1] * axis[1] for p in rect_points]
        if max(p_proj) < min(r_proj) or max(r_proj) < min(p_proj):
            return False
    return True


# =============================================================================
# BACKGROUND
# =============================================================================
stars = [[random.randrange(WIDTH), random.randrange(25, GROUND_Y - 25), random.choice((1, 1, 2)), random.uniform(0.25, 0.85)] for _ in range(95)]


def draw_background(offset, tint=None):
    graphics = profile.get("graphics", {})
    quality = graphics.get("quality", "HIGH")
    motion = graphics.get("animated_background", True)
    scroll = offset if motion else 0
    top = BG_TOP if not tint else (10, 6, 24)
    bottom = BG_BOTTOM if not tint else (31, 8, 34)
    gradient_step = {"LOW": 12, "MEDIUM": 8, "HIGH": 4, "ULTRA": 2}.get(quality, 4)
    for y in range(0, HEIGHT, gradient_step):
        t = y / HEIGHT
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        pygame.draw.rect(screen, color, (0, y, WIDTH, gradient_step))

    star_stride = {"LOW": 5, "MEDIUM": 3, "HIGH": 2, "ULTRA": 1}.get(quality, 2)
    for star_index, (x, y, size, speed) in enumerate(stars):
        if star_index % star_stride:
            continue
        xx = (x - scroll * speed * 0.24) % WIDTH
        pygame.draw.circle(screen, (90, 125, 190), (int(xx), y), size)

    spacing = 48
    shift = int(scroll * 0.55) % spacing
    for x in range(-spacing, WIDTH + spacing, spacing):
        xx = x - shift
        pygame.draw.line(screen, (23, 39, 79), (xx, 105), (xx, GROUND_Y), 1)
    for y in range(125, GROUND_Y, 32):
        pygame.draw.line(screen, (20, 33, 72), (0, y), (WIDTH, y), 1)

    skyline = [28, 50, 34, 72, 41, 58, 26, 81, 45, 63, 35, 69, 30, 52, 76, 39]
    if quality != "LOW":
        for i, h in enumerate(skyline):
            x = (i * 72 - int(scroll * 0.16)) % (WIDTH + 72) - 72
            building = pygame.Rect(x, GROUND_Y - h - 28, 48, h + 28)
            pygame.draw.rect(screen, (11, 19, 49), building)
            pygame.draw.line(screen, (34, 63, 113), building.topleft, building.topright, 2)
            if quality in ("HIGH", "ULTRA"):
                for wy in range(building.top + 10, building.bottom - 6, 14):
                    pygame.draw.rect(screen, (34, 75, 119), (x + 9, wy, 4, 4))
                    pygame.draw.rect(screen, (34, 75, 119), (x + 27, wy, 4, 4))

    pygame.draw.rect(screen, (10, 15, 39), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(screen, CYAN, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
    pygame.draw.line(screen, (34, 87, 127), (0, GROUND_Y + 8), (WIDTH, GROUND_Y + 8), 1)
    floor_shift = int(scroll * 1.2) % 48
    for x in range(-48, WIDTH + 48, 48):
        pygame.draw.line(screen, (28, 45, 82), (x - floor_shift, GROUND_Y + 10), (x - floor_shift - 35, HEIGHT), 1)
    for y in range(GROUND_Y + 32, HEIGHT, 32):
        pygame.draw.line(screen, (20, 36, 68), (0, y), (WIDTH, y), 1)


# =============================================================================
# GAME OBJECTS
# =============================================================================
class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-3.5, 2.8)
        self.vy = random.uniform(-4.5, -0.8)
        self.life = random.randint(16, 30)
        self.max_life = self.life
        self.color = color
        self.radius = random.randint(2, 4)

    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.16 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            r = max(1, int(self.radius * self.life / self.max_life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class Player:
    def __init__(self, skin_id, mode):
        self.skin_id = skin_id
        self.skin = SKINS[skin_id]
        self.color = self.skin["color"]
        self.edge = self.skin["edge"]
        self.x = PLAYER_X
        self.size = PLAYER_SIZE
        self.y = GROUND_Y - self.size
        self.vel_y = 0.0
        self.gravity = MODE_SETTINGS[mode]["gravity"]
        self.jump_power = MODE_SETTINGS[mode]["jump"]
        self.on_ground = True
        self.rotation = 0.0
        self.trail = []
        self.is_flying = skin_id == "flybot"
        self.engine_phase = 0.0

    @property
    def rect(self):
        if self.is_flying:
            return pygame.Rect(int(self.x + 5), int(self.y + 5), self.size - 10, self.size - 10)
        return pygame.Rect(int(self.x + 5), int(self.y + 5), self.size - 10, self.size - 10)

    def jump(self):
        if not self.is_flying and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            play_sfx("jump")

    def update(self, particles, dt, flight_held=False):
        if self.is_flying:
            # Hold to rise, release to descend: a small arcade flight vehicle.
            self.vel_y += (-0.66 if flight_held else 0.55) * dt
            self.vel_y = clamp(self.vel_y, -7.0, 7.0)
            self.y += self.vel_y * dt
            self.y = clamp(self.y, 92, GROUND_Y - self.size)
            self.rotation = clamp(self.vel_y * -2.2, -22, 22)
            self.engine_phase += dt
            if profile.get("graphics", {}).get("particles", True) and random.random() < 0.35 * dt:
                particles.append(Particle(self.x + 2, self.y + 22, GOLD))
        else:
            self.vel_y += self.gravity * dt
            self.y += self.vel_y * dt
            if self.y + self.size >= GROUND_Y:
                if not self.on_ground and self.vel_y > 3:
                    if profile.get("graphics", {}).get("particles", True):
                        count = 3 if profile.get("graphics", {}).get("quality") == "LOW" else 6
                        for _ in range(count):
                            particles.append(Particle(self.x + self.size / 2, GROUND_Y - 2, self.color))
                    play_sfx("land")
                self.y = GROUND_Y - self.size
                self.vel_y = 0
                self.on_ground = True
                self.rotation = 0
            else:
                self.on_ground = False
                self.rotation = (self.rotation + 5.5 * dt) % 360

        self.trail.append((self.x + self.size / 2, self.y + self.size / 2))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, surface):
        if profile.get("graphics", {}).get("particles", True) and profile.get("graphics", {}).get("quality") != "LOW":
            for i, pos in enumerate(self.trail):
                r = max(2, int(4 + i * 0.9))
                ghost = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ghost, (*self.color, 18 + i * 8), (r + 2, r + 2), r)
                surface.blit(ghost, (int(pos[0] - r - 2), int(pos[1] - r - 2)))

        center = (int(self.x + self.size / 2), int(self.y + self.size / 2))
        draw_glow(surface, self.color, center, 31, 3)
        if self.is_flying:
            # Original little flying robot/ship, with a thruster and glowing eye.
            body = pygame.Surface((62, 48), pygame.SRCALPHA)
            pygame.draw.polygon(body, (70, 35, 91), [(7, 23), (20, 7), (48, 10), (59, 23), (48, 38), (20, 40)])
            pygame.draw.polygon(body, self.color, [(7, 23), (20, 7), (48, 10), (59, 23), (48, 38), (20, 40)], 3)
            pygame.draw.rect(body, self.edge, (24, 14, 22, 17), border_radius=6)
            pygame.draw.circle(body, (13, 25, 55), (35, 22), 5)
            pygame.draw.circle(body, CYAN, (37, 21), 2)
            pygame.draw.polygon(body, GOLD, [(8, 17), (0, 23), (8, 29)])
            pygame.draw.polygon(body, self.color, [(48, 12), (58, 6), (54, 18)], 2)
            pygame.draw.polygon(body, self.color, [(48, 35), (58, 42), (54, 29)], 2)
            flame_h = 7 + int(4 * abs(math.sin(self.engine_phase * 1.7)))
            pygame.draw.polygon(body, GOLD, [(2, 19), (2 - flame_h, 23), (2, 27)])
            rotated = pygame.transform.rotate(body, self.rotation)
            surface.blit(rotated, rotated.get_rect(center=center))
        else:
            cube = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(cube, self.color, (1, 1, self.size - 2, self.size - 2), border_radius=7)
            pygame.draw.rect(cube, self.edge, (5, 5, self.size - 10, self.size - 10), 2, border_radius=5)
            # Face changes slightly by skin so each cube feels distinct.
            if self.skin_id == "gold":
                pygame.draw.circle(cube, (80, 47, 5), (14, 16), 3)
                pygame.draw.circle(cube, (80, 47, 5), (27, 16), 3)
                pygame.draw.line(cube, (80, 47, 5), (13, 27), (28, 27), 3)
            else:
                pygame.draw.line(cube, (9, 35, 67), (10, 13), (28, 13), 3)
                pygame.draw.line(cube, (9, 35, 67), (10, 23), (28, 23), 3)
            rotated = pygame.transform.rotate(cube, self.rotation)
            surface.blit(rotated, rotated.get_rect(center=center))


class Obstacle:
    def __init__(self, x, kind="spike", size=42, y=None):
        self.x = float(x)
        self.kind = kind
        self.size = size
        self.y = float(y) if y is not None else GROUND_Y - size
        self.passed = False

    def update(self, speed, dt):
        self.x -= speed * dt

    def collides(self, player_rect):
        if self.kind in ("block", "airblock"):
            box = pygame.Rect(int(self.x + 4), int(self.y + 4), self.size - 8, self.size - 8)
            return player_rect.colliderect(box)
        if self.kind == "airspike":
            points = [(self.x + 2, self.y), (self.x + self.size / 2, self.y + self.size), (self.x + self.size - 2, self.y)]
        else:
            points = [(self.x + 2, self.y + self.size), (self.x + self.size / 2, self.y), (self.x + self.size - 2, self.y + self.size)]
        return polygon_rect_collision(points, player_rect)

    def draw(self, surface):
        if self.kind in ("block", "airblock"):
            rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
            draw_glow(surface, PINK, rect.center, 25, 2)
            pygame.draw.rect(surface, (73, 22, 79), rect, border_radius=5)
            pygame.draw.rect(surface, PINK, rect, 3, border_radius=5)
            pygame.draw.line(surface, (255, 175, 225), (rect.left + 8, rect.top + 8), (rect.right - 8, rect.bottom - 8), 2)
            pygame.draw.line(surface, (255, 175, 225), (rect.right - 8, rect.top + 8), (rect.left + 8, rect.bottom - 8), 2)
        else:
            if self.kind == "airspike":
                points = [(int(self.x), int(self.y)), (int(self.x + self.size / 2), int(self.y + self.size)), (int(self.x + self.size), int(self.y))]
            else:
                points = [(int(self.x), int(self.y + self.size)), (int(self.x + self.size / 2), int(self.y)), (int(self.x + self.size), int(self.y + self.size))]
            draw_glow(surface, PINK, (int(self.x + self.size / 2), int(self.y + self.size / 2)), 24, 2)
            pygame.draw.polygon(surface, (100, 25, 89), points)
            pygame.draw.polygon(surface, PINK, points, 3)
            if self.kind == "airspike":
                pygame.draw.line(surface, (255, 190, 230), (int(self.x + self.size / 2), int(self.y + self.size - 9)), (int(self.x + self.size / 2), int(self.y + 8)), 2)
            else:
                pygame.draw.line(surface, (255, 190, 230), (int(self.x + self.size / 2), int(self.y + 8)), (int(self.x + self.size / 2), int(self.y + self.size - 7)), 2)


class Coin:
    def __init__(self, x, y):
        self.x = float(x)
        self.base_y = float(y)
        self.phase = random.uniform(0, math.tau)
        self.radius = 12
        self.taken = False

    @property
    def y(self):
        return self.base_y + math.sin(self.phase) * 5

    def update(self, speed, dt):
        self.x -= speed * dt
        self.phase += 0.08 * dt

    def collides(self, rect):
        coin_rect = pygame.Rect(int(self.x - 10), int(self.y - 10), 20, 20)
        return rect.colliderect(coin_rect)

    def draw(self, surface):
        center = (int(self.x), int(self.y))
        draw_glow(surface, GOLD, center, 20, 2)
        pygame.draw.circle(surface, (141, 87, 17), center, self.radius + 2)
        pygame.draw.circle(surface, GOLD, center, self.radius)
        pygame.draw.circle(surface, (255, 244, 174), center, self.radius - 4, 2)
        pygame.draw.circle(surface, (255, 255, 225), (center[0] - 3, center[1] - 4), 2)


# =============================================================================
# GAME STATE AND SPAWNING
# =============================================================================
selected_mode = "MEDIUM"
secret_input = ""
secret_typing = False
notice_text = ""
notice_timer = 0


def new_game(dev_course=False):
    settings = MODE_SETTINGS[selected_mode]
    return {
        "player": Player(profile["skin"], selected_mode),
        "obstacles": [],
        "coins": [],
        "particles": [],
        "score": 0,
        "run_coins": 0,
        "speed": settings["speed"],
        "base_speed": settings["speed"],
        "spawn_timer": 68,
        "world_offset": 0.0,
        "state": "playing",
        "dev": dev_course,
        "flight_held": False,
        "rewarded": False,
        "frames": 0,
    }


game = {"state": "menu", "world_offset": 0.0, "score": 0, "best": profile["best"], "obstacles": [], "coins": [], "particles": []}


def start_game(dev_course=False):
    global game
    game = new_game(dev_course)


def spawn_obstacles():
    x = WIDTH + 35
    if game["dev"]:
        # The secret course adds aerial hazards, tighter patterns and paired blocks.
        pattern = random.choice(["double", "block", "air", "mixed", "triple"])
        if pattern == "double":
            game["obstacles"].append(Obstacle(x, "spike", 42))
            game["obstacles"].append(Obstacle(x + 48, "spike", 42))
        elif pattern == "block":
            game["obstacles"].append(Obstacle(x, "block", 44))
            game["obstacles"].append(Obstacle(x + 84, "spike", 40))
        elif pattern == "air":
            game["obstacles"].append(Obstacle(x, "airblock", 42, random.randint(230, 350)))
            game["obstacles"].append(Obstacle(x + 72, "airspike", 42, random.randint(160, 260)))
        elif pattern == "mixed":
            game["obstacles"].append(Obstacle(x, "spike", 40))
            game["obstacles"].append(Obstacle(x + 100, "airblock", 38, random.randint(240, 330)))
        else:
            game["obstacles"].append(Obstacle(x, "spike", 38))
            game["obstacles"].append(Obstacle(x + 43, "spike", 38))
            game["obstacles"].append(Obstacle(x + 86, "spike", 38))
    else:
        roll = random.random()
        if roll < 0.53:
            game["obstacles"].append(Obstacle(x, "spike", random.choice((38, 42, 46))))
        elif roll < 0.76:
            game["obstacles"].append(Obstacle(x, "block", random.choice((38, 42))))
        elif roll < 0.92:
            game["obstacles"].append(Obstacle(x, "spike", 40))
            game["obstacles"].append(Obstacle(x + 47, "spike", 40))
        else:
            game["obstacles"].append(Obstacle(x, "airblock", 36, random.randint(255, 355)))

    # Some coin trails reward risky jumps or precise flying.
    if random.random() < (0.40 if game["dev"] else 0.34):
        coin_y = random.randint(315, 405)
        for i in range(random.choice((1, 1, 2, 3))):
            game["coins"].append(Coin(x + 80 + i * 34, coin_y - (i % 2) * 10))


def finish_run():
    if game.get("rewarded"):
        return
    game["rewarded"] = True
    bonus = game["score"] // 10
    profile["coins"] += bonus
    profile["best"] = max(profile["best"], game["score"])
    game["bonus_coins"] = bonus
    save_profile()


# =============================================================================
# HUD, MENU, SHOP
# =============================================================================
def draw_hud():
    draw_text(f"SCORE  {game['score']}", FONT_MED, WHITE, (112, 34))
    draw_text(f"BEST  {max(profile['best'], game['score'])}", FONT_SMALL, MUTED, (90, 69))
    draw_text(f"COINS  {profile['coins']}", FONT_MED, GOLD, (WIDTH - 115, 34))
    mode_label = "AYYAN'S CIRCUIT" if game.get("dev") else selected_mode
    draw_text(mode_label, FONT_TINY, PURPLE if game.get("dev") else CYAN, (WIDTH // 2, 31))
    if game["player"].is_flying:
        draw_text("FLIGHT BOT: HOLD SPACE TO RISE", FONT_TINY, PINK, (WIDTH // 2, 62))


def draw_menu():
    draw_background(game.get("world_offset", 0))
    # Decorative cube and sound rings.
    pulse = 42 + int(4 * math.sin(pygame.time.get_ticks() * 0.004))
    draw_glow(screen, CYAN, (WIDTH // 2, 145), 68, 4)
    cube = pygame.Surface((pulse, pulse), pygame.SRCALPHA)
    pygame.draw.rect(cube, CYAN, (1, 1, pulse - 2, pulse - 2), border_radius=8)
    pygame.draw.rect(cube, (230, 255, 255), (7, 7, pulse - 14, pulse - 14), 2, border_radius=5)
    pygame.draw.line(cube, (7, 35, 61), (12, 15), (pulse - 12, 15), 4)
    pygame.draw.line(cube, (7, 35, 61), (12, 27), (pulse - 12, 27), 4)
    rotated = pygame.transform.rotate(cube, pygame.time.get_ticks() * 0.035)
    screen.blit(rotated, rotated.get_rect(center=(WIDTH // 2, 145)))

    draw_text("CYBER DASH", FONT_HUGE, CYAN, (WIDTH // 2, 62))
    draw_text("NEON RHYTHM RUNNER", FONT_SMALL, MUTED, (WIDTH // 2, 205))
    draw_text(f"BANK  {profile['coins']} COINS", FONT_SMALL, GOLD, (WIDTH - 135, 30))
    draw_text(f"BEST  {profile['best']}", FONT_SMALL, WHITE, (115, 30))

    draw_text("SELECT DIFFICULTY", FONT_SMALL, MUTED, (WIDTH // 2, 250), shadow=False)
    card_w, card_h, gap = 185, 58, 18
    total = card_w * 4 + gap * 3
    start_x = (WIDTH - total) // 2
    mode_colors = {"EASY": (76, 240, 155), "MEDIUM": CYAN, "HARD": PINK, "EXTREME": (255, 95, 80)}
    for i, mode in enumerate(MODES):
        rect = pygame.Rect(start_x + i * (card_w + gap), 278, card_w, card_h)
        draw_button(rect, mode, mode_colors[mode], enabled=True, small=True)
        if selected_mode == mode:
            pygame.draw.rect(screen, WHITE, rect.inflate(6, 6), 2, border_radius=12)

    draw_button((350, 354, 260, 60), "PLAY  ▶", CYAN)
    draw_button((205, 430, 235, 48), "SKINS  /  SHOP", PURPLE, small=True)
    draw_button((520, 430, 235, 48), "GRAPHICS  ⚙", CYAN, small=True)

    if profile.get("dev_unlocked"):
        draw_button((350, 500, 260, 42), "AYYAN'S DEV COURSE  ★", GOLD, small=True)
        secret_hint_y = 565
    else:
        draw_button((350, 500, 260, 42), "ENTER SECRET CODE  [C]", PINK, small=True)
        secret_hint_y = 565

    if secret_typing:
        panel = pygame.Rect(190, 220, 580, 250)
        pygame.draw.rect(screen, (7, 13, 35), panel, border_radius=16)
        pygame.draw.rect(screen, PINK, panel, 2, border_radius=16)
        draw_text("DEVELOPER ACCESS", FONT_BIG, PINK, (WIDTH // 2, 265))
        draw_text("Type the developer name, then press ENTER", FONT_SMALL, WHITE, (WIDTH // 2, 315), shadow=False)
        shown = secret_input if secret_input else "_"
        draw_text(shown[-28:], FONT_MED, CYAN, (WIDTH // 2, 375), shadow=False)
        draw_text("BACKSPACE = erase     ESC = cancel", FONT_TINY, MUTED, (WIDTH // 2, 425), shadow=False)
    else:
        draw_text("SECRET: press C, type the developer name, press ENTER", FONT_TINY, MUTED, (WIDTH // 2, secret_hint_y), shadow=False)

    audio_label = "MUSIC: ON" if profile.get("music_on", True) else "MUSIC: OFF"
    draw_text(audio_label + " (M)   •   GRAPHICS (G)   •   ESC TO QUIT", FONT_TINY, MUTED, (WIDTH // 2, 590), shadow=False)
    if notice_timer > 0 and notice_text:
        draw_text(notice_text, FONT_SMALL, GOLD, (WIDTH // 2, 535))


def draw_settings():
    draw_background(game.get("world_offset", 0))
    graphics = profile["graphics"]
    draw_text("GRAPHICS SETTINGS", FONT_HUGE, CYAN, (WIDTH // 2, 72))
    draw_text("Tune the visuals for your PC", FONT_SMALL, MUTED, (WIDTH // 2, 120), shadow=False)

    draw_text("QUALITY PRESET", FONT_MED, WHITE, (WIDTH // 2, 180), shadow=False)
    qualities = ["LOW", "MEDIUM", "HIGH", "ULTRA"]
    q_w, q_gap = 150, 20
    q_start = (WIDTH - (q_w * 4 + q_gap * 3)) // 2
    for i, quality in enumerate(qualities):
        rect = pygame.Rect(q_start + i * (q_w + q_gap), 205, q_w, 55)
        color = {"LOW": (110, 190, 210), "MEDIUM": CYAN, "HIGH": PURPLE, "ULTRA": GOLD}[quality]
        draw_button(rect, quality, color, small=True)
        if graphics["quality"] == quality:
            pygame.draw.rect(screen, WHITE, rect.inflate(6, 6), 2, border_radius=12)

    toggles = [
        ("glow", "NEON GLOW"),
        ("particles", "PARTICLE EFFECTS"),
        ("animated_background", "MOVING BACKGROUND"),
        ("fullscreen", "FULLSCREEN"),
    ]
    toggle_positions = [(185, 300), (505, 300), (185, 385), (505, 385)]
    for (key, label), (x, y) in zip(toggles, toggle_positions):
        enabled = graphics.get(key, False)
        color = CYAN if enabled else MUTED
        draw_button((x, y, 270, 58), f"{label}: {'ON' if enabled else 'OFF'}", color, small=True)

    draw_button((380, 485, 200, 52), "BACK  [ESC]", PINK, small=True)
    draw_text("LOW = smoother on older PCs     ULTRA = extra visual detail", FONT_TINY, MUTED, (WIDTH // 2, 565), shadow=False)


def handle_settings_click(pos):
    graphics = profile["graphics"]
    qualities = ["LOW", "MEDIUM", "HIGH", "ULTRA"]
    q_w, q_gap = 150, 20
    q_start = (WIDTH - (q_w * 4 + q_gap * 3)) // 2
    for i, quality in enumerate(qualities):
        rect = pygame.Rect(q_start + i * (q_w + q_gap), 205, q_w, 55)
        if rect.collidepoint(pos):
            graphics["quality"] = quality
            save_profile()
            play_sfx("buy")
            return

    toggle_positions = {
        "glow": pygame.Rect(185, 300, 270, 58),
        "particles": pygame.Rect(505, 300, 270, 58),
        "animated_background": pygame.Rect(185, 385, 270, 58),
        "fullscreen": pygame.Rect(505, 385, 270, 58),
    }
    for key, rect in toggle_positions.items():
        if rect.collidepoint(pos):
            new_value = not graphics.get(key, False)
            if key == "fullscreen":
                apply_fullscreen(new_value)
            else:
                graphics[key] = new_value
                save_profile()
            play_sfx("buy")
            return
    if pygame.Rect(380, 485, 200, 52).collidepoint(pos):
        game["state"] = "menu"


def draw_shop():
    draw_background(game.get("world_offset", 0))
    draw_text("CYBER GARAGE", FONT_HUGE, PURPLE, (WIDTH // 2, 65))
    draw_text(f"YOUR COINS: {profile['coins']}  ◉", FONT_MED, GOLD, (WIDTH // 2, 118))
    card_w, card_h = 250, 160
    positions = [(85, 160), (355, 160), (625, 160), (85, 345), (355, 345), (625, 345)]
    for (skin_id, skin), (x, y) in zip(SKINS.items(), positions):
        rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(screen, (9, 20, 49), rect, border_radius=13)
        pygame.draw.rect(screen, skin["color"], rect, 2, border_radius=13)
        # Character preview.
        if skin_id == "flybot":
            preview = pygame.Rect(x + 95, y + 15, 58, 38)
            pygame.draw.polygon(screen, (67, 35, 88), [(preview.left, preview.centery), (preview.left + 14, preview.top), (preview.right - 5, preview.top + 3), (preview.right, preview.centery), (preview.right - 5, preview.bottom), (preview.left + 14, preview.bottom)])
            pygame.draw.polygon(screen, skin["color"], [(preview.left, preview.centery), (preview.left + 14, preview.top), (preview.right - 5, preview.top + 3), (preview.right, preview.centery), (preview.right - 5, preview.bottom), (preview.left + 14, preview.bottom)], 3)
            pygame.draw.circle(screen, CYAN, (x + 126, y + 34), 5)
        else:
            preview = pygame.Rect(x + 105, y + 14, 40, 40)
            pygame.draw.rect(screen, skin["color"], preview, border_radius=7)
            pygame.draw.rect(screen, skin["edge"], preview, 2, border_radius=7)
        draw_text(skin["name"], FONT_SMALL, WHITE, (x + card_w // 2, y + 76), shadow=False)
        desc = skin["desc"]
        draw_text(desc, FONT_TINY, MUTED, (x + card_w // 2, y + 98), shadow=False)
        owned = skin_id in profile["owned_skins"]
        equipped = profile["skin"] == skin_id
        if equipped:
            label, btn_color, enabled = "EQUIPPED", skin["color"], False
        elif owned:
            label, btn_color, enabled = "EQUIP", CYAN, True
        else:
            label, btn_color, enabled = f"BUY  {skin['price']} COINS", GOLD, profile["coins"] >= skin["price"]
        draw_button((x + 30, y + 116, 190, 34), label, btn_color, enabled, small=True)

    draw_button((380, 535, 200, 48), "BACK  [ESC]", CYAN, small=True)
    draw_text("Flying Robot: while playing, HOLD SPACE / UP / mouse to rise", FONT_TINY, PINK, (WIDTH // 2, 585), shadow=False)


def draw_game_overlay(title, subtitle, hint, color=CYAN):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((2, 4, 20, 190))
    screen.blit(shade, (0, 0))
    draw_text(title, FONT_HUGE, color, (WIDTH // 2, 205))
    draw_text(subtitle, FONT_MED, WHITE, (WIDTH // 2, 275))
    draw_text(hint, FONT_SMALL, MUTED, (WIDTH // 2, 345), shadow=False)


# =============================================================================
# INPUT HELPERS
# =============================================================================
def cycle_mode(direction):
    global selected_mode
    index = MODES.index(selected_mode)
    selected_mode = MODES[(index + direction) % len(MODES)]


def handle_shop_click(pos):
    positions = [(85, 160), (355, 160), (625, 160), (85, 345), (355, 345), (625, 345)]
    for (skin_id, skin), (x, y) in zip(SKINS.items(), positions):
        button_rect = pygame.Rect(x + 30, y + 116, 190, 34)
        if button_rect.collidepoint(pos):
            if skin_id in profile["owned_skins"]:
                profile["skin"] = skin_id
                play_sfx("buy")
                save_profile()
            elif profile["coins"] >= skin["price"]:
                profile["coins"] -= skin["price"]
                profile["owned_skins"].append(skin_id)
                profile["skin"] = skin_id
                play_sfx("buy")
                save_profile()
            else:
                show_notice(f"YOU NEED {skin['price'] - profile['coins']} MORE COINS")
            return
    if pygame.Rect(380, 535, 200, 48).collidepoint(pos):
        game["state"] = "menu"


def show_notice(message):
    global notice_text, notice_timer
    notice_text = message
    notice_timer = 180


def check_secret_code():
    global secret_typing, secret_input
    if secret_input.strip().casefold() == "syed ayyan ahmed".casefold():
        if not profile.get("dev_unlocked"):
            profile["dev_unlocked"] = True
            save_profile()
            play_sfx("unlock")
            show_notice("SECRET COURSE UNLOCKED! AYYAN'S CIRCUIT")
        else:
            show_notice("DEVELOPER COURSE ALREADY UNLOCKED")
    else:
        show_notice("CODE NOT RECOGNISED - TRY AGAIN")
    secret_input = ""
    secret_typing = False
    try:
        pygame.key.stop_text_input()
    except (AttributeError, pygame.error):
        pass


# =============================================================================
# MAIN LOOP
# =============================================================================
running = True
while running:
    dt = min(clock.tick(FPS) / 16.6667, 2.0)
    if notice_timer > 0:
        notice_timer -= dt

    for event in pygame.event.get():
        # SDL/Pygame can report phone taps as FINGER events. Convert them to
        # mouse clicks so the existing menus, shop, settings, and jump work.
        if event.type == getattr(pygame, "FINGERDOWN", -999):
            event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"pos": (int(event.x * WIDTH), int(event.y * HEIGHT)), "button": 1},
            )
        elif event.type == getattr(pygame, "FINGERUP", -999):
            event = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1})

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            state = game["state"]
            if state == "menu" and secret_typing:
                if event.key == pygame.K_ESCAPE:
                    secret_typing = False
                    secret_input = ""
                    try:
                        pygame.key.stop_text_input()
                    except (AttributeError, pygame.error):
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    secret_input = secret_input[:-1]
                elif event.key == pygame.K_RETURN:
                    check_secret_code()
                elif event.unicode and event.unicode.isprintable() and len(secret_input) < 32:
                    secret_input += event.unicode
                continue

            if event.key == pygame.K_ESCAPE:
                if state == "menu":
                    running = False
                elif state in ("shop", "settings"):
                    game["state"] = "menu"
                elif state in ("playing", "paused", "gameover"):
                    game["state"] = "menu"
                    game["flight_held"] = False
            elif event.key == pygame.K_m:
                set_music(not profile.get("music_on", True))
                show_notice("MUSIC " + ("ON" if profile["music_on"] else "OFF"))
            elif state == "menu":
                if event.key == pygame.K_c:
                    secret_typing = True
                    secret_input = ""
                elif event.key == pygame.K_LEFT:
                    cycle_mode(-1)
                elif event.key == pygame.K_RIGHT:
                    cycle_mode(1)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    selected_mode = MODES[event.key - pygame.K_1]
                elif event.key == pygame.K_s:
                    game["state"] = "shop"
                elif event.key == pygame.K_g:
                    game["state"] = "settings"
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    start_game(False)
            elif state == "playing":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if game["player"].is_flying:
                        game["flight_held"] = True
                    else:
                        game["player"].jump()
                elif event.key == pygame.K_p:
                    game["state"] = "paused"
                    game["flight_held"] = False
                elif event.key == pygame.K_r:
                    start_game(game.get("dev", False))
            elif state == "paused":
                if event.key == pygame.K_p or event.key == pygame.K_RETURN:
                    game["state"] = "playing"
                elif event.key == pygame.K_r:
                    start_game(game.get("dev", False))
            elif state == "gameover":
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                    start_game(game.get("dev", False))
                elif event.key == pygame.K_m:
                    game["state"] = "menu"
            elif state == "settings":
                if event.key in (pygame.K_RETURN, pygame.K_BACKSPACE):
                    game["state"] = "menu"
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    profile["graphics"]["quality"] = ["LOW", "MEDIUM", "HIGH", "ULTRA"][event.key - pygame.K_1]
                    save_profile()
                elif event.key == pygame.K_o:
                    profile["graphics"]["glow"] = not profile["graphics"]["glow"]
                    save_profile()
                elif event.key == pygame.K_t:
                    profile["graphics"]["particles"] = not profile["graphics"]["particles"]
                    save_profile()
                elif event.key == pygame.K_b:
                    profile["graphics"]["animated_background"] = not profile["graphics"]["animated_background"]
                    save_profile()
                elif event.key == pygame.K_f:
                    apply_fullscreen(not profile["graphics"]["fullscreen"])
            elif state == "shop" and event.key in (pygame.K_RETURN, pygame.K_BACKSPACE):
                game["state"] = "menu"

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) and game.get("player") and game["player"].is_flying:
                game["flight_held"] = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            state = game["state"]
            if state == "menu" and not secret_typing:
                card_w, card_h, gap = 185, 58, 18
                start_x = (WIDTH - (card_w * 4 + gap * 3)) // 2
                clicked_mode = False
                for i, mode in enumerate(MODES):
                    rect = pygame.Rect(start_x + i * (card_w + gap), 278, card_w, card_h)
                    if rect.collidepoint(pos):
                        selected_mode = mode
                        clicked_mode = True
                        break
                if not clicked_mode:
                    if pygame.Rect(350, 354, 260, 60).collidepoint(pos):
                        start_game(False)
                    elif pygame.Rect(205, 430, 235, 48).collidepoint(pos):
                        game["state"] = "shop"
                    elif pygame.Rect(520, 430, 235, 48).collidepoint(pos):
                        game["state"] = "settings"
                    elif pygame.Rect(350, 500, 260, 42).collidepoint(pos):
                        if profile.get("dev_unlocked"):
                            start_game(True)
                        else:
                            secret_typing = True
                            secret_input = ""
                            try:
                                pygame.key.start_text_input()
                            except (AttributeError, pygame.error):
                                pass
            elif state == "shop":
                handle_shop_click(pos)
            elif state == "settings":
                handle_settings_click(pos)
            elif state == "playing":
                if game["player"].is_flying:
                    game["flight_held"] = True
                else:
                    game["player"].jump()
            elif state == "gameover":
                start_game(game.get("dev", False))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if game.get("player") and game["player"].is_flying:
                game["flight_held"] = False

    # -------------------------------------------------------------------------
    # Update game simulation
    # -------------------------------------------------------------------------
    if game["state"] == "playing":
        player = game["player"]
        settings = MODE_SETTINGS[selected_mode]
        game["frames"] += dt
        game["world_offset"] += game["speed"] * dt
        game["speed"] = min(game["base_speed"] + 2.1, game["base_speed"] + game["score"] * 0.008)

        player.update(game["particles"], dt, game["flight_held"])

        game["spawn_timer"] -= dt
        if game["spawn_timer"] <= 0:
            spawn_obstacles()
            low, high = settings["gap"]
            gap = random.randint(low, high)
            if game["dev"]:
                gap = max(settings["min_gap"] - 5, gap - 7)
            game["spawn_timer"] = max(settings["min_gap"], gap - game["score"] * 0.035)

        for obstacle in game["obstacles"]:
            obstacle.update(game["speed"], dt)
            if not obstacle.passed and obstacle.x + obstacle.size < player.x:
                obstacle.passed = True
                game["score"] += 1
            if obstacle.collides(player.rect):
                game["state"] = "gameover"
                game["flight_held"] = False
                play_sfx("crash")
                if profile.get("graphics", {}).get("particles", True):
                    crash_particles = 12 if profile.get("graphics", {}).get("quality") == "LOW" else 32
                    for _ in range(crash_particles):
                        game["particles"].append(Particle(player.x + 20, player.y + 20, random.choice((player.color, PINK, PURPLE))))
                finish_run()
                break

        for coin in game["coins"]:
            coin.update(game["speed"], dt)
            if not coin.taken and coin.collides(player.rect):
                coin.taken = True
                profile["coins"] += 1
                game["run_coins"] += 1
                play_sfx("coin")
                save_profile()
        game["obstacles"] = [o for o in game["obstacles"] if o.x + o.size > -25]
        game["coins"] = [c for c in game["coins"] if c.x > -25 and not c.taken]

        for particle in game["particles"]:
            particle.update(dt)
        game["particles"] = [p for p in game["particles"] if p.life > 0]

    elif game["state"] == "gameover":
        for particle in game["particles"]:
            particle.update(dt)
        game["particles"] = [p for p in game["particles"] if p.life > 0]

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------
    draw_background(game.get("world_offset", 0), tint=game.get("dev", False))

    for obstacle in game.get("obstacles", []):
        obstacle.draw(screen)
    for coin in game.get("coins", []):
        coin.draw(screen)
    for particle in game.get("particles", []):
        particle.draw(screen)

    if game["state"] in ("playing", "paused", "gameover"):
        if game["state"] != "gameover":
            game["player"].draw(screen)
        draw_hud()

    if game["state"] == "menu":
        draw_menu()
    elif game["state"] == "shop":
        draw_shop()
    elif game["state"] == "settings":
        draw_settings()
    elif game["state"] == "paused":
        draw_game_overlay("PAUSED", f"Score: {game['score']}   •   Coins: {game['run_coins']}", "Press P / ENTER to continue   •   ESC for menu", PURPLE)
    elif game["state"] == "gameover":
        draw_game_overlay("CRASHED!", f"Score: {game['score']}   •   Run coins: {game['run_coins']}   •   Bonus: +{game.get('bonus_coins', 0)}", "SPACE / R = retry     ESC = menu", PINK)

    pygame.display.flip()

pygame.quit()
sys.exit()
