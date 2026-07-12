from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def trace_span(_name: str) -> Iterator[None]:
    yield
