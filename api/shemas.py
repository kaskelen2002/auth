from pydantic import BaseModel

class UserBase(BaseModel):
    role: str
    email: str
    class Config:
       from_attributes=True


class UserCreate(UserBase):
    password: str
    class Config:
       from_attributes=True


class User(UserBase):
    id: int
    class Config:
       from_attributes=True


class GenerateUserToken(BaseModel):
    email: str
    password: str
    class Config:
       from_attributes=True