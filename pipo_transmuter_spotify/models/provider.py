from enum import StrEnum

from pydantic import BaseModel, Field


class Provider(StrEnum):
    """Provider types."""

    YOUTUBE = "youtube"
    SPOTIFY = "spotify"


class ProviderOperation(BaseModel):
    uuid: str = Field(
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    provider: str = Field(pattern=r"^[\d\w]*.[\d\w]*.[\d\w]*$")
    server_id: str
    operation: str
    shuffle: bool = False
    query: str
