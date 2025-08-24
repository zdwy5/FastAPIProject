from typing import Optional, List, Sequence
from datetime import datetime

from sqlmodel import Session, select, update
from sqlalchemy import and_

from src.pojo.po.groupPo import Group


def create_group(session: Session, group: Group) -> Group:
    """
    创建分组

    Args:
        session: 数据库会话
        group: 分组模型实例

    Returns:
        创建后的分组模型实例
    """
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_group_by_id(session: Session, group_id: int) -> Optional[Group]:
    """
    通过ID获取分组

    Args:
        session: 数据库会话
        group_id: 分组ID

    Returns:
        分组模型实例，如果不存在则返回None
    """
    statement = select(Group).where(
        and_(
            Group.id == group_id,
            Group.deleted_at.is_(None)
        )
    )
    result = session.exec(statement).first()
    return result


def update_group(session: Session, group_id: int, update_data: dict) -> Optional[Group]:
    """
    更新分组

    Args:
        session: 数据库会话
        group_id: 分组ID
        update_data: 更新数据字典

    Returns:
        更新后的分组模型实例，如果不存在则返回None
    """
    # 添加更新时间
    update_data["updated_at"] = datetime.now()
    
    statement = update(Group).where(
        and_(
            Group.id == group_id,
            Group.deleted_at.is_(None)
        )
    ).values(**update_data)
    
    session.exec(statement)
    session.commit()
    
    # 返回更新后的分组
    return get_group_by_id(session, group_id)


def soft_delete_group(session: Session, group_id: int) -> bool:
    """
    软删除分组

    Args:
        session: 数据库会话
        group_id: 分组ID

    Returns:
        是否成功删除
    """
    statement = update(Group).where(
        and_(
            Group.id == group_id,
            Group.deleted_at.is_(None)
        )
    ).values(deleted_at=datetime.now())
    
    result = session.exec(statement)
    session.commit()
    
    return result.rowcount > 0


def get_all_active_groups(session: Session) -> List[Group]:
    """
    获取所有未删除的分组

    Args:
        session: 数据库会话

    Returns:
        分组列表
    """
    statement = select(Group).where(
        Group.deleted_at.is_(None)
    ).order_by(Group.level, Group.created_at.desc())
    result = session.exec(statement).all()
    return list(result)


def get_groups_by_level(session: Session, level: int) -> List[Group]:
    """
    根据层级获取分组

    Args:
        session: 数据库会话
        level: 分组层级

    Returns:
        分组列表
    """
    statement = select(Group).where(
        and_(
            Group.level == level,
            Group.deleted_at.is_(None)
        )
    ).order_by(Group.created_at.desc())
    result = session.exec(statement).all()
    return list(result)


def get_child_groups(session: Session, parent_id: int) -> List[Group]:
    """
    获取指定分组的子分组

    Args:
        session: 数据库会话
        parent_id: 父分组ID

    Returns:
        子分组列表
    """
    statement = select(Group).where(
        and_(
            Group.parent_id == parent_id,
            Group.deleted_at.is_(None)
        )
    ).order_by(Group.created_at.desc())
    result = session.exec(statement).all()
    return list(result)


def get_parent_group(session: Session, group_id: int) -> Optional[Group]:
    """
    获取指定分组的父分组

    Args:
        session: 数据库会话
        group_id: 分组ID

    Returns:
        父分组，如果不存在则返回None
    """
    group = get_group_by_id(session, group_id)
    if group and group.parent_id:
        return get_group_by_id(session, group.parent_id)
    return None


 