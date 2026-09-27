from __future__ import annotations

from pydantic import BaseModel, Field

# Nota: usamos `str` (e não `EmailStr`) de propósito — `EmailStr` exigiria
# adicionar o pacote `email-validator` como nova dependência do projeto.


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    senha: str = Field(..., min_length=1)


class AdminOut(BaseModel):
    id: str
    nome: str
    email: str

    model_config = {"from_attributes": True}
