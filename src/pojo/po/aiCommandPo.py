from datetime import datetime
from typing import Optional, ClassVar, List

from sqlmodel import SQLModel, Field
from sqlalchemy import JSON


class AICommand(SQLModel, table=True):
    """
    AI 指令管理表模型
    对应表: ai_command
    """
    __tablename__ = "ai_command"

    __table_args__ = {
        "comment": "AI指令管理表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci",
    }

    # 建议用于模糊搜索的字段
    like_search_fields: ClassVar[List[str]] = [
        "command_code", "command_name", "trigger_keywords", "handler_target", "remark"
    ]

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="雪花ID",
        sa_column_kwargs={"comment": "雪花ID"},
    )

    command_code: str = Field(
        max_length=64,
        index=True,
        description="指令编码",
        sa_column_kwargs={"comment": "指令编码"},
    )

    command_name: str = Field(
        max_length=128,
        description="指令名称",
        sa_column_kwargs={"comment": "指令名称"},
    )

    category_id: Optional[int] = Field(
        default=None,
        description="指令分类ID",
        sa_column_kwargs={"comment": "指令分类ID"},
    )

    trigger_keywords: str = Field(
        max_length=255,
        description="指令触发的关键词",
        sa_column_kwargs={"comment": "指令触发的关键词"},
    )

    handler_type: str = Field(
        max_length=32,
        description="处理器类型: CLASS/METHOD/URL",
        sa_column_kwargs={"comment": "处理器类型: CLASS/METHOD/URL"},
    )

    handler_target: str = Field(
        max_length=255,
        description="处理器目标(类名/方法/URL)",
        sa_column_kwargs={"comment": "处理器目标(类名/方法/URL)"},
    )

    command_params: Optional[dict] = Field(
        default=None,
        sa_type=JSON,
        description="指令参数配置，JSON格式",
        sa_column_kwargs={"comment": "指令参数配置，JSON格式"},
    )

    remark: Optional[str] = Field(
        default=None,
        max_length=255,
        description="备注",
        sa_column_kwargs={"comment": "备注"},
    )

    status: int = Field(
        default=1,
        description="状态：0-禁用，1-启用",
        sa_column_kwargs={"comment": "状态：0-禁用，1-启用"},
    )

    priority: Optional[int] = Field(
        default=50,
        description="优先级(1-100)，值越大优先级越高",
        sa_column_kwargs={"comment": "优先级(1-100)，值越大优先级越高"},
    )

    creator: str = Field(
        max_length=64,
        description="创建人",
        sa_column_kwargs={"comment": "创建人"},
    )

    create_time: Optional[datetime] = Field(
        default=None,
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"},
    )

    update_time: Optional[datetime] = Field(
        default=None,
        description="更新时间",
        sa_column_kwargs={"comment": "更新时间"},
    ) 