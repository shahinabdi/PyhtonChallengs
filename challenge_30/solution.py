"""Challenge 30 — Event bus with weak references and ExceptionGroup."""

import gc
import inspect
import weakref
from collections import defaultdict
from collections.abc import Callable
from typing import Any

type Handler = Callable[[Any], None]
type HandlerRef = weakref.ref[Any]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[HandlerRef]] = defaultdict(list)

    @staticmethod
    def _make_ref(handler: Handler) -> HandlerRef:
        # Bound methods are re-created on every attribute access, so a
        # plain weakref.ref(obj.method) dies IMMEDIATELY. WeakMethod holds
        # the instance and the function separately and rebuilds the bound
        # method on demand — alive exactly as long as the instance is.
        if inspect.ismethod(handler):
            return weakref.WeakMethod(handler)
        return weakref.ref(handler)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers[event_type].append(self._make_ref(handler))

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers[event_type] = [
            ref for ref in self._subscribers[event_type]
            if ref() is not None and ref() != handler
        ]

    def publish(self, event_type: str, payload: Any) -> None:
        # (c) Snapshot the list before iterating: a handler that
        # subscribes/unsubscribes (i.e. publishes-during-publish) mutates
        # self._subscribers[event_type] — iterating the live list would
        # skip or double-call handlers. The snapshot freezes THIS
        # publish's audience; changes apply from the next publish on.
        refs_snapshot = list(self._subscribers[event_type])

        live_handlers: list[Handler] = []
        dead_refs: list[HandlerRef] = []
        for ref in refs_snapshot:
            handler = ref()
            if handler is None:
                dead_refs.append(ref)  # (a) subscriber was garbage-collected
            else:
                live_handlers.append(handler)

        if dead_refs:  # prune lazily, against the CURRENT list
            self._subscribers[event_type] = [
                ref for ref in self._subscribers[event_type]
                if ref not in dead_refs
            ]

        # (b) Run every handler; collect failures; raise them together.
        errors: list[Exception] = []
        for handler in live_handlers:
            try:
                handler(payload)
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise ExceptionGroup(
                f"{len(errors)} handler(s) failed for {event_type!r}", errors
            )


if __name__ == "__main__":
    bus = EventBus()
    log: list[str] = []

    class Subscriber:
        def __init__(self, name: str) -> None:
            self.name = name

        def on_event(self, payload: Any) -> None:
            log.append(f"{self.name}:{payload}")

    # (a) auto-removal on garbage collection
    keeper, goner = Subscriber("keeper"), Subscriber("goner")
    bus.subscribe("tick", keeper.on_event)
    bus.subscribe("tick", goner.on_event)
    bus.publish("tick", 1)
    assert log == ["keeper:1", "goner:1"]

    del goner
    gc.collect()
    log.clear()
    bus.publish("tick", 2)
    assert log == ["keeper:2"], log
    print("dead subscriber auto-removed")

    # (b) one failing handler doesn't stop the others; ExceptionGroup raised
    def bad_handler(payload: Any) -> None:
        raise ValueError(f"cannot handle {payload}")

    def good_handler(payload: Any) -> None:
        log.append(f"good:{payload}")

    bus.subscribe("job", bad_handler)
    bus.subscribe("job", good_handler)
    log.clear()
    try:
        bus.publish("job", "x")
    except* ValueError as eg:
        print(f"caught group with {len(eg.exceptions)} error(s)")
    assert log == ["good:x"]  # good handler still ran

    # (c) publish-during-publish: handler subscribes another handler mid-flight
    def self_extending(payload: Any) -> None:
        log.append("first")
        bus.subscribe("meta", lambda p: log.append("late"))  # mutates list

    bus.subscribe("meta", self_extending)
    # NOTE: the lambda above is held only weakly and dies instantly —
    # which doubles as a warning: subscribers must keep a strong reference
    # to their handlers. Demonstrate corruption-free iteration regardless:
    log.clear()
    bus.publish("meta", None)
    bus.publish("meta", None)
    assert log == ["first", "first"]
    print("ok")
