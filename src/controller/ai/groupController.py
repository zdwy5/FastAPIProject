from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session

from src.dao import groupDao, userGroupDao
from src.db.db import get_db
from src.pojo.po.groupPo import Group
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel, Field

# 创建路由
router = APIRouter(prefix="/app/groups", tags=["分组管理"])

# 请求和响应模型
class GroupCreate(BaseModel):
    name: str = Field(..., description="分组名称")
    creator_id: str = Field(..., description="创建者用户ID")
    parent_id: Optional[int] = Field(None, description="父分组ID，顶级分组为NULL，不传或传null表示顶级分组")
    level: int = Field(1, description="分组层级，1级为顶级分组")

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    level: Optional[int] = Field(None, description="分组层级")

class GroupResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int
    created_at: datetime
    updated_at: datetime

# API接口 - 基本CRUD操作
@router.post("", response_model=HttpResponseModel[GroupResponse])
async def create_group(
    group_create: GroupCreate,
    db: Session = Depends(get_db)
):
    """
    创建分组
    
    Args:
        group_create: 分组创建数据
        db: 数据库会话
        
    Returns:
        创建后的分组
        
    Note:
        创建分组后会自动将创建者添加到用户分组关系表中
    """
    try:
        # 创建分组PO对象
        new_group = Group(
            name=group_create.name,
            parent_id=group_create.parent_id,
            level=group_create.level,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        created_group = groupDao.create_group(db, new_group)
        
        # 自动创建用户分组关系（如果不存在）
        userGroupDao.create_user_group_if_not_exists(db, group_create.creator_id, created_group.id)
        
        # 手动构建响应数据，避免model_dump的问题
        response_data = {
            'id': created_group.id,
            'name': created_group.name,
            'parent_id': created_group.parent_id,
            'level': created_group.level,
            'created_at': created_group.created_at,
            'updated_at': created_group.updated_at
        }
        
        return HttpResponse.success(GroupResponse(**response_data))
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.get("/get/{group_id}", response_model=HttpResponseModel[GroupResponse])
async def get_group(
    group_id: int = Path(..., description="分组ID"),
    db: Session = Depends(get_db)
):
    """
    获取分组详情
    
    Args:
        group_id: 分组ID
        db: 数据库会话
        
    Returns:
        分组详情
    """
    group = groupDao.get_group_by_id(db, group_id)
    if not group:
        return HttpResponse.error(msg=f"分组不存在: {group_id}")
        
    return HttpResponse.success(GroupResponse(**group.model_dump()))

@router.put("/update/{group_id}", response_model=HttpResponseModel[GroupResponse])
async def update_group(
    group_update: GroupUpdate,
    group_id: int = Path(..., description="分组ID"),
    db: Session = Depends(get_db)
):
    """
    更新分组
    
    Args:
        group_id: 分组ID
        group_update: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的分组
    """
    try:
        # 转换为字典，排除未设置的字段
        update_data = {k: v for k, v in group_update.model_dump().items() if v is not None}
        
        # 更新分组
        updated_group = groupDao.update_group(db, group_id, update_data)
        if not updated_group:
            return HttpResponse.error(msg=f"分组不存在: {group_id}")
        
        return HttpResponse.success(GroupResponse(**updated_group.model_dump()))
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.delete("/del/{group_id}", response_model=HttpResponseModel[bool])
async def delete_group(
    group_id: int = Path(..., description="分组ID"),
    db: Session = Depends(get_db)
):
    """
    软删除分组
    
    Args:
        group_id: 分组ID
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    try:
        result = groupDao.soft_delete_group(db, group_id)
        if not result:
            return HttpResponse.error(msg=f"分组不存在: {group_id}")
        
        return HttpResponse.success(True, msg="分组删除成功")
    except Exception as e:
        return HttpResponse.error(msg=str(e))



@router.get("/all", response_model=HttpResponseModel[List[GroupResponse]])
async def get_all_groups(
    db: Session = Depends(get_db)
):
    """
    获取所有未删除的分组
    
    Args:
        db: 数据库会话
        
    Returns:
        所有分组列表
    """
    try:
        groups = groupDao.get_all_active_groups(db)
        return HttpResponse.success([GroupResponse(**group.model_dump()) for group in groups])
    except Exception as e:
        return HttpResponse.error(msg=str(e))


@router.get("/level/{level}", response_model=HttpResponseModel[List[GroupResponse]])
async def get_groups_by_level(
    level: int = Path(..., description="分组层级", ge=1, le=3),
    db: Session = Depends(get_db)
):
    """
    根据层级获取分组
    
    Args:
        level: 分组层级
        db: 数据库会话
        
    Returns:
        指定层级的分组列表
    """
    try:
        groups = groupDao.get_groups_by_level(db, level)
        return HttpResponse.success([GroupResponse(**group.model_dump()) for group in groups])
    except Exception as e:
        return HttpResponse.error(msg=str(e))


@router.get("/children/{parent_id}", response_model=HttpResponseModel[List[GroupResponse]])
async def get_child_groups(
    parent_id: int = Path(..., description="父分组ID"),
    db: Session = Depends(get_db)
):
    """
    获取指定分组的子分组
    
    Args:
        parent_id: 父分组ID
        db: 数据库会话
        
    Returns:
        子分组列表
    """
    try:
        groups = groupDao.get_child_groups(db, parent_id)
        return HttpResponse.success([GroupResponse(**group.model_dump()) for group in groups])
    except Exception as e:
        return HttpResponse.error(msg=str(e))


@router.get("/parent/{group_id}", response_model=HttpResponseModel[GroupResponse])
async def get_parent_group(
    group_id: int = Path(..., description="分组ID"),
    db: Session = Depends(get_db)
):
    """
    获取指定分组的父分组
    
    Args:
        group_id: 分组ID
        db: 数据库会话
        
    Returns:
        父分组信息
    """
    try:
        parent_group = groupDao.get_parent_group(db, group_id)
        if not parent_group:
            return HttpResponse.error(msg="该分组没有父分组或父分组不存在")
        
        return HttpResponse.success(GroupResponse(**parent_group.model_dump()))
    except Exception as e:
        return HttpResponse.error(msg=str(e))


 