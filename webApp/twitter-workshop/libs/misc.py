# Misc. functions


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta