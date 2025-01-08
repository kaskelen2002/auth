import email_validator as _email_check
import passlib.hash as _hash
import api.shemas as _shemas
import api.models as _models
import fastapi as _fastapi
import jwt
from api.database import SessionDep
from fastapi import Response

from sqlalchemy import select

JWT_SECRET_KEY="JWT_SECRET_KEY"

# Извлечь юзера по email из бд
async def get_user_by_email(email: str, session: SessionDep):
    query = select(_models.UserModel).filter(_models.UserModel.email == email)
    result = await session.execute(query)
    return result.scalars().first()

# Создать юзера
async def create_user(user: _shemas.UserCreate, session: SessionDep):
    try:
        valid = _email_check.validate_email(user.email)
        role = user.role
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=404, detail="Please enter a valid email")
    if role != "client" and role != "admin":
        raise _fastapi.HTTPException(status_code=404, detail="Please enter a valid role")

    user_obj = _models.UserModel(email=email, role=role, hashed_password=_hash.bcrypt.hash(user.password))
    session.add(user_obj)
    await session.commit()
    return user_obj


# Аутентификация юзера
async def authenticate_user(email: str, password: str, session: SessionDep):
    user = await get_user_by_email(email=email, session=session)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user

# Сгенерить токен
async def create_token(response: Response, user: _models.UserModel):
    user_obj = _shemas.User.from_orm(user)
    user_dict = user_obj.model_dump()
    token = jwt.encode(user_dict, JWT_SECRET_KEY, algorithm="HS256")
    response.set_cookie(key='token', value=token)
    return dict(access_token=token, token_type="bearer")


