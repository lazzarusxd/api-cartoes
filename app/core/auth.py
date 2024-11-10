from datetime import datetime, timedelta

from pytz import timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.configs import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1}")


def _criar_token(tipo_token: str, tempo_vida: timedelta, sub: str) -> str:
    sp = timezone("America/Sao_Paulo")
    expira = datetime.now(tz=sp) + tempo_vida
    payload = {
        "type": tipo_token,
        "exp": expira,
        "iat": datetime.now(tz=sp),
        "sub": str(sub)
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def criar_token_acesso(cpf: str) -> str:
    return _criar_token(
        tipo_token="access_token",
        tempo_vida=timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES),
        sub=cpf
    )
