import asyncio
from square_wars import main

try:
    asyncio.run(main.run())
except ValueError:
    # I don't know how else to handle "a coroutine was expected, got None" (yet)
    raise SystemExit from None
