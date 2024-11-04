from typing import Any, Dict, List, Optional

from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated


class SpotifyArtist(BaseModel):
    """Spotify artist."""

    name: str


class SpotifyTrack(BaseModel):
    """Spotify Track, composed by name and artists."""

    name: str
    artists: Optional[List[SpotifyArtist]]


def __get_track(v: Any) -> SpotifyTrack:
    """Flattens track structure."""
    return v.get("track", None)


CustomTrack = Annotated[
    Dict[str, SpotifyTrack],
    AfterValidator(__get_track),
]


class SpotifyPlaylist(BaseModel):
    """Spotify Playlist."""

    items: List[CustomTrack]


class SpotifyAlbum(BaseModel):
    """Spotify Album."""

    items: List[SpotifyTrack]
