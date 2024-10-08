from itertools import count
from typing import Iterable, Callable, Generator


def get_condition(limit: int| None) -> Callable:
  return (lambda x: x < limit , lambda _: True)[limit is None]

def get_range(limit: int | None) -> Generator[int, None, None]:
  num = 0
  con = get_condition(limit)
  while con(num):
    yield num 
    num += 1


NAMES = ['Alice', 'Bob', 'Mallory', 'Carol', 'Chuck', 'Peggy', 'Victor', 'Trent']
BOOTSTRAP_SERVERS = 'localhost:9092,localhost:9093,localhost:9094'