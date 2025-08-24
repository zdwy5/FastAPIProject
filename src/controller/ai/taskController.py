from typing import List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session

from src.dao import appScheduleTaskDao
from src.dao import appScheduleTaskDao
from src.dao import userGroupDao
from src.db.db import get_db
from src.pojo.po.appScheduleTaskPo import AppScheduleTask, TaskType, TaskStatus, TaskSource, ImportanceFlag, UrgencyFlag
from src.pojo.po.userGroupPo import UserGroup
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel, Field

# 创建路由
router = APIRouter(prefix="/app/tasks", tags=["任务管理"])

# 请求和响应模型
class TaskCreate(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    content: Optional[str] = None
    is_urgent: Optional[str] = None
    is_important: Optional[str] = None
    attachment: Optional[str] = None
    involved_persons: Optional[str] = None
    watchers: Optional[str] = None
    task_description: Optional[str] = None
    group_id: Optional[int] = None  # 分组ID

    def to_po(self) -> AppScheduleTask:
        """
        将VO转换为PO
        """
        return AppScheduleTask(
            id=uuid.uuid4().hex,
            user_id=self.user_id,
            user_name=self.user_name,
            type=TaskType.TASK.value,
            start_time=self.start_time,
            end_time=self.end_time,
            create_time=datetime.now(),
            content=self.content,
            status=TaskStatus.INCOMPLETE.value,
            source=TaskSource.MANUAL.value,
            is_urgent=self.is_urgent or UrgencyFlag.NOT_URGENT.value,
            is_important=self.is_important or ImportanceFlag.NOT_IMPORTANT.value,
            attachment=self.attachment or "",
            involved_persons=self.involved_persons or "",
            watchers=self.watchers or "",
            task_description=self.task_description or "",
            group_id=self.group_id or 0
        )

class TaskUpdate(BaseModel):
    user_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    content: Optional[str] = None
    status: Optional[TaskStatus] = None
    is_urgent: Optional[UrgencyFlag] = None
    is_important: Optional[ImportanceFlag] = None
    attachment: Optional[str] = None
    involved_persons: Optional[str] = None
    watchers: Optional[str] = None
    task_description: Optional[str] = None
    group_id: Optional[int] = None  # 分组ID

class BatchTaskCreate(BaseModel):
    tasks: List[TaskCreate]

class TaskSearch(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    status: Optional[TaskStatus] = None
    is_urgent: Optional[UrgencyFlag] = None
    is_important: Optional[ImportanceFlag] = None
    content: Optional[str] = None
    involved_persons: Optional[str] = None
    watchers: Optional[str] = None

class CompleteParams(BaseModel):
    task_id: str
    is_complete: bool = True



class TaskCreateResponse(BaseModel):
    task: AppScheduleTask
    message: str = "任务创建成功"

# API接口 - 基本CRUD操作
@router.post("", response_model=HttpResponseModel[TaskCreateResponse])
async def create_task(
    task_create: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    创建任务
    
    Args:
        task_create: 任务创建数据
        db: 数据库会话
        
    Returns:
        创建后的任务信息
    """
    try:
        # 转换为PO并创建任务
        new_task = task_create.to_po()
        created_task = appScheduleTaskDao.create_schedule_task(db, new_task)
        # 同步到 user_group 表
        userGroupDao.create_user_group_if_not_exists(db, new_task.user_id, new_task.group_id)

        # 构建响应数据
        response_data = TaskCreateResponse(
            task=created_task,
            message="任务创建成功"
        )
        
        return HttpResponse.success(response_data)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[AppScheduleTask]])
async def batch_create_tasks(
    batch_data: BatchTaskCreate,
    db: Session = Depends(get_db)
):
    """
    批量创建任务
    
    Args:
        batch_data: 批量任务创建数据
        db: 数据库会话
        
    Returns:
        创建后的任务列表
    """
    try:
        # 转换为PO并批量创建
        new_tasks = [task.to_po() for task in batch_data.tasks]
        created_tasks = appScheduleTaskDao.batch_create_schedule_tasks(db, new_tasks)
        return HttpResponse.success(created_tasks)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.get("/get", response_model=HttpResponseModel[AppScheduleTask])
async def get_task(
    task_id: str = Query(..., description="任务ID"),
    user_id: str = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取任务详情
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        任务详情
    """
    task = appScheduleTaskDao.get_schedule_task_by_id(db, task_id)
    if not task:
        return HttpResponse.error(msg=f"任务不存在: {task_id}")
    
    # 验证任务是否属于该用户
    if task.user_id != user_id:
        return HttpResponse.error(msg=f"无权访问此任务")
        
    return HttpResponse.success(task)

@router.put("/update/{task_id}", response_model=HttpResponseModel[AppScheduleTask])
async def update_task(
    task_update: TaskUpdate,
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """
    更新任务
    
    Args:
        task_id: 任务ID
        task_update: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的任务
    """
    # 转换为字典
    update_data = task_update.model_dump(exclude_unset=True)
    
    # 更新任务
    updated_task = appScheduleTaskDao.update_schedule_task(db, task_id, update_data)
    if not updated_task:
        return HttpResponse.error(msg=f"任务不存在: {task_id}")
    # 同步到 user_group 表
    userGroupDao.create_user_group_if_not_exists(db, updated_task.user_id, updated_task.group_id)
    
    return HttpResponse.success(updated_task)

@router.delete("/del/{task_id}", response_model=HttpResponseModel[bool])
async def delete_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """
    删除任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    try:
        # 软删除相关的分组关系
        userGroupDao.soft_delete_user_groups_by_task_id(db, task_id)
        
        # 删除任务
        result = appScheduleTaskDao.delete_schedule_task(db, task_id)
        if not result:
            return HttpResponse.error(msg=f"任务不存在: {task_id}")
        
        return HttpResponse.success(True)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/search", response_model=HttpResponseModel[List[AppScheduleTask]])
async def search_tasks(
    search_params: TaskSearch,
    db: Session = Depends(get_db)
):
    """
    搜索任务
    
    Args:
        search_params: 搜索参数
        db: 数据库会话
        
    Returns:
        符合条件的任务列表
    """
    try:
        # 将搜索参数转换为字典，排除未设置的字段
        search_dict = {k: v for k, v in search_params.model_dump().items() if v is not None}
        
        # 添加任务类型过滤
        search_dict['type'] = TaskType.TASK.value
        
        # 搜索任务
        tasks = appScheduleTaskDao.search_schedule_tasks(db, search_dict)
        return HttpResponse.success(list(tasks))
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.get("/user/{user_id}", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_user_tasks(
    user_id: str = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有任务
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        用户的任务列表
    """
    # 获取用户的所有任务，过滤任务类型
    all_tasks = appScheduleTaskDao.get_schedule_tasks_by_user_id(db, user_id)
    tasks = [task for task in all_tasks if task.type == TaskType.TASK.value]
    return HttpResponse.success(tasks)

@router.post("/complete", response_model=HttpResponseModel[AppScheduleTask])
async def mark_task_as_complete(
    params: CompleteParams,
    db: Session = Depends(get_db)
):
    """
    将任务标记为已完成
    
    Args:
        params: 完成参数
        db: 数据库会话
        
    Returns:
        更新后的任务
    """
    completed_task = appScheduleTaskDao.mark_schedule_task_as_complete(db, params.task_id, params.is_complete)
    if not completed_task:
        return HttpResponse.error(msg=f"任务不存在: {params.task_id}")
    
    return HttpResponse.success(completed_task, msg="标记完成成功")

 