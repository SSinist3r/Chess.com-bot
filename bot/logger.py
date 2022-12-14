import logging.handlers

class Logger:
    def __init__(self, logging_service="chessbot"):
        self.Logger = logging.getLogger(f"{logging_service}_logger")
        self.Logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')
        fh = logging.FileHandler(f"logs/{logging_service}_logger.txt")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.Logger.addHandler(fh)

        # logging to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.Logger.addHandler(ch)
        
    def info(self, msg):
      self.Logger.info(msg)
    def error(self, msg):
      self.Logger.error(msg)
    def debug(self, msg):
      self.Logger.debug(msg)
    def warning(self, msg):
      self.Logger.warning(msg)