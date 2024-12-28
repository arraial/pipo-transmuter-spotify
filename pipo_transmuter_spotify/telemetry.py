from dataclasses import dataclass
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    InMemoryMetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter


@dataclass
class TelemetryProviders:
    """Tracks used telemetry providers."""

    traces: TracerProvider
    metrics: MeterProvider


def setup_telemetry(service_name: str, local: bool = False) -> TelemetryProviders:
    resource = Resource.create(attributes={"service.name": service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_exporter = InMemorySpanExporter() if local else OTLPSpanExporter()
    processor = BatchSpanProcessor(tracer_exporter)
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    metric_reader = (
        InMemoryMetricReader()
        if local
        else PeriodicExportingMetricReader(OTLPMetricExporter())
    )
    metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(metric_provider)
    return TelemetryProviders(tracer_provider, metric_provider)
