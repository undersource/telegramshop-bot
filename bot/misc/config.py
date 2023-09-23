from configparser import ConfigParser
from bot.misc.arguments import args

config = ConfigParser()
config.read(args.config)
