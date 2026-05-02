from tiny_pomodoro.config import DEFAULTS

def test_required_defaults_exist():
    required = [
        "timer_title",
        "work_minutes",
        "short_break_minutes",
        "long_break_minutes",
        "timer_hours",
        "timer_minutes",
        "timer_seconds",
        "theme",
        "animations",
        "autostart",
    ]

    for key in required:
        assert key in DEFAULTS

def test_default_values_are_valid():
    assert DEFAULTS["work_minutes"] > 0
    assert DEFAULTS["short_break_minutes"] > 0
    assert DEFAULTS["long_break_minutes"] > 0
    assert DEFAULTS["theme"] in {"system", "light", "dark"}
