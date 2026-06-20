"""Eventos de dominio base."""

from __future__ import annotations

from abc import ABC
from datetime import datetime, timezone
from uuid import uuid4


class EventoDominio(ABC):
    """Evento base del que heredan todos los eventos de dominio."""

    def __init__(self) -> None:
        self.evento_id: str = uuid4().hex
        self.timestamp: datetime = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "evento_id": self.evento_id,
            "tipo": type(self).__name__,
            "timestamp": self.timestamp.isoformat(),
        }
