import argparse

args_parser = argparse.ArgumentParser(description='Telegram shop')
args_parser.add_argument(
    '-c',
    '--config',
    type=str,
    default='telegramshop-bot.conf',
    dest='config',
    help='config file path'
)
args_parser.add_argument(
    '-l',
    '--log',
    type=str,
    default='telegramshop-bot.log',
    dest='log',
    help='log file path'
)

args = args_parser.parse_args()
