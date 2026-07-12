import logging

import structlog


def configure_logging(log_level: str) -> None:
    logging.basicConfig(level=log_level.upper(), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )
