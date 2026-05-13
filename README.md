# TG → Max

Мост для пересылки файлов из Telegram в Max (max.ru). Работает как userbot — используется твой личный аккаунт, никаких ботов.

```
Telegram (Saved Messages) → Telethon → GREEN-API → Max
```

## Как это работает

1. Кидаешь файл в Избранное (или любой личный чат) в Telegram
2. Telethon-userbot скачивает файл в изолированную папку `uploads/`
3. GREEN-API отправляет файл в Max на указанный номер
4. Локальный файл удаляется

## Возможности

- Любые типы файлов: фото, видео, документы, аудио
- Retry при скачивании из Telegram (до 3 попыток)
- Белый список отправителей
- Файлы не хранятся локально — удаляются после отправки
- Max не имеет доступа к файловой системе, только к `uploads/`

## Настройка

### 1. Telegram API

| Шаг | Действие |
|-----|----------|
| 1 | Зайди на https://my.telegram.org/apps |
| 2 | Создай приложение, получи `API_ID` и `API_HASH` |
| 3 | Узнай свой Telegram ID — напиши [@userinfobot](https://t.me/userinfobot) |

### 2. GREEN-API (шлюз для Max)

GREEN-API — сторонний сервис, который проксирует запросы в Max от имени пользователя (аналог userbot).

| Шаг | Действие |
|-----|----------|
| 1 | Зарегистрируйся на https://console.green-api.com |
| 2 | Создай инстанс → выбери **MAX Developer** (бесплатно) |
| 3 | Авторизуй: нажми «Получить QR-код» → сканируй из приложения Max: **Профиль → Устройства → Войти по QR-коду** |
| 4 | Скопируй `idInstance`, `apiTokenInstance` и `apiUrl` из настроек инстанса |

> **Тариф Developer**: безлимит на отправку, 3 чата. Для личного использования хватает.

### 3. Настройка .env

```bash
cp .env.example .env
# заполни своими данными
```

```ini
TG_API_ID=12345678
TG_API_HASH=your_hash
TG_ALLOWED_USERS=123456789        # твой Telegram ID

GA_INSTANCE_ID=1100000001
GA_API_TOKEN=your_token
GA_API_URL=https://3100.api.green-api.com   # из консоли GREEN-API
GA_MEDIA_URL=https://3100.api.green-api.com # то же самое

MAX_TARGET_PHONE=79999999999     # твой номер в Max
```

### 4. Установка и запуск

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

При первом запуске Telethon запросит номер телефона и код подтверждения из Telegram.

## Запуск как daemon (Linux)

```bash
# установка
sudo mkdir -p /opt/tg-to-max
sudo cp -r * /opt/tg-to-max/
cd /opt/tg-to-max
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# заполни .env
.venv/bin/python main.py   # первый запуск — авторизация Telethon
# после авторизации — CTRL+C

# systemd
sudo cp tg-to-max.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tg-to-max

# логи
journalctl -u tg-to-max -f
```

## Безопасность

- Max (через GREEN-API) имеет доступ **только** к `uploads/`
- Файлы удаляются сразу после отправки
- Принимаются файлы только от `TG_ALLOWED_USERS`
- Сессия Telethon хранится локально в `tg_session.session`
- Токены в `.env` — **не попадают в репозиторий** (через `.gitignore`)

## Структура

```
tg-to-max/
├── main.py                # точка входа
├── telegram_listener.py   # Telethon userbot
├── max_client.py          # GREEN-API клиент
├── config.py              # конфиг из .env
├── requirements.txt
├── .env.example
└── uploads/               # временное хранилище (Max видит только это)
```

## Лицензия

MIT
