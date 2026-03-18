from db.databases.database import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from db.models.model import User, Project
from db.pydantic.pydantics import UpdateUser, UpdateProject, CreateProject
from db.security.securities import Utils, BaseService, BaseUserPolicy, BaseProjectPolicy
from sqlalchemy.orm import selectinload,joinedload
from fastapi_pagination.ext.sqlalchemy import paginate



class AuthService:
    def __init__(self,db:AsyncSession):
        self.db = db
    async def register_user(self,full_name:str,password:str,email:str):
        result=await self.db.execute(select(User).where(User.full_name==full_name))
        user=result.scalars().first()
        if user:
            raise HTTPException(status_code=409,detail="User already registered with this username")
        result1=await self.db.execute(select(User).where(User.email==email))
        email1=result1.scalars().first()
        if email1:
            raise HTTPException(status_code=409,detail="Email already registered with this username")
        hashed_password = Utils.get_password_hash(password)
        new_user=User(full_name=full_name,password=hashed_password,email=email)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    async def login_user(self,full_name:str,password:str):
        result=await self.db.execute(select(User).where(User.full_name==full_name))
        user=result.scalars().first()
        if not user or not Utils.verify_password(password,user.password):
            raise HTTPException(status_code=401,detail="Incorrect password")
        return user
class UserService(BaseService):
    def __init__(self,db:AsyncSession,policy:BaseUserPolicy):
        self.db = db
        self.policy = policy
    async def get_all(self):
        user_projects=select(User).options(selectinload(User.projects))
        return await paginate(self.db,user_projects)
    async def get_by_id(self,user_id:int):
        if not self.policy(user_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(User).where(User.id==user_id))
        user=result.scalars().first()
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        return user
    async def update(self,user_id:int,user_data:UpdateUser):
        if not self.policy(user_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(User).where(User.id==user_id))
        user=result.scalars().first()
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.password is not None:
            user.password=Utils.get_password_hash(user_data.password)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def delete(self,user_id:int):
        if not self.policy(user_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(User).where(User.id==user_id))
        delete=result.scalars().first()
        if not delete:
            raise HTTPException(status_code=404,detail="User not found")
        await self.db.delete(delete)
        await self.db.commit()
        return delete
class ProjectService(BaseService,CreateProject):
    def __init__(self,db:AsyncSession,policy:BaseProjectPolicy):
        self.db = db
        self.policy = policy
    async def get_all(self):
        result=select(Project).options(joinedload(Project.owner_id))
        return await paginate(self.db,result)
    async def get_by_id(self,project_id:int):
        if not self.policy(project_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(Project).where(Project.id==project_id))
        project=result.scalars().first()
        if not project:
            raise HTTPException(status_code=404,detail="Project not found")
        return project
    async def create(self,project_data:CreateProject):
        result=await self.db.execute(select(User).where(User.id==project_data.owner_id))
        check_user=result.scalars().first()
        if not check_user:
            raise HTTPException(status_code=404,detail="User not found")
        if not self.policy(check_user):
            raise HTTPException(status_code=403, detail="Forbidden")
        check_title=await self.db.execute(select(Project).where(Project.title==project_data.title))
        result1=check_title.scalars().first()
        if result1:
            raise HTTPException(status_code=409,detail="Project with this title already exists")
        new_project=Project(title=project_data.title,description=project_data.description,owner_id=project_data.owner_id or self.policy.user.id)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project
    async def update(self,project_id:int,project_data:UpdateProject):
        if not self.policy(project_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(Project).where(Project.id==project_id))
        project=result.scalars().first()
        if not project:
            raise HTTPException(status_code=404,detail="Project not found")
        if project_data.title is not None:
            project.title=project_data.title
        if project_data.description is not None:
            project.description=project_data.description
        await self.db.commit()
        await self.db.refresh(project)
        return project
    async def delete(self,project_id:int):
        if not self.policy(project_id):
            raise HTTPException(status_code=403,detail="Forbidden")
        result=await self.db.execute(select(Project).where(Project.id==project_id))
        project=result.scalars().first()
        if not project:
            raise HTTPException(status_code=404,detail="Project not found")
        await self.db.delete(project)
        await self.db.commit()
        return project



