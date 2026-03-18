from abc import ABC, abstractmethod
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from db.models.model import User,Project
from typing import Any


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

class Utils:
    @staticmethod
    def get_password_hash(password:str)->str:
        return pwd_context.hash(password)
    @staticmethod
    def verify_password(plain_password:str, hashed_password:str)->bool:
        return pwd_context.verify(plain_password, hashed_password)
class BaseUserPolicy(ABC):
    def __init__(self,user:User):
        self.user = user
    @abstractmethod
    def can_read(self,user:User):
        pass
    @abstractmethod
    def can_update(self,user:User):
        pass
    @abstractmethod
    def can_delete(self,user:User):
        pass
class UserPolicy(BaseUserPolicy):
    def can_read(self,user:User):
        return self.user.role=='admin' or self.user.id==user.id
    def can_update(self,user:User):
        return self.user.role=='admin' or self.user.id==user.id
    def can_delete(self,user:User):
        return self.user.role=='admin' or self.user.id==user.id
class BaseProjectPolicy(ABC):
    def __init__(self,user:User):
        self.user = user
    @abstractmethod
    def can_read(self,project:Project):
        pass
    @abstractmethod
    def can_create(self,project:Project):
        pass
    @abstractmethod
    def can_update(self,project:Project):
        pass
    @abstractmethod
    def can_delete(self,project:Project):
        pass
class ProjectPolicy(BaseProjectPolicy):
    def can_read(self,project:Project):
        return self.user.role=='admin' or self.user.id==project.owner_id
    def can_create(self,project:Project):
        return self.user.is_active
    def can_update(self,project:Project):
        return self.user.role=='admin' or self.user.id==project.owner_id
    def can_delete(self,project:Project):
        return self.user.role=='admin' or self.user.id==project.owner_id
class BaseService(ABC):
    @abstractmethod
    async def get_all(self):
        pass
    @abstractmethod
    async def get_by_id(self,obj_id:int):
        pass
    @abstractmethod
    async def update(self,obj_id:int,obj_in:Any):
        pass
    @abstractmethod
    async def delete(self,obj_id:int):
        pass
class CreateService(ABC):
    @abstractmethod
    async def create(self,obj_in:Any):
        pass


