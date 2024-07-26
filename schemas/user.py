from pydantic import BaseModel, Field


class UserPreRegisterSchema(BaseModel):
    mobile_phone: str = Field(...)
    captcha: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "mobile_phone": "+70001112233",
                "captcha": "token"
            }
        }


class UserResetPasswordSchema(BaseModel):
    mobile_phone: str = Field(...)
    otp: int = Field(...)
    new_password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "mobile_phone": "+70001112233",
                "otp": 123456,
                "new_password": "password"
            }
        }

class UserOtpCheckSchema(BaseModel):
    mobile_phone: str = Field(...)
    otp: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "mobile_phone": "+70001112233",
                "otp": 123456
            }
        }


class UserRegisterSchema(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    mobile_phone: str = Field(...)
    password: str = Field(...)
    otp: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "first_name": "first_name",
                "last_name": "last_name",
                "mobile_phone": "+70001112233",
                "password": "password",
                "otp": 123456
            }
        }


class UserLoginSchema(BaseModel):
    mobile_phone: str = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "mobile_phone": "+70001112233",
                "password": "password"
            }
        }
