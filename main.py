from bot import Bot

import os, asyncio
from dotenv import load_dotenv


def prepare():
    load_dotenv()
    if not os.path.exists("storage"):
        os.makedirs("storage")


async def main():
    bot = Bot(
        "storage/kurirsurat",
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH"),
        bot_token=os.getenv("BOT_TOKEN"),
        plugins=dict(root="bot.plugins"),
    )
    await bot.run()


if __name__ == "__main__":
    prepare()
    asyncio.run(main())
