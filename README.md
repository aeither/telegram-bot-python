## Telegram Python Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/a0ln90?referralCode=CREDITS)

## Overview

This project is a simple Telegram bot built using the telebot library. It demonstrates the basic structure of a Telegram bot and uses uv for dependency management. The bot responds to commands and messages, and can be easily extended with additional functionality.

## Key Features

- Minimal Telegram bot application
- Responds to '/start' and '/hello' commands
- Echoes all other messages
- Uses telebot for bot functionality
- Uses uv for dependency management
- Easy to understand and extend

## Setup

```bash
pip install uv
uv sync
```

## Develop

To run the bot locally:

```bash
uv run python -B main.py
```

Make sure to set up your `.env` file with your Telegram bot token:

```bash
TELEGRAM_BOT_TOKEN=your_token_here
```

## Deploy

Initialize your project:

```bash
railway init
```

To deploy the bot on Railway:

```bash
railway up
```

Remember to set the `TELEGRAM_BOT_TOKEN` environment variable in your Railway project settings.TELEGRAM_BOT_TOKEN

## Test

Open Telegram, start a chat with your bot, and try the commands `/start` or `/hello`. The bot will also echo any other messages you send.

## Learn More

- [Telebot Documentation](https://pypi.org/project/pyTelegramBotAPI/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Railway Documentation](https://docs.railway.app/)
- [Telegram Python Bot Repository](https://github.com/aeither/telegram-bot-python/)
- [Railway Marketplace](https://railway.app/template/a0ln90)
