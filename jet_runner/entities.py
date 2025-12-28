import pygame
import random
import math
from dataclasses import dataclass
from typing import Tuple, List

import jet_runner.config as cfg
import os


@dataclass
class Entity:
    x: float
    y: float
    w: float
    h: float

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.w/2), int(self.y - self.h/2), int(self.w), int(self.h))

    def update(self, dt: float):
        pass

    def draw(self, surf: pygame.Surface):
        pass


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 48, 24)
        self.speed = cfg.PLAYER_SPEED
        self.health = cfg.PLAYER_HEALTH
        self.fire_cooldown = 0.0
        self.score = 0
        # sprite support: try to load assets/jet.png and assets/jet_flame.png; if missing, generate them
        self.sprite = None
        self.flame_sprite = None
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            assets_dir = os.path.join(base_dir, 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            jet_path = os.path.join(assets_dir, 'jet.png')
            flame_path = os.path.join(assets_dir, 'jet_flame.png')
            # attempt load if files exist
            if os.path.exists(jet_path) and os.path.exists(flame_path):
                self.sprite = pygame.image.load(jet_path).convert_alpha()
                self.flame_sprite = pygame.image.load(flame_path).convert_alpha()
            else:
                # generate simple jet sprite
                s = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
                # body
                pygame.draw.polygon(s, cfg.COLOR_PLAYER, [(8,50), (32,10), (56,50), (40,44), (24,44)])
                # cockpit
                pygame.draw.circle(s, (220, 240, 255), (32,22), 6)
                # nozzle highlight
                pygame.draw.polygon(s, (90,90,120), [(24,44),(40,44),(32,54)])
                # save
                try:
                    pygame.image.save(s, jet_path)
                except Exception:
                    pass
                self.sprite = s

                # generate flame sprite
                f = pygame.Surface((20, 30), flags=pygame.SRCALPHA)
                # layered flame shapes
                pygame.draw.polygon(f, (255, 200, 30), [(10,0),(0,18),(20,18)])
                pygame.draw.polygon(f, (255,120,10), [(10,4),(3,20),(17,20)])
                pygame.draw.polygon(f, (200,30,10), [(10,10),(6,24),(14,24)])
                try:
                    pygame.image.save(f, flame_path)
                except Exception:
                    pass
                self.flame_sprite = f
        except Exception:
            # if anything fails, leave sprite None and fall back to polygon drawing
            self.sprite = None
            self.flame_sprite = None

    def move(self, dir_x: float, dt: float):
        self.x += dir_x * self.speed * dt
        self.x = max(self.w/2, min(cfg.WIDTH - self.w/2, self.x))

    def can_fire(self):
        return self.fire_cooldown <= 0.0

    def fire(self):
        self.fire_cooldown = cfg.PLAYER_FIRE_COOLDOWN

    def update(self, dt: float):
        if self.fire_cooldown > 0.0:
            self.fire_cooldown -= dt

    def draw(self, surf: pygame.Surface):
        # If we have a sprite, draw it centered. Otherwise draw the polygon fallback.
        if self.sprite:
            # scale sprite to player's w/h while preserving aspect
            img = self.sprite
            # target width ~ self.w*1.4, target height ~ self.h*2
            target_w = int(self.w * 1.4)
            target_h = int(self.h * 2.0)
            if img.get_width() != target_w or img.get_height() != target_h:
                img = pygame.transform.smoothscale(self.sprite, (target_w, target_h))
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            # draw engine flame behind the jet
            if self.flame_sprite:
                # flame intensity tied to fire cooldown (when firing cooldown small -> showing flame)
                intensity = 1.0 if self.fire_cooldown > 0.0 else 0.6
                # scale flame
                fimg = pygame.transform.smoothscale(self.flame_sprite, (int(target_w*0.3), int(target_h*0.5)))
                # position flame slightly below center
                frect = fimg.get_rect(center=(int(self.x), int(self.y + self.h*0.6)))
                # modulate alpha by intensity
                tmp = fimg.copy()
                try:
                    # create per-surface alpha by filling a transparent surface
                    tmp.fill((255,255,255,int(255*intensity)), special_flags=pygame.BLEND_RGBA_MULT)
                except Exception:
                    pass
                surf.blit(tmp, frect)
            surf.blit(img, rect)
        else:
            pygame.draw.polygon(surf, cfg.COLOR_PLAYER, [
                (self.x, self.y - self.h/2),
                (self.x - self.w/2, self.y + self.h/2),
                (self.x + self.w/2, self.y + self.h/2),
            ])


class Bullet(Entity):
    def __init__(self, x, y, vy, owner: str = "player"):
        super().__init__(x, y, 6, 12)
        self.vy = vy
        self.owner = owner

    def update(self, dt: float):
        self.y += self.vy * dt

    def draw(self, surf: pygame.Surface):
        color = cfg.COLOR_BULLET
        pygame.draw.rect(surf, color, self.rect())


class Scenery(Entity):
    def __init__(self, x, y, w, h, vy, kind: str = None, palette=None, depth: float = 1.0, alpha: int = 255):
        super().__init__(x, y, w, h)
        self.vy = vy
        self.kind = kind
        self.palette = palette
        self.age = 0.0
        self.depth = depth
        # clamp alpha
        self.alpha = max(0, min(255, int(alpha)))
        # set default palette if not provided so draw() can safely unpack values
        if self.palette is None:
            if self.kind == "planet":
                # (fill, ring, highlight)
                self.palette = ( (random.randint(80,230), random.randint(80,230), random.randint(80,230)),
                                 (random.randint(20,120), random.randint(20,120), random.randint(20,120)),
                                 (255,255,255) )
            elif self.kind == "comet":
                self.palette = ( (240,240,200), (200,200,180), (255,255,220) )
            elif self.kind == "nebula":
                # nebula palette: two colors and optional highlight
                self.palette = ( (random.randint(40,160), random.randint(40,160), random.randint(80,200)),
                                 (random.randint(60,200), random.randint(60,200), random.randint(60,200)),
                                 (200,200,255) )
            else:
                # default star colors
                self.palette = ( (255, 255, 200), (255, 220, 120), (255,255,255) )

    def update(self, dt: float):
        self.y += self.vy * dt
        self.age += dt

    def draw(self, surf: pygame.Surface):
        # draw various space objects based on kind onto a temporary surface, then blit with alpha
        rect = self.rect()
        # prepare a temporary surface slightly larger to accommodate tails/highlights
        tmp_w = max(4, int(rect.w * 2))
        tmp_h = max(4, int(rect.h * 2))
        tmp = pygame.Surface((tmp_w, tmp_h), flags=pygame.SRCALPHA)
        center_x = tmp_w // 2
        center_y = tmp_h // 2
        ox = center_x - int(self.w/2)
        oy = center_y - int(self.h/2)

        if self.kind == "star":
            # simple twinkling point: draw a small circle and cross
            r = max(1, int(min(self.w, self.h)/2))
            intensity = 180 + int(75 * (0.5 + 0.5 * math.sin(self.age * 6 + self.x)))
            col = (int(min(255, intensity)),) * 3
            pygame.draw.circle(tmp, col + (self.alpha,), (center_x, center_y), r)
            # small sparkle lines
            pygame.draw.line(tmp, col + (self.alpha,), (center_x-r-1, center_y), (center_x+r+1, center_y), 1)
            pygame.draw.line(tmp, col + (self.alpha,), (center_x, center_y-r-1), (center_x, center_y+r+1), 1)

        elif self.kind == "planet":
            fill, ring, highlight = self.palette
            # draw planet on tmp
            pygame.draw.circle(tmp, ring + (self.alpha,), (center_x, center_y), int(self.w/2)+3)
            pygame.draw.circle(tmp, fill + (self.alpha,), (center_x, center_y), int(self.w/2))
            # simple band (darker)
            band_h = int(self.h * 0.18)
            band_rect = pygame.Rect(center_x - int(self.w*0.6), center_y - band_h//2, int(self.w*1.2), band_h)
            band_col = tuple(max(0, c-30) for c in fill)
            pygame.draw.ellipse(tmp, band_col + (self.alpha,), band_rect)
            # highlight
            pygame.draw.circle(tmp, highlight + (self.alpha,), (int(center_x - self.w*0.25), int(center_y - self.h*0.25)), max(2, int(self.w*0.08)))

        elif self.kind == "comet":
            head_col, tail_col, _ = self.palette
            # draw head on tmp
            pygame.draw.ellipse(tmp, head_col + (self.alpha,), pygame.Rect(ox, oy, int(self.w), int(self.h)))
            # tail: fading triangles drawn on tmp to the left
            tail_len = int(self.w * 3)
            tail_points = [ (ox, center_y), (ox - tail_len, center_y - int(self.h*0.6)), (ox - tail_len, center_y + int(self.h*0.6)) ]
            pygame.draw.polygon(tmp, tail_col + (max(10, int(self.alpha*0.6)),), tail_points)

        elif self.kind == "nebula":
            # nebula: draw several translucent ellipses on tmp
            for i in range(4):
                rx = center_x - int(self.w/2) + int(random.uniform(0, self.w))
                ry = center_y - int(self.h/2) + int(random.uniform(0, self.h))
                rw = max(2, int(self.w * (0.6 + 0.6 * ((i+1)/4))))
                rh = max(2, int(self.h * (0.6 + 0.6 * ((4-i)/4))))
                color = c1 if i % 2 == 0 else c2
                alpha_i = max(10, min(200, int(self.alpha * (0.4 + i*0.2))))
                pygame.draw.ellipse(tmp, (color[0], color[1], color[2], alpha_i), pygame.Rect(rx - rw//2, ry - rh//2, rw, rh))

        else:
            # fallback: rectangle scenic stripe on tmp
            pygame.draw.rect(tmp, cfg.COLOR_SCENERY + (self.alpha,), pygame.Rect(ox, oy, int(self.w), int(self.h)))

        # finally blit temporary surface to main surface at rect center
        blit_x = int(self.x - tmp_w // 2)
        blit_y = int(self.y - tmp_h // 2)
        surf.blit(tmp, (blit_x, blit_y))


class Obstacle(Entity):
    def __init__(self, x, y, size, vy, damage=1):
        super().__init__(x, y, size, size)
        self.vy = vy
        # collision damage to player on contact
        self.damage = damage
        # destructible: set HP based on size (bigger = tougher)
        self.max_hp = max(1, int(size // 24))
        self.hp = self.max_hp
        # pick asteroid palette (body, outline)
        try:
            self.asteroid_palette = random.choice(cfg.ASTEROID_PALETTES)
        except Exception:
            self.asteroid_palette = ((120,120,120),(80,80,80))
        # random seed for consistent-looking craters
        self.seed = random.random()

    def update(self, dt: float):
        self.y += self.vy * dt

    def draw(self, surf: pygame.Surface):
        # Draw an asteroid-like rock with some craters and an outline.
        rect = self.rect()
        body_col, outline_col = self.asteroid_palette
        # outline
        pygame.draw.ellipse(surf, outline_col, rect.inflate(4,4))
        # body
        pygame.draw.ellipse(surf, body_col, rect)

        # draw 2-4 craters as darker ellipses
        crater_count = 2 + int(self.seed * 3)
        for i in range(crater_count):
            cx = rect.x + int((0.15 + ((self.seed + i*0.23) % 0.7)) * rect.w)
            cy = rect.y + int((0.2 + ((self.seed * 1.3 + i*0.17) % 0.6)) * rect.h)
            cw = int(rect.w * (0.15 + ((self.seed + i*0.17) % 0.25)))
            ch = int(rect.h * (0.12 + ((self.seed + i*0.11) % 0.2)))
            crater_rect = pygame.Rect(cx, cy, cw, ch)
            pygame.draw.ellipse(surf, tuple(max(0,c-30) for c in body_col), crater_rect)
            pygame.draw.ellipse(surf, tuple(max(0,c-10) for c in outline_col), crater_rect.inflate(2,2), 1)

    def explode(self):
        """Return a list of Debris fragments spawned when this obstacle is destroyed."""
        pieces = []
        frag_count = 3 + int(self.max_hp)
        for i in range(frag_count):
            # small random sizes
            fw = max(4, int(self.w * random.uniform(0.12, 0.28)))
            fh = max(3, int(self.h * random.uniform(0.08, 0.22)))
            fx = self.x + random.uniform(-self.w*0.3, self.w*0.3)
            fy = self.y + random.uniform(-self.h*0.1, self.h*0.3)
            # velocity shards scatter outward and downward
            vx = random.uniform(-80, 80)
            vy = random.uniform(self.vy*0.3, self.vy*1.2)
            life = 0.8 + random.random()*1.2
            pieces.append(Debris(fx, fy, fw, fh, vx, vy, life, color=self.asteroid_palette[0]))
        return pieces


class Debris(Entity):
    def __init__(self, x, y, w, h, vx, vy, lifetime=1.0, color=(120,120,120)):
        super().__init__(x, y, w, h)
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.color = color

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

    def draw(self, surf: pygame.Surface):
        # small rotated rectangle/ellipse to represent fragment
        r = self.rect()
        pygame.draw.ellipse(surf, self.color, r)


class Enemy(Entity):
    def __init__(self, x, y, w, h, vy, pattern: str = "straight", can_fire: bool = False, hp: int = 1):
        super().__init__(x, y, w, h)
        self.vy = vy
        self.pattern = pattern
        self.can_fire = can_fire
        self.hp = hp
        self.age = 0.0
        self.fire_cd = random.uniform(0.5, 2.0)
        # pick a random color palette for this enemy (body, eye, pupil, mouth, outline)
        try:
            self.palette = random.choice(cfg.ENEMY_PALETTES)
        except Exception:
            # fallback to legacy colors
            self.palette = (cfg.COLOR_ENEMY_BODY, cfg.COLOR_ENEMY_EYE, cfg.COLOR_ENEMY_PUPIL, cfg.COLOR_ENEMY_MOUTH, cfg.COLOR_ENEMY_OUTLINE)

    def update(self, dt: float):
        self.age += dt
        # patterns: straight, sine, zigzag
        if self.pattern == "straight":
            self.y += self.vy * dt
        elif self.pattern == "sine":
            self.y += self.vy * dt
            self.x += math.sin(self.age * 3.0) * 60.0 * dt
        elif self.pattern == "zigzag":
            self.y += self.vy * dt
            self.x += (1 if int(self.age * 2) % 2 == 0 else -1) * 80.0 * dt

        if self.can_fire:
            self.fire_cd -= dt

    def try_fire(self):
        if not self.can_fire:
            return None
        if self.fire_cd <= 0.0:
            self.fire_cd = random.uniform(0.6, 2.5)
            return Bullet(self.x, self.y + self.h/2 + 6, cfg.ENEMY_BULLET_SPEED, owner="enemy")
        return None

    def draw(self, surf: pygame.Surface):
        # Draw a simple 'space monster' instead of a plain rectangle.
        # Body
        rect = self.rect()
        body_w = rect.w
        body_h = rect.h
        body_rect = pygame.Rect(rect.x, rect.y, body_w, body_h)
        # Outline
        outline_col = self.palette[4]
        body_col = self.palette[0]
        eye_col = self.palette[1]
        pupil_col = self.palette[2]
        mouth_col = self.palette[3]
        pygame.draw.ellipse(surf, outline_col, body_rect.inflate(4, 4))
        # Body fill
        pygame.draw.ellipse(surf, body_col, body_rect)

        # Eyes (1 or 2 depending on width)
        eye_count = 1 if body_w < 34 else 2
        for i in range(eye_count):
            ex = self.x - body_w*0.2 + (i * (body_w*0.4) if eye_count == 2 else 0)
            ey = self.y - body_h*0.18
            eye_r = max(3, int(min(body_w, body_h) * 0.12))
            pygame.draw.circle(surf, eye_col, (int(ex), int(ey)), eye_r)
            pygame.draw.circle(surf, pupil_col, (int(ex), int(ey)), max(1, eye_r//2))

        # Mouth
        mouth_w = int(body_w * 0.5)
        mouth_h = int(body_h * 0.18)
        mouth_rect = pygame.Rect(int(self.x - mouth_w/2), int(self.y + body_h*0.12), mouth_w, mouth_h)
        pygame.draw.ellipse(surf, mouth_col, mouth_rect)

        # Simple teeth lines
        tx = mouth_rect.x
        for i in range(4):
            sx = tx + int((i+1) * mouth_rect.w / 5)
            pygame.draw.line(surf, outline_col, (sx, mouth_rect.y), (sx, mouth_rect.y + mouth_rect.h//2), 1)

        # Tentacles: draw 3 curved lines below the body
        for i in range(3):
            start_x = int(self.x - body_w*0.35 + i*(body_w*0.35))
            start_y = int(self.y + body_h/2)
            # draw simple segmented tentacle
            points = []
            segs = 5
            for s in range(segs):
                px = start_x + int(math.sin(self.age*2 + i + s*0.6) * (6 + s*2))
                py = start_y + s * int(body_h*0.18)
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(surf, outline_col, False, points, 2)

    def hit(self, dmg: int = 1):
        self.hp -= dmg
        return self.hp <= 0
