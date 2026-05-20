import re

from pydantic import BaseModel, Field, field_validator, model_validator

PASSWORD_PATTERN = re.compile(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z0-9]{8,}$')
LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


class Registration(BaseModel):
    user_name: str = Field(min_length=1, max_length=70)
    job_title: str = Field(min_length=1, max_length=50)
    login: str = Field(min_length=1, max_length=30)
    password: str
    confirm_password: str

    @field_validator('login')
    @classmethod
    def validate_login(cls, value: str) -> str:
        if not LOGIN_PATTERN.fullmatch(value):
            raise ValueError('Логин может содержать только латинские буквы, цифры, _ и -')
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.fullmatch(value):
            raise ValueError(
                'Пароль должен быть не короче 8 символов, содержать цифру и латинскую букву',
            )
        return value

    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Пароли не совпадают')
        return self


class LoginRequest(BaseModel):
    login: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    confirm_password: str
    new_password: str = Field(min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.fullmatch(value):
            raise ValueError(
                'Пароль должен быть не короче 8 символов, содержать цифру и латинскую букву',
            )
        return value

    @model_validator(mode='after')
    def new_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError('Новый пароль и подтверждение не совпадают')
        return self


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_in: int


class RegistrationSuccess(BaseModel):
    message: str = 'Регистрация прошла успешно!'
