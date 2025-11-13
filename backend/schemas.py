from pydantic import BaseModel

class Account(BaseModel):
    id: int
    account_type: str
    balance: float
    owner_id: int

    class Config:
        from_attributes = True # Pydantic v2 uses this instead of orm_mode

class User(BaseModel):
    id: int
    username: str
    accounts: list[Account] = []

    class Config:
        from_attributes = True