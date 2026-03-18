from datetime import datetime,timedelta
from config import settings
from jose import jwt,JWTError
from db.databases.database import AsyncSession,get_db
from db.security.securities import Utils,oauth2_scheme
from db.models.model import RefreshTokenDB, User
from sqlalchemy import select,update
from fastapi import HTTPException,Depends


def create_access_token(user_id:int,role:str):
    payload={'sub':str(user_id),'role':role,'type':'access','exp':datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
def create_refresh_token(user_id:int,role:str):
    payload={'sub':str(user_id),'role':role,'type':'refresh','exp':datetime.utcnow()+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)}
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
async def save_refresh_token(db:AsyncSession,refresh_token:str,user_id:int):
    hashed_token=Utils.get_password_hash(refresh_token)
    new_refresh_token = RefreshTokenDB(token=hashed_token,user_id=user_id,expires_at=datetime.utcnow()+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),created_at=datetime.utcnow(),is_revoked=True)
    db.add(new_refresh_token)
    await db.commit()
    await db.refresh(new_refresh_token)
    return new_refresh_token
async def validate_refresh_token(db:AsyncSession,refresh_token:str,user_id:int):
    query=await db.execute(select(RefreshTokenDB).where(RefreshTokenDB.user_id==user_id,RefreshTokenDB.is_revoked==False))
    result=query.scalars().all()
    correct_token=None
    for value in result:
        if Utils.verify_password(refresh_token,value.token):
            correct_token=value
            break
    if not correct_token:
        raise HTTPException(status_code=404,detail="Token not found")
    delete_all_tokens=await db.execute(update(RefreshTokenDB).where(RefreshTokenDB.user_id==user_id).values(is_revoked=True))
    await db.commit()
    return delete_all_tokens
def decode_token(token:str):
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        if 'sub' not in payload:
            raise HTTPException(status_code=404,detail="Token not found")
        return payload
    except JWTError:
        raise HTTPException(status_code=404,detail="Token not found")
async def get_current_user(db:AsyncSession=Depends(get_db),token:str=Depends(oauth2_scheme)):
    try:
        payload=decode_token(token)
        user_id=int(payload.get('sub'))
        if not user_id:
            raise HTTPException(status_code=404,detail="Token not found")
        if payload['type']!='access':
            raise HTTPException(status_code=404,detail="Token not found")
    except JWTError:
        raise HTTPException(status_code=404, detail="Token not found")
    result=await db.execute(select(User).where(User.id==user_id))
    user=result.scalars().first()
    if not user:
        raise HTTPException(status_code=404,detail="Token not found")
    return user

