from pydantic import BaseModel


class EmployerBase(BaseModel):
    id: int = 0
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    hard_skill: str = ""
    soft_skill: str = ""
