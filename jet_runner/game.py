import pygame
import sys
import random
from typing import List

import jet_runner.config as cfg
from jet_runner.entities import Player, Bullet, Enemy, Obstacle, Scenery
from jet_runner import spawner


class Game:
    def __init__(self, headless=False, enemy_bullets: bool = True, allow_nebulae: bool = False, max_scenery_alpha: int = 255):
        self.headless = headless
        self.enemy_bullets = enemy_bullets
        self.allow_nebulae = allow_nebulae
        self.max_scenery_alpha = max(0, min(255, int(max_scenery_alpha)))
        pygame.init()
        if headless:
            # use a hidden display mode
            pygame.display.init()
            pygame.display.set_mode((1,1), flags=pygame.HIDDEN)
        else:
            self.screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
            pygame.display.set_caption("Jet Runner")

        self.clock = pygame.time.Clock()
        self.player = Player(cfg.WIDTH/2, cfg.HEIGHT - 60)
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.obstacles: List[Obstacle] = []
        self.debris: List = []  # dynamic fragments from destroyed asteroids
        self.scenery: List[Scenery] = []

        self.spawn_t = 0.0
        self.spawn_enemy_t = 0.0
        self.spawn_obstacle_t = 0.0
        self.spawn_scenery_t = 0.0

        self.running = True

    def run(self, max_seconds: float = None):
        """Main loop. If max_seconds is set, run for at most that many seconds (useful for headless tests)."""
        elapsed = 0.0
        while self.running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            elapsed += dt
            self.handle_events()
            self.update(dt)
            if not self.headless:
                self.draw()
            if max_seconds is not None and elapsed >= max_seconds:
                print(f"Stopping after {elapsed:.2f}s (max_seconds={max_seconds}) - score={self.player.score} health={self.player.health}")
                self.running = False

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dir_x = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dir_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dir_x += 1.0
        self.player.move(dir_x, dt)

        if keys[pygame.K_SPACE] and self.player.can_fire():
            self.player.fire()
            self.bullets.append(Bullet(self.player.x, self.player.y - self.player.h/2 - 6, -cfg.BULLET_SPEED, owner="player"))

        # spawning
        self.spawn_enemy_t += dt
        self.spawn_obstacle_t += dt
        self.spawn_scenery_t += dt

        if self.spawn_enemy_t >= cfg.SPAWN_ENEMY_INTERVAL:
            self.spawn_enemy_t = 0.0
            self.enemies.append(spawner.spawn_enemy())

        if self.spawn_obstacle_t >= cfg.SPAWN_OBSTACLE_INTERVAL:
            self.spawn_obstacle_t = 0.0
            self.obstacles.append(spawner.spawn_obstacle())

        if self.spawn_scenery_t >= cfg.SPAWN_SCENERY_INTERVAL:
            self.spawn_scenery_t = 0.0
            self.scenery.append(spawner.spawn_scenery(allow_nebulae=self.allow_nebulae, max_alpha=self.max_scenery_alpha))

        # update entities
        self.player.update(dt)
        for e in self.bullets:
            e.update(dt)
        for en in self.enemies:
            en.update(dt)
            # Only allow enemy bullets if enabled globally
            if self.enemy_bullets:
                b = en.try_fire()
                if b:
                    self.bullets.append(b)
        for ob in self.obstacles:
            ob.update(dt)
        # update debris fragments
        for d in list(self.debris):
            d.update(dt)
        for s in self.scenery:
            s.update(dt)

        # collisions
        self.handle_collisions()

        # cleanup off-screen
        self.bullets = [b for b in self.bullets if -50 < b.y < cfg.HEIGHT + 50]
        self.enemies = [e for e in self.enemies if -200 < e.y < cfg.HEIGHT + 200]
        self.obstacles = [o for o in self.obstacles if -200 < o.y < cfg.HEIGHT + 200]
        self.scenery = [s for s in self.scenery if -200 < s.y < cfg.HEIGHT + 200]
        # keep debris while lifetime remains and on-screen
        self.debris = [d for d in self.debris if d.lifetime > 0 and -200 < d.y < cfg.HEIGHT + 200]

        # end condition
        if self.player.health <= 0:
            print(f"Game Over. Score: {self.player.score}")
            self.running = False

    def handle_collisions(self):
        # bullets vs enemies
        for b in list(self.bullets):
            if b.owner == "player":
                for e in list(self.enemies):
                    if b.rect().colliderect(e.rect()):
                        self.bullets.remove(b)
                        killed = e.hit(1)
                        if killed:
                            try:
                                self.enemies.remove(e)
                            except ValueError:
                                pass
                            self.player.score += 10
                        break
                else:
                    # bullets vs obstacles (player bullets can damage asteroids)
                    for ob in list(self.obstacles):
                        if b.rect().colliderect(ob.rect()):
                            try:
                                self.bullets.remove(b)
                            except ValueError:
                                pass
                            ob.hp -= 1
                            # small score for damaging
                            self.player.score += 2
                            if ob.hp <= 0:
                                # spawn debris
                                try:
                                    pieces = ob.explode()
                                except Exception:
                                    pieces = []
                                self.debris.extend(pieces)
                                try:
                                    self.obstacles.remove(ob)
                                except ValueError:
                                    pass
                                self.player.score += 5
                            break
            else:
                # enemy bullet vs player
                if b.rect().colliderect(self.player.rect()):
                    try:
                        self.bullets.remove(b)
                    except ValueError:
                        pass
                    self.player.health -= 1

        # player vs obstacles
        for ob in list(self.obstacles):
            if ob.rect().colliderect(self.player.rect()):
                # on collision, obstacle is destroyed and spawns debris
                try:
                    pieces = ob.explode()
                except Exception:
                    pieces = []
                self.debris.extend(pieces)
                try:
                    self.obstacles.remove(ob)
                except ValueError:
                    pass
                self.player.health -= ob.damage

        # player vs enemies
        for en in list(self.enemies):
            if en.rect().colliderect(self.player.rect()):
                try:
                    self.enemies.remove(en)
                except ValueError:
                    pass
                self.player.health -= 1

    def draw(self):
        self.screen.fill(cfg.COLOR_BG)
        for s in self.scenery:
            s.draw(self.screen)
        for ob in self.obstacles:
            ob.draw(self.screen)
        # draw debris fragments
        for d in self.debris:
            d.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        self.player.draw(self.screen)

        # HUD
        font = pygame.font.SysFont(None, 22)
        txt = font.render(f"Health: {self.player.health}  Score: {self.player.score}", True, (240,240,240))
        self.screen.blit(txt, (8,8))

        pygame.display.flip()
