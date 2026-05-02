def test_timer_seconds_math():
    hours = 1
    minutes = 2
    seconds = 3

    assert hours * 3600 + minutes * 60 + seconds == 3723
