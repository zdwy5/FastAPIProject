from typing import Optional, List, Sequence
from datetime import datetime

from sqlmodel import Session, select, update, delete
from sqlalchemy import and_

from src.pojo.po.userGroupPo import UserGroup


def create_user_group(session: Session, user_group: UserGroup) -> UserGroup:
    """
    创建用户分组关系

    Args:
        session: 数据库会话
        user_group: 用户分组关系模型实例

    Returns:
        创建后的用户分组关系模型实例
    """
    session.add(user_group)
    session.commit()
    session.refresh(user_group)
    return user_group


def get_user_group_by_id(session: Session, relation_id: int) -> Optional[UserGroup]:
    """
    通过ID获取用户分组关系

    Args:
        session: 数据库会话
        relation_id: 关系ID

    Returns:
        用户分组关系模型实例，如果不存在则返回None
    """
    statement = select(UserGroup).where(
        and_(
            UserGroup.id == relation_id,
            UserGroup.deleted_at.is_(None)
        )
    )
    result = session.exec(statement).first()
    return result


def get_user_groups_by_user_id(session: Session, user_id: str) -> List[UserGroup]:
    """
    获取用户的所有分组关系

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        用户分组关系列表
    """
    statement = select(UserGroup).where(
        and_(
            UserGroup.user_id == user_id,
            UserGroup.deleted_at.is_(None)
        )
    ).order_by(UserGroup.created_at.desc())
    result = session.exec(statement).all()
    return list(result)


def get_user_groups_by_group_id(session: Session, group_id: int) -> List[UserGroup]:
    """
    获取分组的所有用户关系

    Args:
        session: 数据库会话
        group_id: 分组ID

    Returns:
        用户分组关系列表
    """
    statement = select(UserGroup).where(
        and_(
            UserGroup.group_id == group_id,
            UserGroup.deleted_at.is_(None)
        )
    ).order_by(UserGroup.created_at.desc())
    result = session.exec(statement).all()
    return list(result)


def check_user_group_exists(session: Session, user_id: str, group_id: int) -> bool:
    """
    检查用户分组关系是否已存在

    Args:
        session: 数据库会话
        user_id: 用户ID
        group_id: 分组ID

    Returns:
        如果关系存在返回True，否则返回False
    """
    statement = select(UserGroup).where(
        and_(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id,
            UserGroup.deleted_at.is_(None)
        )
    )
    result = session.exec(statement).first()
    return result is not None


def create_user_group_if_not_exists(session: Session, user_id: str, group_id: int) -> Optional[UserGroup]:
    """
    如果用户分组关系不存在则创建，否则返回现有关系

    Args:
        session: 数据库会话
        user_id: 用户ID
        group_id: 分组ID

    Returns:
        用户分组关系对象
    """
    # 检查关系是否已存在
    if check_user_group_exists(session, user_id, group_id):
        # 如果已存在，返回现有关系
        statement = select(UserGroup).where(
            and_(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id,
                UserGroup.deleted_at.is_(None)
            )
        )
        return session.exec(statement).first()
    
    # 如果不存在，创建新关系
    user_group = UserGroup(
        user_id=user_id,
        group_id=group_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return create_user_group(session, user_group)


def update_user_group(session: Session, relation_id: int, update_data: dict) -> Optional[UserGroup]:
    """
    更新用户分组关系

    Args:
        session: 数据库会话
        relation_id: 关系ID
        update_data: 更新数据字典

    Returns:
        更新后的用户分组关系模型实例，如果不存在则返回None
    """
    # 添加更新时间
    update_data["updated_at"] = datetime.now()
    
    statement = update(UserGroup).where(
        and_(
            UserGroup.id == relation_id,
            UserGroup.deleted_at.is_(None)
        )
    ).values(**update_data)
    
    session.exec(statement)
    session.commit()
    
    # 返回更新后的关系
    return get_user_group_by_id(session, relation_id)


def soft_delete_user_group(session: Session, relation_id: int) -> bool:
    """
    软删除用户分组关系

    Args:
        session: 数据库会话
        relation_id: 关系ID

    Returns:
        是否成功删除
    """
    statement = update(UserGroup).where(
        and_(
            UserGroup.id == relation_id,
            UserGroup.deleted_at.is_(None)
        )
    ).values(deleted_at=datetime.now())
    
    result = session.exec(statement)
    session.commit()
    
    return result.rowcount > 0


def soft_delete_user_groups_by_task_id(session: Session, task_id: str) -> bool:
    """
    根据任务ID软删除相关的用户分组关系

    Args:
        session: 数据库会话
        task_id: 任务ID

    Returns:
        是否成功删除
    """
    # 这里需要根据具体的业务逻辑来实现
    # 暂时返回True，具体实现需要根据任务和分组的关系来设计
    return True


def get_all_active_user_groups(session: Session) -> List[UserGroup]:
    """
    获取所有未删除的用户分组关系

    Args:
        session: 数据库会话

    Returns:
        用户分组关系列表
    """
    statement = select(UserGroup).where(
        UserGroup.deleted_at.is_(None)
    ).order_by(UserGroup.created_at.desc())
    result = session.exec(statement).all()
    return list(result) 