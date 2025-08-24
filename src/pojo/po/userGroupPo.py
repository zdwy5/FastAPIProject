from datetime import datetime
from typing import Optional, ClassVar, List

from sqlmodel import SQLModel, Field, Index


class UserGroup(SQLModel, table=True):
    """
    用户分组关系表模型
    """
    __tablename__ = "user_group"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "用户分组关系表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = []

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="关系ID，主键",
        sa_column_kwargs={"comment": "关系ID，主键"}
    )

    user_id: str = Field(
        max_length=64,
        description="用户ID",
        sa_column_kwargs={"comment": "用户ID"}
    )

    group_id: int = Field(
        description="分组ID",
        sa_column_kwargs={"comment": "分组ID"}
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间",
        sa_column_kwargs={"comment": "更新时间"}
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        description="删除时间(软删除)",
        sa_column_kwargs={"comment": "删除时间(软删除)"}
    )

    # 定义索引
    class Config:
        indexes = [
            Index("idx_user_id", "user_id"),
            Index("idx_group_id", "group_id"),
            Index("idx_deleted_at", "deleted_at")
        ] 