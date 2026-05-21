from typing import List
from pydantic import BaseModel, Field, IPvAnyAddress, field_validator


class SNMPSchema(BaseModel):
    ip: IPvAnyAddress | str
    port: int = Field(default=161, ge=1, le=65535)
    community: str = Field(default="public", min_length=1)
    oids: List[str]

    @field_validator("oids")
    @classmethod
    def validate_oids(cls, value: List[str]) -> List[str]:
        """
        Valida que los OIDs tengan formato numérico:
        1.3.6.1.2.1...
        """
        for oid in value:
            parts = oid.split(".")

            if not all(part.isdigit() for part in parts):
                raise ValueError(f"OID inválido: {oid}")

        return value