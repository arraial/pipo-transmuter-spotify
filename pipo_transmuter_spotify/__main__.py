#!usr/bin/env python3
import logging
import os
import sys

import uvicorn
from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify.app import create_app


def main():
    logging.basicConfig(
        level=settings.telemetry.log.level,
        format=settings.telemetry.log.format,
        encoding=settings.telemetry.log.encoding,
    )

    logger = logging.getLogger(__name__)

    app = create_app()

    try:
        uvicorn.run(
            app,
            host=settings.probes.host,
            port=settings.probes.port,
            log_level=settings.probes.log_level
        )
    except Exception:
        logger.exception("Unexpected exception raised")
    finally:
        logger.info("Exiting program")
        sys.stderr.flush()
        os._exit(1)


if __name__ == "__main__":
    main()
