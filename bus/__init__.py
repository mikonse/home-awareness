import asyncio
from collections import defaultdict, OrderedDict
from typing import Optional, Callable, List

from asyncio import iscoroutine, ensure_future

from bus.events import Event, EventError
from log import LOG


class EventException(Exception):
    """An exception internal to the event bus."""
    pass


class EventBus:
    def __init__(self, scheduler=ensure_future, loop=None):
        self._events = defaultdict(OrderedDict)
        self._all_handlers = list()
        self._schedule = scheduler
        self._loop = loop

    def _add_event_handler(self, event_type: str, k: Callable[[Event], None], v: Callable[[Event], None]) -> None:
        # Fire 'new_listener' *before* adding the new listener!
        # self.emit('new_listener', event, k)

        # Add the necessary function
        # Note that k and v are the same for `on` handlers, but
        # different for `once` handlers, where v is a wrapped version
        # of k which removes itself before calling k
        self._events[event_type][k] = v

    def on(self, event_type: str, callback: Optional[Callable[[Event], None]] = None) -> Callable:
        def _on(f):
            self._add_event_handler(event_type, f, f)
            return f

        if self is None:
            return _on
        else:
            return _on(callback)

    def emit(self, event_type: str, event: Event):
        LOG.debug(f'Bus - {event_type}: {event}')
        handled = False

        to_handle = list(self._events[event_type].values())
        for f in to_handle:
            result = f(event)

            # If f was a coroutine function, we need to schedule it and
            # handle potential errors
            if iscoroutine and iscoroutine(result):
                if self._loop:
                    d = self._schedule(result, loop=self._loop)
                else:
                    d = self._schedule(result)

                # scheduler gave us an asyncio Future
                if hasattr(d, 'add_done_callback'):
                    @d.add_done_callback
                    def _callback(f):
                        exc = f.exception()
                        if exc:
                            self.emit('error', EventError(exc))

                # scheduler gave us a twisted Deferred
                elif hasattr(d, 'addErrback'):
                    @d.addErrback
                    def _callback(exc: Exception):
                        self.emit('error', EventError(exc))
            handled = True

        if not handled and type(event) == EventError:
            raise EventException("Uncaught, unspecified 'error' event.")

        return handled

    def once(self, event_type: str, f: Optional[Callable[[Event], None]] = None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """

        def _wrapper(f):
            def g(e: Event) -> None:
                self.remove_listener(event_type, f)
                # f may return a coroutine, so we need to return that
                # result here so that emit can schedule it
                return f(e)

            self._add_event_handler(event_type, f, g)
            return f

        if f is None:
            return _wrapper
        else:
            return _wrapper(f)

    def remove_listener(self, event_type: str, f: Callable[[Event], None]) -> None:
        """Removes the function ``f`` from ``event``."""
        self._events[event_type].pop(f)

    def remove_all_listeners(self, event_type: Optional[str] = None) -> None:
        """Remove all listeners attached to ``event``.
        If ``event`` is ``None``, remove all listeners on all events.
        """
        if event_type is not None:
            self._events[event_type] = OrderedDict()
        else:
            self._events = defaultdict(OrderedDict)

    def listeners(self, event_type: str) -> List[Callable[[Event], None]]:
        """Returns a list of all listeners registered to the ``event``.
        """
        return list(self._events[event_type].keys())


e_bus = EventBus()


async def main(shutdown_signal: asyncio.Event):
    await shutdown_signal.wait()


if __name__ == '__main__':
    main()
