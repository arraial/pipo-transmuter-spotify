import ssl
import logging

from opentelemetry import metrics, trace
from prometheus_client import REGISTRY
from faststream.security import BaseSecurity
from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
)
from faststream.rabbit.fastapi import RabbitRouter, Logger, Context
from faststream.rabbit.prometheus import RabbitPrometheusMiddleware
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware

from pipo_transmuter_spotify.telemetry import setup_telemetry
from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify.models import ProviderOperation
from pipo_transmuter_spotify.handler import SpotifyHandler

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


def __load_router(service_name: str) -> RabbitRouter:
    telemetry = setup_telemetry(service_name, settings.telemetry.local)
    core_router = RabbitRouter(
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
            RabbitPrometheusMiddleware(
                registry=REGISTRY,
                app_name=settings.telemetry.metrics.service,
                metrics_prefix="faststream",
            ),
            RabbitTelemetryMiddleware(tracer_provider=telemetry.traces or None),
        ),
    )
    return core_router


router = __load_router(settings.app)


def get_router():
    return router


def get_broker():
    return router.broker


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

spotify_publisher = router.broker.publisher(
    exchange=provider_exch,
    routing_key=settings.player.queue.service.transmuter.youtube_query.routing_key,
    description="Produces to provider exchange with key provider.spotify.url",
)

processed_url_success_counter = meter.create_counter(
    name="pipo.transmuter.spotify.url.success",
    description="Number of spotify url processed successfully",
    unit="requests",
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
    with tracer.start_as_current_span(
        "spotify_api_query",
        attributes={
            "pipo.request.uuid": request.uuid,
            "pipo.request.query": request.query,
        },
    ):
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
    processed_url_success_counter.add(1)
    logger.info("Transmuted spotify request: %s", query.uuid)
