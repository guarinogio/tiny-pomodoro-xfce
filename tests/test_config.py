from tiny_pomodoro.config import DEFAULTS

def test_defaults_keys():
    assert "work_minutes" in DEFAULTS
    assert "timer_minutes" in DEFAULTS
    assert "theme" in DEFAULTS
