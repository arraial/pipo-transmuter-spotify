#!usr/bin/env python3
from fastapi import FastAPI
from prometheus_client import REGISTRY, make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from faststream.asgi import make_ping_asgi, get, AsgiResponse
from prometheus_client import make_asgi_app, REGISTRY
from pipo_transmuter_spotify._queues import get_router
from pipo_transmuter_spotify.config import settings


@get
async def liveness_ping(scope):
    return AsgiResponse(b"", status_code=settings.probes.liveness.status_code)


def create_app(router=None) -> FastAPI:
    router = router or get_router()
    application = FastAPI()
    application.include_router(router)
    application.mount(settings.probes.liveness.endpoint, liveness_ping)
    application.mount(
        settings.probes.readiness.endpoint,
        make_ping_asgi(router.broker, timeout=settings.probes.readiness.timeout),
    )
    application.mount(settings.telemetry.metrics.endpoint, make_asgi_app(REGISTRY))
    FastAPIInstrumentor.instrument_app(application)
    return application
