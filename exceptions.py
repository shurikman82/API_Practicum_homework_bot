class TelegramError(Exception):
    """Ошибка телеграм."""

    pass


class EmptyResponse(Exception):
    """Пустой ответ от сервера."""

    pass


class ProgrammError(Exception):
    """Сбой в работе программы."""

    pass


class InvalidResponse(Exception):
    """Неверный ответ сервера."""

    pass


class JsonError(Exception):
    """Не в json."""

    pass
