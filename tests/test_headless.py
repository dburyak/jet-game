import pytest
import pygame
from jet_runner.game import Game


def test_headless_runs_two_seconds():
    g = Game(headless=True)
    # Run for 2 seconds; should not crash and should stop
    g.run(max_seconds=2.0)
    # After run, health should be <= initial and score >= 0
    assert g.player.health <= 5
    assert g.player.score >= 0
