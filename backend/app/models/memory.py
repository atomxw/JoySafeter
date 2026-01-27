"""
Memory 模型

根据需求新增表:
MEMORY_TABLE_SCHEMA = {
    "memory_id": {"type": String, "primary_key": True, "nullable": False},
    "memory": {"type": JSON, "nullable": False},
    "feedback": {"type": Text, "nullable": True},
    "input": {"type": Text, "nullable": True},
    "agent_id": {"type": String, "nullable": True},
    "team_id": {"type": String, "nullable": True},
    "user_id": {"type": String, "nullable": True, "index": True},
    "topics": {"type": JSON, "nullable": True},
    "created_at": {"type": BigInteger, "nullable": False, "index": True},
    "updated_at": {"type": BigInteger, "nullable": True, "index": True},
}
"""

from typing import Optional

from sqlalchemy import JSON, BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Memory(Base):
    """记忆表模型"""

    __tablename__ = "memories"

    # 主键为字符串类型的 memory_id
    memory_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False, comment="记忆ID")

    # 核心内容字段
    memory: Mapped[dict] = mapped_column(JSON, nullable=False, comment="记忆内容(JSON)")

    # 可选的文本类字段
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="反馈")
    input: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="输入")

    # 关联信息(不强制外键约束，按需求仅索引/存储)
    agent_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Agent ID")
    team_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="团队ID")
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True, comment="用户ID(String)")

    # 主题列表(JSON数组)
    topics: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="主题列表(JSON 数组)")

    # 时间戳(Unix 时间，BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="创建时间(Unix 时间戳)")
    updated_at: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, index=True, comment="更新时间(Unix 时间戳)"
    )

    def __repr__(self) -> str:
        return f"<Memory(memory_id={self.memory_id})>"
