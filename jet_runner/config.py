# Configuration constants for Jet Runner
WIDTH = 480
HEIGHT = 640
FPS = 60

PLAYER_SPEED = 300.0  # pixels per second
BULLET_SPEED = 500.0
ENEMY_MIN_SPEED = 80.0
ENEMY_MAX_SPEED = 200.0
SCENERY_MIN_SPEED = 60.0
SCENERY_MAX_SPEED = 140.0

PLAYER_HEALTH = 5
PLAYER_FIRE_COOLDOWN = 0.25  # seconds

SPAWN_ENEMY_INTERVAL = 1.2  # seconds
SPAWN_OBSTACLE_INTERVAL = 0.9
SPAWN_SCENERY_INTERVAL = 0.5

ENEMY_FIRE_CHANCE = 0.25  # chance per firing opportunity
ENEMY_BULLET_SPEED = 220.0

# Colors
COLOR_BG = (10, 10, 30)
COLOR_PLAYER = (60, 180, 200)
COLOR_BULLET = (255, 220, 20)
COLOR_ENEMY = (200, 60, 80)
COLOR_OBSTACLE = (120, 120, 120)
COLOR_SCENERY = (80, 100, 140)

# New enemy appearance colors (used for 'space monster' drawing)
COLOR_ENEMY_BODY = (180, 80, 150)
COLOR_ENEMY_EYE = (255, 255, 255)
COLOR_ENEMY_PUPIL = (20, 20, 30)
COLOR_ENEMY_MOUTH = (30, 10, 40)
COLOR_ENEMY_OUTLINE = (90, 30, 80)

# Optional palettes: tuples of (body, eye, pupil, mouth, outline)
ENEMY_PALETTES = [
    ((180, 80, 150), (255, 255, 255), (20, 20, 30), (30, 10, 40), (90, 30, 80)),  # purple
    ((80, 160, 200), (255, 255, 255), (8, 20, 30), (10, 60, 90), (30, 80, 100)),   # teal
    ((200, 120, 60), (255, 255, 255), (30, 20, 10), (80, 30, 10), (120, 60, 30)),  # orange
    ((120, 200, 100), (255, 255, 255), (10, 30, 10), (30, 70, 20), (50, 120, 50)), # green
    ((220, 80, 120), (255, 255, 255), (20, 10, 20), (80, 10, 40), (140, 50, 80)),  # pink
]

# Asteroid color options (body, shadow/outline)
ASTEROID_PALETTES = [
    ((120, 120, 120), (80, 80, 80)),   # neutral gray
    ((150, 130, 100), (100, 80, 60)),  # brownish
    ((170, 170, 150), (110, 110, 90)), # pale rock
    ((140, 160, 180), (90, 110, 130)), # bluish rock
]
