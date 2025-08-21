import uuid
from datetime import datetime, timezone
from typing import Optional, ClassVar, List

from pydantic import BaseModel
from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index

from src.pojo.po.sessionDetailPo import SessionDetail


class SessionFieldsMixin:
    """
    会话字段混入类，包含所有共享字段定义
    """
    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "session_title", "session_desc", "history_semantic"
    ]

    id: str = Field(
        primary_key=True,
        max_length=64,
        description="唯一标识",
        sa_column_kwargs={"comment": "唯一标识"}
    )

    dify_conversation_id: Optional[str] = Field(
        max_length=64,
        description="dify的会话ID",
        sa_column_kwargs={"comment": "dify的会话ID"}
    )

    session_title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="会话标题",
        sa_column_kwargs={"comment": "会话标题"}
    )

    session_desc: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="会话描述",
        sa_column_kwargs={"comment": "会话描述"}
    )

    create_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    update_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="更新时间",
        sa_column_kwargs={"comment": "更新时间"}
    )

    user_id: str = Field(
        max_length=64,
        index=True,
        description="用户ID",
        sa_column_kwargs={"comment": "用户ID"}
    )

    token: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="token",
        sa_column_kwargs={"comment": "token"}
    )

    history_semantic: Optional[str] = Field(
        default=None,
        description="历史会话语义",
        sa_column_kwargs={"comment": "历史会话语义"}
    )


class SessionPo(SessionFieldsMixin, SQLModel, table=True):
    """
    会话表模型
    """
    __tablename__ = "session"
    
    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "会话表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义索引
    class Config:
        indexes = [
            Index("idx_user_id", "user_id"),
            Index("idx_create_time", "create_time")
        ]

    @classmethod
    def get_default(cls) -> "SessionPo":
        """
        获取默认实例
        :return:
        """
        return cls(
            id=uuid.uuid4().hex,
            session_title="新会话",
            session_desc="暂时没有更多描述",
            create_time=datetime.now(timezone.utc),
            update_time=datetime.now(timezone.utc)
        )

    def to_session_info(self, history: Optional[List[SessionDetail]] = None) -> "SessionInfo":
        """
        将Session实例转换为SessionInfo实例

        Args:
            history: 可选的历史会话详情列表

        Returns:
            SessionInfo实例
        """
        # 获取所有共享字段的值
        shared_fields = {
            field: getattr(self, field)
            for field in SessionFieldsMixin.__annotations__
            if hasattr(self, field)
        }

        # 将SessionDetail列表转换为字典列表
        history_data = [item.model_dump() for item in history] if history else None

        # 创建SessionInfo实例
        return SessionInfo(
            **shared_fields,
            history=history_data
        )


class SessionInfo(SessionFieldsMixin, BaseModel):
    """
    会话信息接口返回结构
    """
    history: Optional[List[SessionDetail]] = Field(
        default=None,
        description="历史会话",
    )