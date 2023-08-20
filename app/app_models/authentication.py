from pydantic import BaseModel


class LoginInput(BaseModel):
    id: str
    password: str

    class Config:
        schema_extra = {"example": {"id": "0001", "password": "1234"}}
