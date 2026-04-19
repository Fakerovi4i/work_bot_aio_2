import logging





class ColoredFormatter(logging.Formatter):
    """Добавляет цвета в консоль (без внешних библиотек)"""

    COLORS = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[31;1m",  # bright red
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"



def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # ====================== КОНСОЛЬ ======================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    console_formatter = ColoredFormatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ====================== ФАЙЛ ======================
    file_handler = logging.FileHandler("errors.log", mode="a", encoding="utf-8", delay=True)
    file_handler.setLevel(logging.ERROR)

    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s\n"
        "└─ %(pathname)s:%(lineno)d\n",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Отключаем шум от библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Защита от дублирования логов
    logger.propagate = False




