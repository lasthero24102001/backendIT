import pytest
from db.tokens.token import create_access_token,create_refresh_token
from jose import jwt
from config import settings
from db.security.securities import Utils



def test_hash_and_verify_password():
    password="12345"
    hash_password=Utils.get_password_hash(password)
    assert Utils.verify_password(password, hash_password) is True
    assert Utils.verify_password('2345', hash_password) is False
def test_access_token():
    user_id=1
    role='user'
    access_token=create_access_token(user_id,role)
    assert isinstance(access_token,str)

    payload=jwt.decode(access_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    assert payload['sub']==str(user_id)
    assert payload['role']==role
    assert payload['type']=='access'
def test_refresh_token():
    user_id=42
    role='user'
    refresh_token=create_refresh_token(user_id,role)
    assert isinstance(refresh_token,str)

    payload=jwt.decode(refresh_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    assert payload['sub']==str(user_id)
    assert payload['role']==role
    assert payload['type']=='refresh'


