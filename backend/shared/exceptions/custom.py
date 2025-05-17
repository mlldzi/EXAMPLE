class AppException(Exception):
    """Базовый класс для исключений приложения."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(AppException):
    """Исключение для случаев, когда ресурс не найден."""
    def __init__(self, resource_name: str, resource_id: str):
        message = f"{resource_name} с ID '{resource_id}' не найден."
        super().__init__(message, status_code=404)

class BadRequestException(AppException):
    """Исключение для неверных запросов."""
    def __init__(self, message: str = "Неверный запрос."):
        super().__init__(message, status_code=400)

# Другие кастомные исключения можно добавить здесь 