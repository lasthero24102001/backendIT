from pydantic import BaseModel, ConfigDict, constr,Field
from datetime import datetime
from typing import Optional,List


class CreateUser(BaseModel):
    full_name: str
    password: str=constr(min_length=8,max_length=15)
    email: str
    created_at: Optional[datetime]=None
    is_active: bool=False
class CreateProject(BaseModel):
    title: str
    description: Optional[str]=None
    owner_id:int
class CreateRefreshTokenDB(BaseModel):
    token: str
    expires_at: Optional[datetime]=None
    is_revoked: bool=False
    created_at: Optional[datetime]=None
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str='Bearer'
class RefreshToken(BaseModel):
    refresh_token: str
class RefreshTokenDBOut(BaseModel):
    id:int
    token:str
    expires_at:Optional[datetime]=None
    created_at:Optional[datetime]=None
    is_revoked: bool=False
    model_config = ConfigDict(from_attributes=True)
class ProjectOut(BaseModel):
    id:int
    title: str
    description: Optional[str]=None
    model_config = ConfigDict(from_attributes=True)
class UserOut(BaseModel):
     id:int
     full_name: str
     email:str
     created_at: Optional[datetime]=None
     is_active: bool=True
     projects:List[ProjectOut]=Field(default_factory=list)
     model_config = ConfigDict(from_attributes=True)
class UpdateUser(BaseModel):
    full_name: Optional[str]=None
    password: Optional[str]=None
    email: Optional[str]=None
    is_active: Optional[bool]=False
    created_at: Optional[datetime]=None
    model_config = ConfigDict(from_attributes=True)
class UpdateProject(BaseModel):
    title: Optional[str]=None
    description: Optional[str]=None
    model_config = ConfigDict(from_attributes=True)




