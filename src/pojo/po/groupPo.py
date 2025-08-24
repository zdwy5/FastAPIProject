from datetime import datetime
from typing import Optional, ClassVar, List

from sqlmodel import SQLModel, Field, Index


class Group(SQLModel, table=True):
    """
    分组表模型
    """
    __tablename__ = "group"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "分组表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "name"
    ]

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="分组ID，主键",
        sa_column_kwargs={"comment": "分组ID，主键"}
    )

    name: str = Field(
        max_length=100,
        description="分组名称",
        sa_column_kwargs={"comment": "分组名称"}
    )

    parent_id: Optional[int] = Field(
        default=None,
        description="父分组ID，顶级分组为NULL",
        sa_column_kwargs={"comment": "父分组ID，顶级分组为NULL"}
    )

    level: int = Field(
        default=1,
        description="分组层级，1级为顶级分组",
        sa_column_kwargs={"comment": "分组层级，1级为顶级分组"}
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
            Index("idx_parent_id", "parent_id"),
            Index("idx_level", "level"),
            Index("idx_deleted_at", "deleted_at")
        ] 