import asyncio
from twisted.internet.defer import Deferred


def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))
