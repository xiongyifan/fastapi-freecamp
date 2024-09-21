from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime



class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(UserBase):
    pass



class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    create_at: datetime
    # user_id: int
    user: UserResponse

    class Config:
        from_attributes = True


class PostWithVotesResponse(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        from_attributes = True


class Vote(BaseModel):
    post_id: int
    direction: conint(le=1) # type: ignore


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None