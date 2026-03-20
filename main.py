import traceback
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import add_pagination
from config import settings
from db.databases.database import AsyncSession,get_db
from db.models.model import User
from db.pydantic.pydantics import TokenResponse, CreateUser, UserSimpleOut, RefreshToken
from db.service.services import AuthService
from jose import jwt,JWTError
from db.tokens.token import create_access_token, create_refresh_token, save_refresh_token, validate_refresh_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем подключение к Redis на порту 6380
    # Параметр decode_responses=True критически важен для лимитера!
    redis_instance = redis.from_url(
        "redis://localhost:6380",
        encoding="utf-8",
        decode_responses=True
    )

    # Инициализируем лимитер ОДИН РАЗ при старте
    await FastAPILimiter.init(redis_instance)

    print("--- REDIS RATE LIMITER ГОТОВ (Порт 6380) ---")

    yield

    # Закрываем соединение при выключении сервера
    await redis_instance.close()


app = FastAPI(lifespan=lifespan)
add_pagination(app)

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("------- КРИТИЧЕСКАЯ ОШИБКА -------")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": str(exc), "traceback": traceback.format_exc()},
    )
@app.post("/register", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def register_users(user:CreateUser,db:AsyncSession=Depends(get_db)):
    auth=AuthService(db)
    result=await auth.register_user(full_name=user.full_name,password=user.password,email=user.email)
    return result
@app.post("/login/users",response_model=TokenResponse)
async def login_users(form_data:OAuth2PasswordRequestForm=Depends(),db:AsyncSession=Depends(get_db)):
    auth=AuthService(db)
    new_user=await auth.login_user(form_data.username,form_data.password)
    new_access_token=create_access_token(user_id=new_user.id,role=new_user.role)
    new_refresh_token=create_refresh_token(user_id=new_user.id,role=new_user.role)
    return {"access_token":new_access_token,"refresh_token":new_refresh_token,'token_type':'Bearer'}
@app.post('/refresh/users',response_model=TokenResponse)
async def refresh(data:RefreshToken,db:AsyncSession=Depends(get_db)):
    try:
        payload=jwt.decode(data.refresh_token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        user_id=int(payload.get('sub'))
        if not user_id:
            raise HTTPException(status_code=401,detail='Invalid token')
        if payload['type'] !='refresh':
            raise HTTPException(status_code=401,detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401,detail='Invalid token')
    result=await db.execute(select(User).where(User.id==user_id))
    user=result.scalars().first()
    if not user:
        raise HTTPException(status_code=404,detail='User not found')
    await validate_refresh_token(refresh_token=data.refresh_token,user_id=user.id)
    new_access_token1=create_access_token(user_id=user.id,role=user.role)
    new_refresh_token1=create_refresh_token(user_id=user.id,role=user.role)
    await save_refresh_token(refresh_token=data.refresh_token,user_id=user.id)
    await db.commit()
    return TokenResponse(access_token=new_access_token1,refresh_token=new_refresh_token1,token_type='Bearer')
@app.post('/logout')
async def logout(data:RefreshToken,db:AsyncSession=Depends(get_db)):
    try:
        payload=jwt.decode(data.refresh_token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        user_id=int(payload.get('sub'))
        if not user_id:
            raise HTTPException(status_code=401,detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401,detail='Invalid token')
    result=await db.execute(select(User).where(User.id==user_id))
    user_logout=result.scalars().first()
    if not user_logout:
        raise HTTPException(status_code=404,detail='User not found')
    await validate_refresh_token(refresh_token=data.refresh_token,user_id=user_logout.id)
    await db.commit()
    return {'message':'Successfully logged out'}
