from typing import Optional, Dict, Any, Sequence, List

from sqlmodel import Session, select

from src.exception.aiException import AIException
from src.pojo.po.aiCommandPo import AICommand


def create_ai_command(session: Session, command: AICommand) -> AICommand:
    """创建AI指令（校验唯一command_code）"""
    exists = get_command_by_code(session, command.command_code)
    if exists:
        raise AIException.quick_raise(f"指令编码已存在: {command.command_code}")
    session.add(command)
    session.commit()
    session.refresh(command)
    return command


def batch_create_ai_commands(session: Session, commands: List[AICommand]) -> List[AICommand]:
    """批量创建AI指令（逐条校验）"""
    created: List[AICommand] = []
    for cmd in commands:
        created.append(create_ai_command(session, cmd))
    return created


def get_command_by_id(session: Session, command_id: int) -> Optional[AICommand]:
    statement = select(AICommand).where(AICommand.id == command_id)
    return session.exec(statement).first()


def get_command_by_code(session: Session, command_code: str) -> Optional[AICommand]:
    statement = select(AICommand).where(AICommand.command_code == command_code)
    return session.exec(statement).first()


def update_ai_command(session: Session, command_id: int, update_data: Dict[str, Any]) -> AICommand:
    command = get_command_by_id(session, command_id)
    if not command:
        raise AIException.quick_raise(f"未找到指令: {command_id}")

    # 不允许修改唯一编码到已存在的值
    new_code = update_data.get("command_code")
    if new_code and new_code != command.command_code:
        if get_command_by_code(session, new_code):
            raise AIException.quick_raise(f"指令编码已存在: {new_code}")

    for field, value in update_data.items():
        if hasattr(command, field) and value is not None:
            setattr(command, field, value)

    session.add(command)
    session.commit()
    session.refresh(command)
    return command


def delete_ai_command(session: Session, command_id: int) -> bool:
    command = get_command_by_id(session, command_id)
    if not command:
        return False
    session.delete(command)
    session.commit()
    return True


def search_ai_commands(
    session: Session,
    filters: Dict[str, Any],
    limit: int = 50,
    offset: int = 0,
    order_by_priority_desc: bool = True,
) -> Sequence[AICommand]:
    """
    动态条件搜索：
    - 支持按状态、分类、handler_type 等精确匹配
    - 支持 command_name / command_code / trigger_keywords 模糊搜索
    - 按优先级排序（默认倒序）
    """
    statement = select(AICommand)

    # 精确匹配
    exact_fields = [
        "status",
        "category_id",
        "handler_type",
        "creator",
    ]

    for field in exact_fields:
        value = filters.get(field)
        if value is not None:
            statement = statement.where(getattr(AICommand, field) == value)

    # 模糊搜索
    keyword = filters.get("keyword")
    if keyword:
        like = f"%{keyword}%"
        statement = statement.where(
            (AICommand.command_name.like(like))
            | (AICommand.command_code.like(like))
            | (AICommand.trigger_keywords.like(like))
            | (AICommand.handler_target.like(like))
            | (AICommand.remark.like(like))
        )

    # 排序
    if order_by_priority_desc:
        statement = statement.order_by(AICommand.priority.desc())
    else:
        statement = statement.order_by(AICommand.priority)

    # 分页
    if offset:
        statement = statement.offset(offset)
    if limit:
        statement = statement.limit(limit)

    return session.exec(statement).all()


def count_ai_commands(session: Session, filters: Dict[str, Any]) -> int:
    """统计数量（与 search 条件一致）"""
    # 简化实现：直接取全部再计数（小规模足够，后续可改为select(func.count())）
    return len(search_ai_commands(session, filters, limit=0, offset=0)) 