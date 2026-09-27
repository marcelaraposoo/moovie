"""Cria a conta do Administrador (login do sistema).

Uso:
    cd backend
    .venv/bin/python -m scripts.seed_admin

Pede nome, e-mail e senha interativamente. A senha nunca é salva em texto
puro — só o hash (PBKDF2-HMAC-SHA256, ver app/core/security.py) vai para o
banco.
"""

from __future__ import annotations

import asyncio
import getpass

from app.auth import repository
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal


async def main() -> None:
    print("=== Criar conta do Administrador ===")
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()

    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")
    if senha != confirmacao:
        print("As senhas não coincidem. Nada foi criado.")
        return
    if len(senha) < 4:
        print("Use uma senha com pelo menos 4 caracteres. Nada foi criado.")
        return

    async with AsyncSessionLocal() as db:
        existente = await repository.get_by_email(db, email)
        if existente is not None:
            print(f"Já existe um administrador com o e-mail {email}. Nada foi criado.")
            return

        await repository.create(db, nome=nome, email=email, senha_hash=hash_password(senha))

    print(f"Administrador '{nome}' <{email}> criado com sucesso. Já pode fazer login no frontend.")


if __name__ == "__main__":
    asyncio.run(main())
