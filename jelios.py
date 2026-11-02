
#!/usr/bin/env python3
"""
JEliOS — early desktop prototype.

Run with: python3 jelios.py
Requires pygame.
Persistent state: ~/.config/jelios/state.json
"""

import json
import random
import sys
import time
from pathlib import Path

import pygame
import numpy as np

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

WIDTH, HEIGHT = 640, 480
FPS = 60

BG = (18, 22, 24)
FG = (204, 220, 204)
DIM = (111, 137, 119)
ACCENT = (169, 201, 170)
WARNING = (231, 235, 222)

APP_DIR = Path.home() / ".config" / "jelios"
STATE_FILE = APP_DIR / "state.json"


# --------------------------------------------------
# MENUS
# --------------------------------------------------

MENU_ITEMS = [
    "Emulators",
    "Settings",
    "Creator",
    "Past Creator",
    "Power Off",
]

SETTINGS_ITEMS = [
    "Display",
    "Audio",
    "Controls",
    "Layout",
    "Language",
    "System",
]

DISPLAY_ITEMS = [
    "Brightness",
    "Colorblind Mode",
    "Monochrome",
    "Extra Retro",
    "CRT Scanlines",
]

COLORBLIND_ITEMS = [
    "Protanopia",
    "Deuteranopia",
    "Tritanopia",
    "Reset All",
]


# --------------------------------------------------
# SAVED STATE
# --------------------------------------------------

def load_and_increment_state():
    APP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        state = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        state = {
            "boot_count": 0,
            "past_creator_visits": 0,
            "story_flags": {},
        }

    state.setdefault("boot_count", 0)
    state.setdefault("past_creator_visits", 0)
    state.setdefault("story_flags", {})
    state.setdefault("brightness", 100)
    state.setdefault("colorblind_mode", False)
    colorblind_types = state.get("colorblind_types", {})
    if not isinstance(colorblind_types, dict):
        colorblind_types = {}

    # Migrate the old misspelled key without losing its saved value.
    if "Trianopia" in colorblind_types:
        colorblind_types.setdefault(
            "Tritanopia", colorblind_types["Trianopia"]
        )
        colorblind_types.pop("Trianopia", None)

    colorblind_types.setdefault("Protanopia", False)
    colorblind_types.setdefault("Deuteranopia", False)
    colorblind_types.setdefault("Tritanopia", False)
    state["colorblind_types"] = colorblind_types

    state["boot_count"] += 1

    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )
    temporary.replace(STATE_FILE)

    return state


def save_state(state):
    APP_DIR.mkdir(parents=True, exist_ok=True)

    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )
    temporary.replace(STATE_FILE)


# --------------------------------------------------
# SHARED DRAWING FUNCTIONS
# --------------------------------------------------

def draw_centered(surface, font, text, y, color=FG):
    rendered = font.render(text, True, color)
    surface.blit(
        rendered,
        (WIDTH // 2 - rendered.get_width() // 2, y),
    )


def draw_static(surface):
    surface.fill((8, 10, 10))

    for y in range(0, HEIGHT, 4):
        shade = random.choice([
            (27, 34, 31),
            (58, 70, 62),
            (102, 117, 103),
            (15, 18, 17),
        ])

        pygame.draw.rect(
            surface,
            shade,
            (0, y, WIDTH, random.choice([1, 2, 3])),
        )

    for _ in range(90):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        w = random.randrange(2, 55)
        h = random.choice([1, 2, 3, 5])

        color = random.choice([
            (170, 188, 170),
            (83, 100, 88),
            (220, 225, 214),
        ])

        pygame.draw.rect(
            surface,
            color,
            (x, y, min(w, WIDTH - x), h),
        )

    for _ in range(3):
        y = random.randrange(HEIGHT)

        pygame.draw.rect(
            surface,
            random.choice([
                (190, 205, 190),
                (50, 65, 55),
            ]),
            (0, y, WIDTH, random.randrange(2, 9)),
        )


def draw_help_glitch(surface, font_big, elapsed):
    draw_static(surface)

    jitter_x = random.randint(-5, 5)
    jitter_y = random.randint(-3, 3)

    msg_font = pygame.font.Font(None, 32)

    msg = msg_font.render(
        "This isn't right...",
        True,
        WARNING,
    )
    msg2 = msg_font.render(
        "Something is wrong.",
        True,
        WARNING,
    )

    surface.blit(
        msg,
        (
            WIDTH // 2 - msg.get_width() // 2 + jitter_x,
            HEIGHT // 2 - 25 + jitter_y,
        ),
    )

    surface.blit(
        msg2,
        (
            WIDTH // 2 - msg2.get_width() // 2 + jitter_x,
            HEIGHT // 2 + 5 + jitter_y,
        ),
    )

    if random.random() < 0.35:
        y = random.randrange(
            HEIGHT // 2 - 30,
            HEIGHT // 2 + 30,
        )

        pygame.draw.rect(
            surface,
            (8, 10, 10),
            (0, y, WIDTH, random.randint(2, 8)),
        )

    if elapsed < 0.8:
        draw_centered(
            surface,
            pygame.font.Font(None, 20),
            "SIGNAL INTERRUPTED",
            22,
            DIM,
        )


def draw_logo(surface, logo_image, progress):
    surface.fill((0, 0, 0))

    start_y = HEIGHT
    end_y = 0

    progress = max(0.0, min(progress, 1.0))
    eased = 1 - (1 - progress) ** 3
    y = int(start_y + (end_y - start_y) * eased)

    surface.blit(logo_image, (0, y))


# --------------------------------------------------
# MAIN MENU DRAWING
# --------------------------------------------------

def draw_home(surface, font_big, font, small, selected, state):
    surface.fill(BG)

    draw_centered(surface, font_big, "JEliOS", 35, FG)
    pygame.draw.line(
        surface, DIM, (55, 91), (585, 91), 2
    )

    draw_centered(
        surface,
        small,
        f"BOOT {state['boot_count']:03d}",
        103,
        DIM,
    )

    for i, item in enumerate(MENU_ITEMS):
        y = 155 + i * 48

        if i == selected:
            pygame.draw.rect(
                surface,
                (42, 57, 46),
                (142, y - 5, 356, 36),
                border_radius=3,
            )

            pygame.draw.rect(
                surface,
                ACCENT,
                (142, y - 5, 4, 36),
            )

            color = WARNING
            prefix = "> "
        else:
            color = FG
            prefix = "  "

        rendered = font.render(prefix + item, True, color)
        surface.blit(rendered, (170, y))

    draw_centered(
        surface,
        small,
        "UP/DOWN: SELECT     ENTER: OPEN     ESC: QUIT",
        427,
        DIM,
    )


# --------------------------------------------------
# SETTINGS MENU DRAWING
# --------------------------------------------------

def draw_settings(surface, font_big, font, small, selected):
    surface.fill(BG)

    draw_centered(surface, font_big, "SETTINGS", 35, FG)
    pygame.draw.line(
        surface, DIM, (55, 91), (585, 91), 2
    )

    for i, item in enumerate(SETTINGS_ITEMS):
        y = 125 + i * 43

        if i == selected:
            pygame.draw.rect(
                surface,
                (42, 57, 46),
                (142, y - 4, 356, 34),
                border_radius=3,
            )

            color = WARNING
            prefix = "> "
        else:
            color = FG
            prefix = "  "

        rendered = font.render(prefix + item, True, color)
        surface.blit(rendered, (170, y))

    draw_centered(
        surface,
        small,
        "UP/DOWN: SELECT   ENTER: OPEN   ESC: BACK",
        427,
        DIM,
    )


# --------------------------------------------------
# DISPLAY MENU DRAWING
# --------------------------------------------------

def draw_display(surface, font_big, font, small, selected, brightness, colorblind_mode):
    surface.fill(BG)

    draw_centered(surface, font_big, "DISPLAY", 35, FG)
    pygame.draw.line(
        surface, DIM, (55, 91), (585, 91), 2
    )

    for i, item in enumerate(DISPLAY_ITEMS):
        y = 125 + i * 43

        if i == selected:
            pygame.draw.rect(
                surface,
                (42, 57, 46),
                (142, y - 4, 356, 34),
                border_radius=3,
            )

            color = WARNING
            prefix = "> "
        else:
            color = FG
            prefix = "  "
            
        if item == "Brightness":
            label = f"{item}: {brightness}%"
        elif item == "Colorblind Mode":
            status = "ON" if colorblind_mode else "OFF"
            label = f"{item}: {status}"
        else:
            label = item
            
        rendered = font.render(prefix + label, True, color)
        surface.blit(rendered, (170, y))

    draw_centered(
        surface,
        small,
        "UP/DOWN: SELECT   ENTER: OPEN   ESC: BACK",
        427,
        DIM,
    )

def draw_colorblind_menu(surface, font, small, selected, colorblind_types):
    panel = pygame.Rect(320, 145, 285, 220)

    # Solid background hides the Display menu beneath it.
    pygame.draw.rect(surface, BG, panel, border_radius=5)
    pygame.draw.rect(surface, ACCENT, panel, width=2, border_radius=5)

    for i, item in enumerate(COLORBLIND_ITEMS):
        y = 195 + i * 37

        if i == selected:
            pygame.draw.rect(
                surface,
                (42, 57, 46),
                (panel.x + 10, y - 4, panel.width - 20, 30),
                border_radius=3,
            )
            color = WARNING
            prefix = "> "
        else:
            color = FG
            prefix = "  "

        if item == "Reset All":
            label = item
        else:
            status = "ON" if colorblind_types[item] else "OFF"
            label = f"{item}: {status}"

        rendered = font.render(prefix + label, True, color)
        surface.blit(rendered, (panel.x + 18, y))


def apply_colorblind_filter(surface, colorblind_types):
    pixels = pygame.surfarray.pixels3d(surface)
    rgb = pixels.astype(np.float32).copy()

    # Experimental color adjustments for improved color separation.
    if colorblind_types["Protanopia"]:
        rgb[:, :, 0] = np.clip(
            rgb[:, :, 0] + 0.15 * rgb[:, :, 2], 0, 255
        )

    if colorblind_types["Deuteranopia"]:
        rgb[:, :, 1] = np.clip(
            rgb[:, :, 1] + 0.15 * rgb[:, :, 0], 0, 255
        )

    if colorblind_types["Tritanopia"]:
        rgb[:, :, 2] = np.clip(
            rgb[:, :, 2] * 0.8, 0, 255
        )
        rgb[:, :, 0] = np.clip(
            rgb[:, :, 0] + 0.15 * rgb[:, :, 2], 0, 255
        )

    pixels[:] = rgb.astype(np.uint8)
    del pixels

# --------------------------------------------------
# MESSAGE SCREEN DRAWING
# --------------------------------------------------

def draw_message(surface, font, small, lines, title=""):
    surface.fill((8, 10, 10))

    if title:
        draw_centered(surface, small, title, 105, DIM)

    for i, line in enumerate(lines):
        draw_centered(
            surface,
            font,
            line,
            190 + i * 38,
            FG,
        )

    draw_centered(
        surface,
        small,
        "ENTER: RETURN",
        405,
        DIM,
    )


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():
    pygame.init()
    pygame.display.set_caption("JEliOS — Prototype")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    logo_path = Path(__file__).resolve().parent / "logo.png"
    logo_image = pygame.image.load(str(logo_path)).convert()
    logo_image = pygame.transform.smoothscale(
        logo_image,
        (WIDTH, HEIGHT),
    )

    clock = pygame.time.Clock()

    font_big = pygame.font.Font(None, 64)
    font = pygame.font.Font(None, 31)
    small = pygame.font.Font(None, 19)

    state = load_and_increment_state()
    boot_count = state["boot_count"]

    if boot_count == 1:
        boot_mode = "first"
    elif boot_count == 5:
        boot_mode = "fifth"
    else:
        boot_mode = "normal"

    if boot_mode == "first":
        boot_stage = "aelita"
    elif boot_mode == "fifth":
        boot_stage = "flash"
    else:
        boot_stage = "scroll"

    stage_started = time.monotonic()

    selected = 0
    settings_selected = 0
    display_selected = 0
    brightness_selected = 0
    colorblind_selected = 0
    
    page = "boot"
    message_lines = []
    running = True

    # --------------------------------------------------
    # EVENT HANDLING
    # --------------------------------------------------

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # First-boot and fifth-boot story events
                if page == "boot" and boot_stage == "aelita":
                    if boot_mode == "first":
                        boot_stage = "flash"
                    else:
                        boot_stage = "scroll"

                    stage_started = time.monotonic()
                    continue

                # Escape navigation
                if event.key == pygame.K_ESCAPE:
                    if page == "home":
                        running = False
                    elif page == "display":
                        page = "settings"
                    elif page == "colorblind":
                        page = "display"
                    elif page == "settings":
                        page = "home"
                    else:
                        page = "home"

                # Main menu controls
                elif page == "home":

                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected = (
                            selected - 1
                        ) % len(MENU_ITEMS)

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (
                            selected + 1
                        ) % len(MENU_ITEMS)

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                    ):
                        choice = MENU_ITEMS[selected]

                        if choice == "Power Off":
                            running = False

                        elif choice == "Emulators":
                            page = "message"
                            message_lines = [
                                "Emulator support comes next."
                            ]

                        elif choice == "Settings":
                            page = "settings"
                            settings_selected = 0

                        elif choice == "Creator":
                            page = "message"
                            message_lines = [
                                "JEliOS",
                                "Programming: Spencer Donovan",
                                "Graphics / Images: JKG",
                            ]

                        elif choice == "Past Creator":
                            state["past_creator_visits"] += 1
                            save_state(state)

                            page = "message"
                            message_lines = [
                                "PC: Hello? Does this work?",
                                "PC: I... can't see...",
                                "PC: Hello?",
                            ]

                # Settings menu controls
                elif page == "settings":

                    if event.key in (pygame.K_UP, pygame.K_w):
                        settings_selected = (
                            settings_selected - 1
                        ) % len(SETTINGS_ITEMS)

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        settings_selected = (
                            settings_selected + 1
                        ) % len(SETTINGS_ITEMS)

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                    ):
                        choice = SETTINGS_ITEMS[settings_selected]

                        if choice == "Display":
                            page = "display"
                            display_selected = 0
                        else:
                            page = "message"
                            message_lines = [
                                f"{choice} settings coming soon."
                            ]

                # Display menu controls
                elif page == "display":

                    if event.key in (pygame.K_UP, pygame.K_w):
                        display_selected = (
                            display_selected - 1
                        ) % len(DISPLAY_ITEMS)

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        display_selected = (
                            display_selected + 1
                        ) % len(DISPLAY_ITEMS)

                    elif (
                        DISPLAY_ITEMS[display_selected] == "Brightness"
                        and event.key in (pygame.K_LEFT, pygame.K_a)
                    ):
                        state["brightness"] = max(
                            0, state["brightness"] - 5
                        )
                        save_state(state)
                        
                    elif (
                        DISPLAY_ITEMS[display_selected] == "Brightness"
                        and event.key in (pygame.K_RIGHT, pygame.K_d)
                    ):
                        state["brightness"] = min(
                            100, state["brightness"] + 5
                        )
                        save_state(state)
                        
                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                    ):
                        choice = DISPLAY_ITEMS[display_selected]
                        
                        if choice == "Colorblind Mode":
                            page = "colorblind"
                            colorblind_selected = 0
                            
                        elif choice == "Brightness":
                            pass
                            
                        else:
                            page = "message"
                            message_lines = [
                                f"{choice} settings coming soon."
                        ]
                        
                
                # Colorblind submenu controls
                elif page == "colorblind":

                    if event.key in (pygame.K_UP, pygame.K_w):
                        colorblind_selected = (
                            colorblind_selected - 1
                        ) % len(COLORBLIND_ITEMS)

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        colorblind_selected = (
                            colorblind_selected + 1
                        ) % len(COLORBLIND_ITEMS)

                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        choice = COLORBLIND_ITEMS[colorblind_selected]

                        if choice == "Reset All":
                            for mode in state["colorblind_types"]:
                                state["colorblind_types"][mode] = False
                        else:
                            state["colorblind_types"][choice] = (
                                not state["colorblind_types"][choice]
                            )

                        state["colorblind_mode"] = any(
                            state["colorblind_types"].values()
                        )
                        save_state(state)

        # Placeholder message controls
                elif page == "message":

                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                        pygame.K_BACKSPACE,
                    ):
                        page = "home"

        # --------------------------------------------------
        # SCREEN DRAWING
        # --------------------------------------------------

        if page == "boot":
            stage_elapsed = time.monotonic() - stage_started

            if boot_stage == "aelita":

                if boot_mode == "first":
                    draw_help_glitch(
                        screen,
                        font_big,
                        stage_elapsed,
                    )
                else:
                    draw_static(screen)

                    draw_centered(
                        screen,
                        font,
                        "It wasn't your imagination...",
                        HEIGHT // 2 - 35,
                        FG,
                    )

                    draw_centered(
                        screen,
                        font,
                        "Please help.",
                        HEIGHT // 2 + 5,
                        FG,
                    )

            elif boot_stage == "flash":
                screen.fill((0, 0, 0))
                screen.blit(logo_image, (0, 0))

                if stage_elapsed >= 0.15:
                    if boot_mode == "fifth":
                        boot_stage = "aelita"
                    else:
                        boot_stage = "scroll"

                    stage_started = time.monotonic()

            elif boot_stage == "scroll":
                progress = min(1.0, stage_elapsed / 1.5)
                draw_logo(screen, logo_image, progress)

                if stage_elapsed >= 3.0:
                    page = "home"

        elif page == "home":
            draw_home(
                screen,
                font_big,
                font,
                small,
                selected,
                state,
            )

        elif page == "settings":
            draw_settings(
                screen,
                font_big,
                font,
                small,
                settings_selected,
            )

        elif page == "display":
            draw_display(
                screen,
                font_big,
                font,
                small,
                display_selected,
                state["brightness"],
                state["colorblind_mode"],
            )          
        
        # Colorblind submenu open
        elif page == "colorblind":
            draw_display(
                screen,
                font_big,
                font,
                small,
                display_selected,
                state["brightness"],
                state["colorblind_mode"],
            )
            draw_colorblind_menu(
                screen,
                font,
                small,
                colorblind_selected,
                state["colorblind_types"],
            )
        
        elif page == "message":
            draw_message(
                screen,
                font,
                small,
                message_lines,
                "JEliOS / SYSTEM",
            )
            
        ## Colorblind filter loop
        if state ["colorblind_mode"]:
            apply_colorblind_filter(
                screen,
                state["colorblind_types"],clear
                )

## APPLY BRIGHTNESS SETTINGS
        
        brightness_overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )
        brightness_overlay.fill(
            (0, 0, 0, round((100 - state["brightness"]) * 2.55))
        )
        screen.blit(brightness_overlay, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

