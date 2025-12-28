import random
import jet_runner.config as cfg
from jet_runner.entities import Enemy, Obstacle, Scenery


def spawn_enemy(width=cfg.WIDTH):
    x = random.uniform(20, width-20)
    y = -20
    w = random.uniform(24, 48)
    h = random.uniform(18, 36)
    vy = random.uniform(cfg.ENEMY_MIN_SPEED, cfg.ENEMY_MAX_SPEED)
    pattern = random.choice(["straight", "sine", "zigzag"])
    can_fire = random.random() < 0.35
    hp = 1 if not can_fire else random.choice([1, 2])
    return Enemy(x, y, w, h, vy, pattern, can_fire, hp)


def spawn_obstacle(width=cfg.WIDTH):
    x = random.uniform(16, width-16)
    y = -20
    size = random.uniform(22, 48)
    vy = random.uniform(cfg.SCENERY_MIN_SPEED, cfg.SCENERY_MAX_SPEED)
    damage = random.choice([1, 2])
    return Obstacle(x, y, size, vy, damage)


def spawn_scenery(width=cfg.WIDTH, allow_nebulae: bool = False, max_alpha: int = 255):
    x = random.uniform(10, width-10)
    y = -10
    # choose a scenery kind to draw. Include nebula only if allowed.
    if allow_nebulae:
        kinds = ["star", "planet", "comet", "nebula"]
        weights = [40, 25, 20, 15]
    else:
        kinds = ["star", "planet", "comet"]
        weights = [60, 25, 15]
    kind = random.choices(kinds, weights=weights)[0]
    # size and velocity tuned per kind
    if kind == "star":
        w = h = random.uniform(4, 10)
        vy = random.uniform(cfg.SCENERY_MIN_SPEED * 0.5, cfg.SCENERY_MIN_SPEED)
    elif kind == "planet":
        w = h = random.uniform(28, 80)
        vy = random.uniform(cfg.SCENERY_MIN_SPEED * 0.6, cfg.SCENERY_MIN_SPEED * 1.0)
    elif kind == "comet":
        w = random.uniform(8, 18)
        h = random.uniform(6, 12)
        vy = random.uniform(cfg.SCENERY_MIN_SPEED * 1.0, cfg.SCENERY_MAX_SPEED * 1.2)
    elif kind == "nebula":
        w = random.uniform(60, 140)
        h = random.uniform(20, 60)
        vy = random.uniform(cfg.SCENERY_MIN_SPEED * 0.4, cfg.SCENERY_MIN_SPEED * 0.9)

    # determine a depth (parallax) and alpha to make scenery feel in the background
    if kind == "star":
        depth = random.uniform(0.2, 0.5)
    elif kind == "planet":
        depth = random.uniform(0.3, 0.7)
    elif kind == "comet":
        depth = random.uniform(0.6, 1.0)
    elif kind == "nebula":
        depth = random.uniform(0.15, 0.35)
    else:
        depth = 0.5

    # apply depth to vertical speed so far objects move slower
    vy_base = vy
    vy = vy_base * depth

    # alpha (transparency) lower for far (small depth) to appear more background-like
    # cap by max_alpha provided by caller to allow CLI/runtime tuning
    base_alpha = int(60 + depth * 180)
    alpha = int(max(10, min(max_alpha, base_alpha)))

    palette = None
    return Scenery(x, y, w, h, vy, kind=kind, palette=palette, depth=depth, alpha=alpha)
