import asyncio
import functools


class BaseAdapter:
    def __init__(self, executor=None):
        self._executor = executor

    async def run_in_executor(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        if kwargs:
            func = functools.partial(func, *args, **kwargs)
            args = []
        return await loop.run_in_executor(self._executor, func, *args)
