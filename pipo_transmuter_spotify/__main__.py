#!usr/bin/env python3
import logging
import os
import sys

import uvicorn
from pipo_transmuter_spotify.config import settings
from pipo_transmuter_spotify.app import get_app



def main():
    logging.basicConfig(
        level=settings.log.level,
        format=settings.log.format,
        encoding=settings.log.encoding,
    )

    logger = logging.getLogger(__name__)

    app = get_app()

    try:
        uvicorn.run(
            app,
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
