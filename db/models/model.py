from sqlalchemy import Column, Integer, String, Boolean,Index,ForeignKey, DateTime
from sqlalchemy.orm import relationship,declarative_base
from datetime import datetime,timezone

Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True,nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    refresh_tokens = relationship("RefreshTokenDB", back_populates="user")
    projects = relationship("Project", back_populates="owner")
    __table_args__ = (Index('idx_full_name_email', full_name,email),)



class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String,nullable=False)
    description = Column(String,nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    __table_args__ = (Index('idx_description_title', description,title),)


class RefreshTokenDB(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    user = relationship("User", back_populates="refresh_tokens")