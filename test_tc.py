from tc import Time, _REGEXP, run
from pytest import raises

def test_regexp():
    assert _REGEXP.fullmatch("15m")

def test_match():
    assert Time.parse("15m") == Time(minutes=15)
    assert Time.parse("30s") == Time(seconds=30.0)
    assert Time.parse("1d1h1m1.1s") == Time(days=1, hours=1, minutes=1, seconds=1.1)
    assert Time.parse("01d01h01m01.10s") == Time(days=1, hours=1, minutes=1, seconds=1.1)

def test_failed_match():
    assert Time.parse("1m1d") is None
    assert Time.parse("aoanmsdfoimsdf1m1.0s") is None

def test_Time__from_seconds():
    assert Time.from_seconds(125.5) == Time(minutes=2, seconds=5.5)
    assert Time.from_seconds(86_525.5) == Time(days=1, minutes=2, seconds=5.5)

def test_Time_add():
    assert (Time(minutes=1) + Time(seconds=1)) == Time(minutes=1, seconds=1)

def test_Time_sub():
    assert (Time(minutes=1) - Time(seconds=1)) == Time(seconds=59)

def test_run():
    result = run(["1m30s", "+", "1m"])
    assert result == Time(minutes=2, seconds=30)
    result = run("1m30s - 1m".split())
    assert result == Time(seconds=30)

def test_run_chain():
    result =  run("1m30s - 1m + 30s".split())
    assert result == Time(minutes=1)