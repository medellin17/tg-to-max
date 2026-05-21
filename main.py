import asyncio
import os
from pathlib import Path
from telethon.tl.types import Message
from config import Config
from telegram_listener import TelegramListener
from max_client import MaxSender


async def main():
    cfg = Config()

    tg = TelegramListener(
        api_id=cfg.TG_API_ID,
        api_hash=cfg.TG_API_HASH,
        allowed_users=cfg.TG_ALLOWED_USERS,
        upload_dir=cfg.UPLOAD_DIR,
    )

    max_client = MaxSender(
        instance_id=cfg.GA_INSTANCE_ID,
        api_token=cfg.GA_API_TOKEN,
        api_url=cfg.GA_API_URL,
        media_url=cfg.GA_MEDIA_URL,
    )

    state = max_client.check_state()
    print(f"Статус GREEN-API инстанса: {state}")

    if isinstance(state, dict) and state.get("stateInstance") != "authorized":
        print("ВНИМАНИЕ: Инстанс не авторизован! Авторизуй в кабинете GREEN-API через QR/SMS")
        print(f"Текущий статус: {state}")
        return

    chat_id = max_client.resolve_chat_id(cfg.MAX_TARGET_PHONE)
    print(f"chatId для {cfg.MAX_TARGET_PHONE}: {chat_id}")

    async def on_files(files: list[tuple[str, str, Message]]):
        sent, errors = [], []
        for file_path, caption, msg in files:
            try:
                print(f"Max: отправляю {file_path}...")
                result = max_client.send_file(file_path=file_path, caption=caption)
                print(f"Max: отправлено! {result}")
                sent.append(Path(file_path).name)
            except Exception as e:
                print(f"Max: ошибка: {e}")
                errors.append(Path(file_path).name)
            finally:
                try:
                    os.remove(file_path)
                    print(f"Удалил локальный файл: {file_path}")
                except OSError:
                    pass

        ref_msg = files[0][2]
        if len(files) == 1:
            name = sent[0] if sent else errors[0]
            if sent:
                await ref_msg.reply(f"✅ Отправлено в Max: `{name}`")
            else:
                await ref_msg.reply(f"❌ Ошибка отправки в Max: {errors[0]}")
        else:
            if sent:
                await ref_msg.reply(f"✅ Отправлено в Max: {len(sent)} файлов")
            if errors:
                await ref_msg.reply(f"❌ Ошибки: {', '.join(errors)}")

    async def on_text(text: str, msg: Message):
        try:
            print(f"Max: отправляю текст: {text[:50]}...")
            result = max_client.send_text(text)
            print(f"Max: текст отправлен! {result}")
            await msg.reply(f"✅ Текст отправлен в Max")
        except Exception as e:
            print(f"Max: ошибка отправки текста: {e}")
            await msg.reply(f"❌ Ошибка отправки текста в Max: {e}")

    tg.on_file(on_files)
    tg.on_text(on_text)

    print("Запуск... жду файлы в Telegram")
    await tg.start()


if __name__ == "__main__":
    asyncio.run(main())
