from os import environ
from re import compile
from dataclasses import dataclass
from functools import cached_property
from sys import argv, stderr
from typing import List, Optional

_REGEXP = compile(
    r"(?P<days>\d+d)?(?P<hours>\d+h)?(?P<minutes>\d+m)?(?P<seconds>\d+\.?\d*s)?"
)
FIELDS = 'days', 'hours', 'minutes'

_debug = lambda *a, **k: print(*a, file=stderr, **k)
_nop = lambda *a, **k: ...
debug = _debug if environ.get("DEBUG_LOG") else _nop

OPERATORS = {
    '+': lambda cumulation, value: cumulation + value,
    '-': lambda cumulation, value: cumulation - value
}


@dataclass
class Time:
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: float = 0.0

    @classmethod
    def from_seconds(cls, total_seconds: int):
        t_min, sec = total_seconds // 60, total_seconds % 60
        t_hour, min = t_min // 60, t_min % 60
        return cls(days=int(t_hour // 24),
                   hours=int(t_hour % 24),
                   minutes=int(min),
                   seconds=float(sec))

    @cached_property
    def total_seconds(self) -> float:
        return self.seconds + self.minutes * 60 + self.hours * 3_600 + self.days * 86_400

    def __add__(self, other):
        return Time.from_seconds(self.total_seconds + other.total_seconds)

    def __sub__(self, other):
        return Time.from_seconds(self.total_seconds - other.total_seconds)

    @classmethod
    def parse(cls, text) -> Optional['Time']:
        if match := _REGEXP.fullmatch(text):
            t = Time()
            for group in FIELDS:
                if value := match.group(group):
                    setattr(t, group, int(value[:-1]))
            if secs := match.group('seconds'):
                t.seconds = float(secs[:-1])
            return t
        else:
            return None

    def __str__(self) -> str:
        result = ""
        if self.days:
            result += str(self.days) + 'd'
        if self.hours:
            result += str(self.hours) + 'h'
        if self.minutes:
            result += str(self.minutes) + 'm'
        floored = self.seconds.__floor__()
        seconds = floored if floored == self.seconds else self.seconds
        return result + str(seconds) + 's'


def run(args: List[str]):
    cumulation = None
    value = None
    operator = None
    global debug
    for arg in args:
        if arg == "--debug":
            debug = _debug  # enable debug logging
            continue
        if time := Time.parse(arg):
            if cumulation is None:
                cumulation = value = time
            elif operator is None:
                value = time
            else:
                if value is None:
                    print("syntax error")
                    debug(f'{cumulation=}; {operator=}; {value=}')
                    exit(1)
                cumulation = operator(value, time)
                operator = None
                value = None
        elif _operator := OPERATORS.get(arg.strip()):
            operator = _operator
        else:
            debug(f'failed to parse operator or time "{arg}"')
    return cumulation


if __name__ == "__main__":
    print(run(argv))