import pytest

from pipo_transmuter_spotify.handler import SpotifyHandler
import tests.constants


@pytest.mark.unit
@pytest.mark.spotify
class TestSpotifySource:
    @pytest.fixture(scope="function", autouse=True)
    def music_handler(self, mocker):
        return SpotifyHandler()

    @pytest.mark.asyncio
    async def test_empty_url(self, music_handler):
        assert not (await music_handler.tracks_from_query(tests.constants.EMPTY_MUSIC))

    @pytest.mark.parametrize(
        "url",
        [
            tests.constants.SPOTIFY_URL_NO_HTTPS,
            tests.constants.SPOTIFY_URL_1,
            tests.constants.SPOTIFY_URL_2,
            tests.constants.SPOTIFY_URL_3,
            tests.constants.SPOTIFY_PLAYLIST_1,
            tests.constants.SPOTIFY_ALBUM_1,
        ],
    )
    @pytest.mark.asyncio
    async def test_intput(self, music_handler, url):
        assert await music_handler.tracks_from_query(url)
