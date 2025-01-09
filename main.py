import api.service as _services
import api.shemas as _shemas
import api.models as _models
import api.auth_jwt as _auth
import fastapi as _fastapi
from fastapi import FastAPI, HTTPException, Response, Request
from api.database import engine, SessionDep
from sqlalchemy import select

app = FastAPI()


@app.post("/setup_database", tags=["Database"], summary="Пересоздать базу данных")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(_models.Base.metadata.drop_all)
        await conn.run_sync(_models.Base.metadata.create_all)
    return {"status": "ok"}

@app.get("/get_user", tags=["Admin Panel"])
async def get_user(session: SessionDep):
    query = select(_models.UserModel)
    result = await session.execute(query)
    return result.scalars().all()


# Создание пользователя
@app.post("/sign_up", tags=["User Auth"])
async def reg_user(user: _shemas.UserCreate, session: SessionDep):
    n_user = await _services.get_user_by_email(email = user.email, session = session)
    if n_user:
        raise HTTPException(status_code=401, detail="This user is already registered")
    else:
        n_user = await _services.create_user(user = user, session = session)
        #user_id = n_user.id
    return _fastapi.HTTPException(
        status_code=201,
        detail="User Registered!"
    )


# Создание токена
@app.post("/sign_in", tags=['User Auth'])
async def generate_token(response: Response, user_data: _shemas.GenerateUserToken, session: SessionDep):
    user = await _services.authenticate_user(email=user_data.email, password=user_data.password, session = session)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await _services.create_token(response=response, user=user)

# Выход из аккаунта
@app.get("/logout", tags = ['User Auth'])
async def logout(response: Response):
    response.delete_cookie(key="token")
    return {"massage": "Logout complete."}

@app.get("/decode_token_and_get_user", tags=['User Auth'])
async def decode_token_and_get_user(request: Request, session: SessionDep):
    token = request.cookies.get("token")
    user = await _auth.decode_jwt_token_and_get_user(token=token, session=session)
    return user

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5003,  reload=True)
