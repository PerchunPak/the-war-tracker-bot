# the-war-tracker-bot

[![Support Ukraine](https://badgen.net/badge/support/UKRAINE/?color=0057B8&labelColor=FFD700)](https://www.gov.uk/government/news/ukraine-what-you-can-do-to-help)

[![Build Status](https://github.com/PerchunPak/the-war-tracker-bot/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/the-war-tracker-bot/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/PerchunPak/the-war-tracker-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/PerchunPak/the-war-tracker-bot)
[![Documentation Build Status](https://readthedocs.org/projects/the-war-tracker-bot/badge/?version=latest)](https://the-war-tracker-bot.readthedocs.io/)
[![Supported languages](https://img.shields.io/badge/languages-en%20%7C%20uk-brightgreen)](https://the-war-tracker-bot.readthedocs.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python support versions badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)

The bot that doom-scrolls through the war news for you!

- [Документація українською](https://the-war-tracker-bot.readthedocs.io/uk_UA/latest)

> **Note**:
> This bot is still in very alpha stage. I will update the README with better instructions on how to use it soon.

## Features

- Free! We don't want any money from you!
- Add yours!

## Installing

This is the same with installing for local developing.

```bash
git clone https://github.com/PerchunPak/the-war-tracker-bot.git
cd the-war-tracker-bot
```

### Installing `poetry`

Next we need install `poetry` with [recommended way](https://python-poetry.org/docs/master/#installation).

If you use Linux, use command:

```bash
curl -sSL https://install.python-poetry.org | python -
```

If you use Windows, open PowerShell with admin privileges and use:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Installing dependencies

```bash
poetry install --no-dev
```

#### Compiling translations

This required even if you want just use English.

```bash
pybabel compile -d locales
```

### Configuration

All configuration happens in `config.yml`, or with environment variables.

### If something is not clear

You can always write me!

## Updating

For updating, just re-download repository (do not forget save config),
if you used `git` for downloading, just run `git pull`.
After that, you need update translations, commands the same as in installing section:

```bash
pybabel compile -d locales
```

## Thanks

This project was generated with [python-template](https://github.com/PerchunPak/python-template).
