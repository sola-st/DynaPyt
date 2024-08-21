async def foo():
    for i in range(3):
        yield i
    return


async def main():
    async for i in foo():
        print(i)


import asyncio

asyncio.run(main())
