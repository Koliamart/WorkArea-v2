import re


# Валидатор для паролей
class Validators:
    @staticmethod
    def validate_password(password):
        pattern = r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z0-9]{8,}$'
        return re.fullmatch(pattern, password) is not None









