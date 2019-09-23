import logging
import settings
logging.basicConfig(format=settings.loggerformat)

class _logger:
    def __init__(self, logger):
        self.logger = logger

    def _chain(self, *msg):
        return ' '.join(str(b) for b in msg)

    def _setLevel(self, lvl):
        self.logger.setLevel(lvl)

    def debug(self, *msg, **kwargs):
        self.logger.debug(self._chain(*msg))

    def info(self, *msg, **kwargs):
        self.logger.info(self._chain(*msg))

    def warning(self, *msg, **kwargs):
        self.logger.warning(self._chain(*msg))

    def error(self, *msg, **kwargs):
        self.logger.error(self._chain(*msg))

    def critical(self, *msg, **kwargs):
        self.logger.critical(self._chain(*msg))


def getLogger(fname):
    fname = fname[:-3] if fname.endswith('.py') else fname
    baselogger = logging.getLogger(fname)

    fname = fname.split('.')[-1]
    dbglvl = settings._debuglevel.get(fname)
    logger = _logger(baselogger)
    if not dbglvl:
        dbglvl = 0
        print(f'logger for {fname} not found, defaulting to 0')
    else:
        print(f'logger for {fname} initialized with debug level {dbglvl}')
    logger._setLevel(dbglvl)

    return logger
