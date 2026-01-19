from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import verify_token
from app.models.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=True)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)

        if payload is None:
            raise credentials_exception

        user_id_str: str | None = payload.get("sub", None)
        email: str | None = payload.get("email", None)
        role: str | None = payload.get("role", None)

        if user_id_str is None:
            raise credentials_exception

        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email, role=role)
        return token_data

    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception


def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    # Здесь можно добавить проверку на активность пользователя
    return current_user
