from bus import Event


def make_callback(f, *args, **kwargs):
    async def wrapper(event: Event):
        await f(*args, **kwargs)

    return wrapper
