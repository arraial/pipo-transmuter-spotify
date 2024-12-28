import random
import asyncio
import logging
from enum import StrEnum
from dataclasses import dataclass
from typing import Iterable, List

import spotipy

from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify.models import (
    SpotifyAlbum,
    SpotifyPlaylist,
    SpotifyTrack,
)


class SourceType(StrEnum):
    """SourceHandler types."""

    NULL = "null"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"


@dataclass
class SourcePair:
    query: str
    handler_type: str
    operation: str = "query"


class SpotifyOperations(StrEnum):
    """Spotify operation types."""

    URL = "url"


class SpotifyHandler:
    """Handles spotify url music."""

    name = SourceType.SPOTIFY

    @staticmethod
    def __format_query(track: SpotifyTrack) -> SourcePair:
        song = track.name
        artist = track.artists[0].name if track.artists else ""
        entry = f"{song} - {artist}" if artist else song
        return SourcePair(
            query=entry,
            handler_type=SourceType.YOUTUBE,
        )

    @staticmethod
    def _get_playlist(
        client: spotipy.Spotify, query: str, fields: Iterable[str], limit: int
    ) -> List[SpotifyTrack]:
        tracks = client.playlist_items(
            query,
            fields=fields,
            limit=limit,
            additional_types="track",
        )
        return SpotifyPlaylist(**tracks).items

    @staticmethod
    def _get_album(
        client: spotipy.Spotify, query: str, limit: int
    ) -> List[SpotifyTrack]:
        tracks = client.album_tracks(
            query,
            limit=limit,
        )
        return SpotifyAlbum(**tracks).items

    @staticmethod
    def _get_track(client: spotipy.Spotify, query: str) -> List[SpotifyTrack]:
        track = client.track(
            query,
        )
        return [SpotifyTrack(**track)]

    @staticmethod
    async def tracks_from_query(
        query: str, shuffle: bool = False
    ) -> Iterable[SourcePair]:
        """
        TODO

        asyncio.to_thread is used to avoid blocking asyncio event loop, considering Spotipy
        library is not CPU nor asyncio friendly.
        """
        tracks = []
        if not query:
            return tracks
        try:
            spotify = spotipy.Spotify(
                client_credentials_manager=spotipy.SpotifyClientCredentials(
                    client_id=settings.spotify_client,
                    client_secret=settings.spotify_secret,
                )
            )
            if "playlist" in query:
                logging.getLogger(__name__).info(
                    "Processing spotify playlist '%s'", query
                )
                task = asyncio.to_thread(
                    SpotifyHandler._get_playlist,
                    spotify,
                    query,
                    [settings.player.source.spotify.playlist.filter],
                    settings.player.source.spotify.playlist.limit,
                )
            elif "album" in query:
                logging.getLogger(__name__).info("Processing spotify album '%s'", query)
                task = asyncio.to_thread(
                    SpotifyHandler._get_album,
                    spotify,
                    query,
                    settings.player.source.spotify.album.limit,
                )
            else:
                logging.getLogger(__name__).info("Processing spotify track '%s'", query)
                task = asyncio.to_thread(SpotifyHandler._get_track, spotify, query)
            tracks = (await asyncio.gather(task))[0]
        except spotipy.oauth2.SpotifyOauthError:
            logging.getLogger(__name__).exception(
                "Unable to access spotify API. \
                Confirm API credentials are correct."
            )
        except spotipy.exceptions.SpotifyException:
            logging.getLogger(__name__).exception(
                "Unable to process spotify query '%s'", query
            )
        shuffle and random.shuffle(tracks)
        return [SpotifyHandler.__format_query(track) for track in tracks]
