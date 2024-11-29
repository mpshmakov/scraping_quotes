import asyncio
from time import sleep


async def t():
    sleep(5)
    print("finished")

async def main():    
    asyncio.create_task(t()) 
    print("t")
    sleep(5)
    print("done")

asyncio.run(main())
# main()