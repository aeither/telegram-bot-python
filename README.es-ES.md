

## Bot de Telegram en Python

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/a0ln90?referralCode=CREDITS&utm_medium=integration&utm_source=template&utm_campaign=generic)

## Descripción general

Este proyecto es un bot de Telegram simple construido utilizando la biblioteca telebot. Demuestra la estructura básica de un bot de Telegram y utiliza uv para la gestión de dependencias. El bot responde a comandos y mensajes, y puede extenderse fácilmente con funcionalidad adicional.

## Características principales

- Aplicación mínima de bot de Telegram
- Responde a los comandos '/start' y '/hello'
- Repite todos los demás mensajes
- Utiliza telebot para la funcionalidad del bot
- Utiliza uv para la gestión de dependencias
- Fácil de entender y extender

## Configuración

```bash
pip install uv
uv sync
```

## Desarrollo

Para ejecutar el bot localmente:

```bash
uv run python -B main.py
```

Asegúrate de configurar tu archivo `.env` con tu token de bot de Telegram:

```bash
TELEGRAM_BOT_TOKEN=your_token_here
```

## Despliegue

Inicializa tu proyecto:

```bash
railway init
```

Para desplegar el bot en Railway:

```bash
railway up
```

Recuerda configurar la variable de entorno `TELEGRAM_BOT_TOKEN` en la configuración de tu proyecto en Railway.

## Pruebas

Abre Telegram, inicia un chat con tu bot y prueba los comandos `/start` o `/hello`. El bot también repetirá cualquier otro mensaje que envíes.

## Más información

- [Documentación de Telebot](https://pypi.org/project/pyTelegramBotAPI/)
- [Documentación de uv](https://docs.astral.sh/uv/)
- [API de Bots de Telegram](https://core.telegram.org/bots/api)
- [Documentación de Railway](https://docs.railway.app/)
- [Repositorio del Bot de Telegram en Python](https://github.com/aeither/telegram-bot-python/)
- [Mercado de Railway](https://railway.app/template/a0ln90)
