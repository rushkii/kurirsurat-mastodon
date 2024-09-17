from pyrogram import Client, idle


class Bot(Client):
    def __init__(
        self,
        name: str,
        api_id: int | str,
        api_hash: str,
        bot_token: str = None,
        plugins: str = None,
        *args,
        **kwargs
    ):
        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            plugins=plugins,
            *args,
            **kwargs
        )

    async def run(self):
        await self.start()
        print("Bot sedang berjalan...")
        await idle()
        await self.stop()
