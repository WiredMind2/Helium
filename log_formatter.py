import logging
import logging.handlers
import os
import sys

class CustomFormatter(logging.Formatter):
	"""Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

	grey = '\x1b[38;21m'
	blue = '\x1b[38;5;39m'
	yellow = '\x1b[38;5;226m'
	red = '\x1b[38;5;196m'
	bold_red = '\x1b[31;1m'
	reset = '\x1b[0m'

	def __init__(self, fmt, *args, **kwargs):
		super().__init__()

		self.fmts = {}

		lvls = {
			logging.DEBUG: self.grey,
			logging.INFO: self.blue,
			logging.WARNING: self.yellow,
			logging.ERROR: self.red,
			logging.CRITICAL: self.bold_red,
		}

		use_cols = sys.platform.startswith('linux')

		for lvl, col in lvls.items():
			if use_cols and fmt is not None:
				fmt = fmt.replace('%(asctime)s', self.grey + '%(asctime)s' + self.reset)
				fmt = fmt.replace('%(levelname)s', col + '%(levelname)s' + self.reset)
			self.fmts[lvl] = logging.Formatter(fmt, *args, **kwargs)

		# self.FORMATS = {
		# 	logging.DEBUG: self.grey + self.fmt + self.reset,
		# 	logging.INFO: self.blue + self.fmt + self.reset,
		# 	logging.WARNING: self.yellow + self.fmt + self.reset,
		# 	logging.ERROR: self.red + self.fmt + self.reset,
		# 	logging.CRITICAL: self.bold_red + self.fmt + self.reset
		# }

	def format(self, record):
		# log_fmt = self.FORMATS.get(record.levelno)
		# formatter = logging.Formatter(log_fmt)
		formatter = self.fmts.get(record.levelno)

		return formatter.format(record)

def setup_logs():
	# Logging setup
	if not os.path.exists('logs'):
		os.mkdir('logs')

	# log_file = f'logs/helium_{datetime.now().isoformat()}.log'
	log_file = 'logs/helium.log'

	logger = logging.getLogger('helium_logger')
	logger.setLevel(logging.DEBUG)
	format_args = {
		'fmt': '%(asctime)s-%(levelname)s: %(message)s',
		'datefmt': '%H:%M:%S'
	}

	ch = logging.StreamHandler(sys.stdout)
	ch.setFormatter(CustomFormatter(**format_args))
	logger.addHandler(ch)

	fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=(1048576*5), backupCount=7, encoding='utf-8')
	fh.setFormatter(logging.Formatter(**format_args))
	logger.addHandler(fh)
