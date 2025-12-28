import sys
import argparse
from jet_runner.game import Game


def main(argv=None):
    p = argparse.ArgumentParser(description="Jet Runner")
    p.add_argument("--headless", action="store_true", help="Run without opening a window")
    p.add_argument("--duration", type=float, default=None, help="If set, run for this many seconds and exit")
    p.add_argument("--no-enemy-bullets", dest="enemy_bullets", action="store_false",
                   help="Disable enemies firing bullets (they will still collide on contact)")
    p.add_argument("--enable-nebulae", dest="enable_nebulae", action="store_true",
                   help="Enable nebulae in background scenery")
    p.add_argument("--max-scenery-alpha", type=int, default=180,
                   help="Maximum alpha (0-255) used for scenery opacity; lower = more transparent")
    args = p.parse_args(argv)

    # clamp max alpha
    max_alpha = max(0, min(255, int(args.max_scenery_alpha)))
    g = Game(headless=args.headless, enemy_bullets=args.enemy_bullets, allow_nebulae=bool(args.enable_nebulae), max_scenery_alpha=max_alpha)
    g.run(max_seconds=args.duration)


if __name__ == "__main__":
    main()
