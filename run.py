import asyncio
import square_wars

try:
    asyncio.run(square_wars.run())
except ValueError:
    # I don't know how else to handle "a coroutine was expected, got None" (yet)
    raise SystemExit from None
