import logging
from bot.misc.arguments import args

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(args.log)
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
