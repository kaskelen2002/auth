import api.models as _models
import fastapi as _fastapi
import jwt
from api.database import engine, SessionDep
from sqlalchemy import select

JWT_SECRET_KEY="JWT_SECRET_KEY"

async def decode_jwt_token_and_get_user(token: str, session: SessionDep):
    try:
        # Декодируем JWT-токен
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

        # Извлекаем email из полезной нагрузки
        email = payload.get("email")
        if not email:
            raise _fastapi.HTTPException(status_code=401, detail="Invalid token, email not found")

        # Выполняем запрос к базе данных без использования ORM
        async with engine.begin() as conn:
            query = select(_models.UserModel).where(_models.UserModel.email == email)
            result = await conn.execute(query)
            result = result.fetchone()

        if not result:
            raise _fastapi.HTTPException(status_code=404, detail="User not found")

        # Преобразуем результат в словарь для ответа
        user_data = {
            "id": result.id,
            "role": result.role,
            "email": result.email
        }
        return user_data
    except jwt.InvalidTokenError:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid token")
