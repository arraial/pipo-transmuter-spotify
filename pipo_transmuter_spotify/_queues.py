import ssl
import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from prometheus_client import REGISTRY
from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
)
from faststream.rabbit.fastapi import RabbitRouter, Logger, Context
from faststream.rabbit.prometheus import RabbitPrometheusMiddleware
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware
from faststream.security import BaseSecurity

from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify.models import ProviderOperation
from pipo_transmuter_spotify.handler import SpotifyHandler

tracer_provider = TracerProvider(
    resource=Resource.create(attributes={"service.name": "faststream"})
)
trace.set_tracer_provider(tracer_provider)

router = RabbitRouter(
    app_id=settings.app,
    url=settings.queue_broker_url,
    host=settings.player.queue.broker.host,
    virtualhost=settings.player.queue.broker.vhost,
    port=settings.player.queue.broker.port,
    timeout=settings.player.queue.broker.timeout,
    max_consumers=settings.player.queue.broker.max_consumers,
    graceful_timeout=settings.player.queue.broker.graceful_timeout,
    logger=logging.getLogger(__name__),
    security=BaseSecurity(ssl_context=ssl.create_default_context()),
    middlewares=(
        RabbitPrometheusMiddleware(registry=REGISTRY),
        RabbitTelemetryMiddleware(tracer_provider=tracer_provider),
    ),
)

broker = router.broker


@router.get("/livez")
async def liveness() -> bool:
    return True


@router.get("/readyz")
async def readiness() -> bool:
    return await router.broker.ping(timeout=settings.probes.readiness.timeout)


provider_exch = RabbitExchange(
    settings.player.queue.service.transmuter.exchange,
    type=ExchangeType.TOPIC,
    durable=True,
)

spotify_queue = RabbitQueue(
    settings.player.queue.service.transmuter.spotify.queue,
    routing_key=settings.player.queue.service.transmuter.spotify.routing_key,
    durable=True,
    arguments=settings.player.queue.service.transmuter.spotify.args,
)

spotify_publisher = router.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.service.transmuter.youtube_query.routing_key,
    description="Produces to provider exchange with key provider.spotify.url",
)


@router.subscriber(
    queue=spotify_queue,
    exchange=provider_exch,
    description="Consumes from provider topic with provider.spotify.* key and produces to providers topic with provider.youtube.query",
)
async def transmute_spotify(
    request: ProviderOperation,
    logger: Logger,
    correlation_id: str = Context("message.correlation_id"),
) -> None:
    logger.debug("Received request: %s", request)
    tracks = await SpotifyHandler.tracks_from_query(request.query, request.shuffle)
    for track in tracks:
        query = ProviderOperation(
            uuid=request.uuid,
            server_id=request.server_id,
            provider=settings.player.queue.service.transmuter.youtube_query.routing_key,
            operation=track.operation,
            query=track.query,
        )
        await spotify_publisher.publish(
            query,
            correlation_id=correlation_id,
        )
    logger.info("Transmuted spotify request: %s", query.uuid)
