from __future__ import annotations
import asyncio
from collections import defaultdict


class SSEManager:
    """Manages Server-Sent Events subscriptions per booth."""

    def __init__(self) -> None:
        self._subs: dict[int, list[asyncio.Queue[str]]] = defaultdict(list)

    def subscribe(self, booth_id: int) -> asyncio.Queue[str]:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=16)
        self._subs[booth_id].append(q)
        return q

    def unsubscribe(self, booth_id: int, q: asyncio.Queue[str]) -> None:
        try:
            self._subs[booth_id].remove(q)
        except ValueError:
            pass

    def notify(self, booth_id: int, event: str = "settings_updated") -> None:
        for q in list(self._subs.get(booth_id, [])):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


_manager = SSEManager()


def get_sse_manager() -> SSEManager:
    return _manager
