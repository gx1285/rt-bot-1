# RT - Data Manager

from typing import TypeVar

from inspect import iscoroutinefunction, getsource
from warnings import filterwarnings
from functools import wraps

from aiomysql import Pool, Cursor


filterwarnings('ignore', module=r"aiomysql")
__all__ = ("DatabaseManager", "cursor")
cursor: Cursor
cursor = None # type: ignore


CaT = TypeVar("CaT")
class DatabaseManager:

    pool: Pool

    def __init_subclass__(cls):
        for key, value in list(cls.__dict__.items()):
            if iscoroutinefunction(value) and not getattr(value, "__dm_ignore__", False):
                # `cursor`の引数を増設する。
                l = {}
                source = getsource(value).replace("self",  "self, cursor", 1)
                source = "\n".join((
                    "\n".join(
                        f"{'    '*i}if True:"
                        for i in range(int(len(source[:source.find("d")]) / 4)-1)
                    ), source
                ))
                exec(source, value.__globals__, l)
                # 新しい関数を作る。
                @wraps(l[key])
                async def _new(
                    self: DatabaseManager, *args, __dm_func__=l[key], **kwargs
                ):
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cursor:
                            return await __dm_func__(self, cursor, *args, **kwargs)
                setattr(cls, key, _new)

    @staticmethod
    def ignore(func: CaT) -> CaT:
        setattr(func, "__dm_ignore__", True)
        return func