from pydantic import BaseModel,EmailStr,Field

class RegisterRequest(BaseModel):
    username:str = Field(min_length=3,max_length=50)
    email:EmailStr
    password:str = Field(min_length=8)

class LoginRequest(BaseModel):
    account:str = Field(min_length=1)
    password:str = Field(min_length=8)
