# telegramshop-bot

Telegram shop bot on aiogram on webhook architecture.

## Dependencies

* python
* pip
* redis
* nginx
* openrc/systemd

## Installing

Working directory is in `/var/www/telegramshop-bot`

## Setup

### Bot

```
python -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### OpenRC

`cp contrib/openrc/telegramshop-bot /etc/init.d/telegramshop-bot`

### Systemd

`cp contrib/systemd/telegramshop-bot.service /etc/systemd/system/telegramshop-bot.service`

### Nginx

```
cp contrib/nginx/sites-available/telegramshop-bot.conf /etc/nginx/sites-available/telegramshop-bot.conf
ln -s /etc/nginx/sites-available/telegramshop-bot.conf /etc/nginx/sites-enabled/telegramshop-bot.conf
```

## Start

### OpenRC

```
rc-update add redis default
rc-update add telegramshop-bot default
rc-update add nginx default

rc-service redis start
rc-service telegramshop-bot start
rc-service nginx start
```

### Systemd

`systemctl enable --now redis telegramshop-bot nginx`
