from pydantic import BaseModel, field_validator
from typing import Optional

class Schedule(BaseModel):
    interval_minutes: Optional[int] = None
    @field_validator('interval_minutes')
    @classmethod
    def interval_valid(cls, v):
        if v is not None and v < 1:
            raise ValueError("El intervalo debe ser al menos 1 minuto")
        return v
