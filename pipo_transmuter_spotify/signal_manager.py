#!usr/bin/env python3
import asyncio
import logging
import signal
from typing import Iterable


class SignalManager:
    """Manage program signals."""

    @staticmethod
    async def __shutdown(
        signal, main_task: str, loop: asyncio.AbstractEventLoop
    ) -> None:
        """Cancel all running async tasks.

        Cancel running asyncio tasks, except this one, so they can perform necessary
        cleanup by processing an asyncio.CancelledError exception.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            Loop from where tasks should be cancelled.
        """
        logger = logging.getLogger(__name__)

        logger.debug("Received exit signal %s", signal.name)
        logger.debug(
            "Current task '%s' will not be deleted", asyncio.current_task().get_name()
        )

        tasks = [
            task
            for task in asyncio.all_tasks()
            if ((task is not asyncio.current_task()) and (task.get_name() != main_task))
        ]

        for task in tasks:
            logger.debug("Cancelling task '%s'", task.get_name())
            task.cancel()
            logger.debug("Cancelled task '%s'", task.get_name())

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All tasks cancelled")
        logger.debug("Stopping asyncio loop")
        loop.stop()
        logger.info("Stopped asyncio loop")

    @staticmethod
    def add_handlers(
        loop: asyncio.AbstractEventLoop,
        main_task: str,
        signals: Iterable[signal.Signals],
    ) -> None:
        """Add signal handlers to manage program execution."""
        for sig in signals:
            loop.add_signal_handler(
                sig,
                lambda sig=sig: asyncio.create_task(
                    SignalManager.__shutdown(sig, main_task, loop),
                    name="signal_shutdown",
                ),
            )
