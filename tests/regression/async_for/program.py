import asyncio


async def get_next_async():
    for i in range(3):
        yield i
        await asyncio.sleep(0.5)


async def main():
    async for i in get_next_async():
        print(i)


asyncio.run(main())
