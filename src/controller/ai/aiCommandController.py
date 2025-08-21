from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from src.pojo.po.aiCommandPo import AICommand
from pydantic import BaseModel, Field
from src.dao.aiCommandDao import (
    create_ai_command,
    batch_create_ai_commands,
    get_command_by_id,
    get_command_by_code,
    update_ai_command,
    delete_ai_command,
    search_ai_commands,
    count_ai_commands,
)

router = APIRouter(prefix="/ai/commands", tags=["AI 指令管理"])


class AICommandCreate(BaseModel):
    command_code: str = Field(..., max_length=64, description="指令编码")
    command_name: str = Field(..., max_length=128, description="指令名称")
    category_id: Optional[int] = Field(None, description="指令分类ID")
    trigger_keywords: str = Field(..., max_length=255, description="触发关键词，逗号分隔或空格分隔")
    handler_type: str = Field(..., max_length=32, description="处理器类型: CLASS/METHOD/URL")
    handler_target: str = Field(..., max_length=255, description="处理器目标(类名/方法/URL)")
    command_params: Optional[Dict[str, Any]] = Field(None, description="指令参数配置，JSON")
    remark: Optional[str] = Field(None, max_length=255, description="备注")
    status: int = Field(1, description="状态：0-禁用，1-启用")
    priority: int = Field(50, description="优先级(1-100)")
    creator: str = Field(..., max_length=64, description="创建人")

    def to_po(self) -> AICommand:
        return AICommand(
            command_code=self.command_code,
            command_name=self.command_name,
            category_id=self.category_id,
            trigger_keywords=self.trigger_keywords,
            handler_type=self.handler_type,
            handler_target=self.handler_target,
            command_params=self.command_params,
            remark=self.remark,
            status=self.status,
            priority=self.priority,
            creator=self.creator,
            create_time=datetime.now(),
            update_time=datetime.now(),
        )


class AICommandUpdate(BaseModel):
    command_code: Optional[str] = None
    command_name: Optional[str] = None
    category_id: Optional[int] = None
    trigger_keywords: Optional[str] = None
    handler_type: Optional[str] = None
    handler_target: Optional[str] = None
    command_params: Optional[Dict[str, Any]] = None
    remark: Optional[str] = None
    status: Optional[int] = None
    priority: Optional[int] = None


class AICommandSearch(BaseModel):
    status: Optional[int] = Field(None, description="状态过滤")
    category_id: Optional[int] = Field(None, description="分类过滤")
    handler_type: Optional[str] = Field(None, description="处理器类型")
    creator: Optional[str] = Field(None, description="创建人")
    keyword: Optional[str] = Field(None, description="模糊搜索：编码/名称/关键词/目标/备注")


@router.post("", response_model=HttpResponseModel[AICommand])
async def create(command: AICommandCreate, db: Session = Depends(get_db)):
    po = command.to_po()
    created = create_ai_command(db, po)
    return HttpResponse.success(created)


@router.post("/batch", response_model=HttpResponseModel[List[AICommand]])
async def batch_create(commands: List[AICommandCreate], db: Session = Depends(get_db)):
    pos = [c.to_po() for c in commands]
    created = batch_create_ai_commands(db, pos)
    return HttpResponse.success(created)


@router.get("/{command_id}", response_model=HttpResponseModel[AICommand])
async def get_by_id(command_id: int, db: Session = Depends(get_db)):
    command = get_command_by_id(db, command_id)
    return HttpResponse.success(command)


@router.get("/code/{command_code}", response_model=HttpResponseModel[AICommand])
async def get_by_code(command_code: str, db: Session = Depends(get_db)):
    command = get_command_by_code(db, command_code)
    return HttpResponse.success(command)


@router.put("/{command_id}", response_model=HttpResponseModel[AICommand])
async def update(command_id: int, update_data: AICommandUpdate, db: Session = Depends(get_db)):
    updated = update_ai_command(db, command_id, update_data.model_dump(exclude_none=True))
    return HttpResponse.success(updated)


@router.delete("/{command_id}", response_model=HttpResponseModel[bool])
async def delete(command_id: int, db: Session = Depends(get_db)):
    ok = delete_ai_command(db, command_id)
    return HttpResponse.success(ok)


@router.post("/search", response_model=HttpResponseModel[List[AICommand]])
async def search(
    search_params: AICommandSearch,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=0, le=500),
    offset: int = Query(0, ge=0),
    order_by_priority_desc: bool = Query(True),
):
    results = search_ai_commands(
        db,
        filters=search_params.model_dump(exclude_none=True),
        limit=limit,
        offset=offset,
        order_by_priority_desc=order_by_priority_desc,
    )
    return HttpResponse.success(results) 