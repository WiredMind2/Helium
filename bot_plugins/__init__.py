import os
import importlib
import logging
logger = logging.getLogger('helium_logger')

def import_plugins(reload=False):
	if __package__ is None:
		return
	cwd = os.path.dirname(__file__)
	plugins = []
	for f in os.listdir(cwd):
		path = os.path.join(cwd, f)
		if os.path.isfile(path) and len(f) >= 3 and f[-3:] == ".py" and f[:2] != "__":
			try:
				m = importlib.import_module(f'.{f[:-3]}', package=__package__)
			except ImportError as e:
				logger.warn('Error', e)
			else:
				if hasattr(m, 'module_class'):
					plugins.append(m.module_class)
	return plugins

plugins = import_plugins()
