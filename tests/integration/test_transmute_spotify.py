import pytest
import mock
import tests.constants
from tests.conftest import Helpers
from faststream.rabbit import TestRabbitBroker, RabbitQueue
from pipo_transmuter_spotify.handler import SpotifyOperations
from pipo_transmuter_spotify.models import ProviderOperation
from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify._queues import (
    router,
    broker,
    transmute_spotify,
    provider_exch,
)

test_queue = RabbitQueue(
    "test-queue",
    routing_key="provider.#",
    auto_delete=True,
)


@router.subscriber(
    queue=test_queue,
    exchange=provider_exch,
    description="Consumes from dispatch topic and produces to provider exchange",
)
async def consume_dummy(
    request: ProviderOperation,
) -> None:
    pass


@pytest.mark.spotify
@pytest.mark.remote_queue
class TestDispatch:
    @pytest.mark.parametrize(
        "query, expected",
        [
            (tests.constants.SPOTIFY_URL_1, tests.constants.SPOTIFY_URL_1_SONG),
            (
                tests.constants.SPOTIFY_ALBUM_1,
                tests.constants.SPOTIFY_ALBUM_1_SAMPLE_SONG,
            ),
            (
                tests.constants.SPOTIFY_PLAYLIST_1,
                tests.constants.SPOTIFY_PLAYLIST_1_SAMPLE_SONG,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_transmute_spotify(self, query, expected):
        server_id = "0"
        uuid = Helpers.generate_uuid()

        async with TestRabbitBroker(
            broker, with_real=settings.player.queue.remote
        ) as br:
            operation_request = ProviderOperation(
                uuid=uuid,
                server_id=server_id,
                provider="provider.spotify.url",
                operation=SpotifyOperations.URL,
                query=query,
            )

            provider_operations = [
                mock.call(
                    dict(
                        ProviderOperation(
                            uuid=uuid,
                            server_id=server_id,
                            query=expected,
                            provider="provider.youtube.query",
                            operation="query",
                        )
                    )
                )
            ]

            await br.publish(
                operation_request,
                exchange=provider_exch,
                routing_key=operation_request.provider,
            )
            await transmute_spotify.wait_call(timeout=tests.constants.SHORT_TIMEOUT)
            transmute_spotify.mock.assert_called_once_with(dict(operation_request))
            await consume_dummy.wait_call(timeout=tests.constants.MEDIUM_TIMEOUT)
            consume_dummy.mock.assert_has_calls(provider_operations, any_order=True)
