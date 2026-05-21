import asyncio
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.types import Message


class TelegramListener:
    def __init__(self, api_id: int, api_hash: str, allowed_users: list[int], upload_dir: str):
        self.client = TelegramClient("tg_session", api_id, api_hash)
        self.allowed_users = set(allowed_users)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._on_file_callback = None
        self._pending_groups: dict[int, list[Message]] = {}

    def on_file(self, callback):
        self._on_file_callback = callback

    async def start(self):
        self.client.add_event_handler(self._handle_message, events.NewMessage)
        await self.client.start()
        me = await self.client.get_me()
        print(f"Telegram: авторизован как {me.first_name} (id={me.id})")
        await self.client.run_until_disconnected()

    async def _download_with_retry(self, msg: Message, retries: int = 3) -> str | None:
        for attempt in range(1, retries + 1):
            try:
                path = await msg.download_media(file=str(self.upload_dir))
                if path:
                    return path
            except Exception as e:
                print(f"Telegram: попытка {attempt}/{retries} скачать не удалась: {e}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
        return None

    async def _handle_message(self, event: events.NewMessage.Event):
        msg: Message = event.message
        if not msg.out and msg.sender_id not in self.allowed_users:
            return

        if not msg.file:
            return

        if msg.grouped_id:
            if msg.grouped_id not in self._pending_groups:
                self._pending_groups[msg.grouped_id] = []
                asyncio.create_task(self._process_group(msg.grouped_id))
            self._pending_groups[msg.grouped_id].append(msg)
            return

        file_path = await self._download_with_retry(msg)
        if not file_path:
            print("Telegram: не смог скачать файл после 3 попыток")
            await event.reply("❌ Не удалось скачать файл после 3 попыток")
            return

        print(f"Telegram: скачал файл: {file_path}")
        caption = msg.message or ""

        if self._on_file_callback:
            await self._on_file_callback([(file_path, caption, msg)])

    async def _process_group(self, grouped_id: int):
        await asyncio.sleep(0.7)

        messages = self._pending_groups.pop(grouped_id, [])
        if not messages:
            return

        results = []
        for msg in messages:
            file_path = await self._download_with_retry(msg)
            if file_path:
                print(f"Telegram: скачал файл: {file_path}")
                caption = msg.message or ""
                results.append((file_path, caption, msg))

        if results and self._on_file_callback:
            await self._on_file_callback(results)

    async def reply(self, event, text: str):
        await event.reply(text)
