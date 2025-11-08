# app/models/user.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    player_id: Optional[str]  # For push notifications
    phone: Optional[str]      # For SMS
    registered_at: datetime
