"""
基础 Service
"""
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository

T = TypeVar("T")


class BaseService(Generic[T]):
    """
    基础 Service 类
    
    提供通用的业务逻辑层基础设施
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def commit(self):
        """提交事务"""
        await self.db.commit()
    
    async def rollback(self):
        """回滚事务"""
        await self.db.rollback()

