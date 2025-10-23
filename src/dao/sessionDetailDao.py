from typing import Optional, Dict, List, Any, Sequence

from sqlmodel import Session, select, delete, update

from src.pojo.po.sessionDetailPo import SessionDetail
from src.pojo.po.sessionPo import SessionPo
from sqlalchemy import func


def create_session_detail(session: Session, session_detail: SessionDetail) -> SessionDetail:
    """
    创建会话详情

    Args:
        session: 数据库会话
        session_detail: 会话详情模型实例

    Returns:
        创建后的会话详情模型实例
    """
    session_detail.handle_dict()
    session.add(session_detail)
    session.commit()
    session.refresh(session_detail)
    return session_detail

def batch_create_session_details(session: Session, session_details: List[SessionDetail]) -> List[SessionDetail]:
    """
    批量创建会话详情

    Args:
        session: 数据库会话
        session_details: 会话详情模型实例列表

    Returns:
        创建后的会话详情模型实例列表
    """
    session.add_all(session_details)
    session.commit()
    for detail in session_details:
        session.refresh(detail)
    return session_details

def get_session_detail_by_id(session: Session, detail_id: str) -> Optional[SessionDetail]:
    """
    通过ID获取会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID

    Returns:
        会话详情模型实例，如果不存在则返回None
    """
    statement = select(SessionDetail).where(SessionDetail.id == detail_id)
    result = session.exec(statement).first()
    return result

def get_session_details_by_session_id(session: Session, session_id: str) -> Sequence[SessionDetail]:
    """
    通过会话ID获取会话详情列表

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        会话详情模型实例列表
    """
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id).order_by(SessionDetail.create_time.asc())
    results = session.exec(statement).all()
    return results

def search_session_details(session: Session, search_params: Dict[str, Any],limit: int | None = None) -> Sequence[SessionDetail]:
    """
    根据提供的参数搜索会话详情，使用SessionDetail中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为SessionDetail的字段名，值为搜索条件
        limit: 搜索结果数量限制
    Returns:
        符合条件的SessionDetail列表
    """
    statement = select(SessionDetail)

    # 获取SessionDetail类的所有字段名
    session_detail_fields = [column.name for column in SessionDetail.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in session_detail_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in SessionDetail.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(SessionDetail, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(SessionDetail, field) == value)

    # 执行查询
    results = session.exec(statement.order_by(SessionDetail.create_time.desc()).limit(limit)).all()
    return results

def search_session_details_by_user_id(session: Session, user_id:str, search_params=None, limit: int | None = None) -> Sequence[SessionDetail]:
    """
    根据提供的参数搜索会话详情，使用SessionDetail中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为SessionDetail的字段名，值为搜索条件
        limit: 搜索结果数量限制
    Returns:
        符合条件的SessionDetail列表
        :param user_id:
    """
    if search_params is None:
        search_params = {}
    statement = select(SessionDetail).join(SessionPo,SessionPo.id == SessionDetail.session_id).where(SessionPo.user_id == user_id)

    # 获取SessionDetail类的所有字段名
    session_detail_fields = [column.name for column in SessionDetail.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in session_detail_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in SessionDetail.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(SessionDetail, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(SessionDetail, field) == value)

    # 执行查询
    results = session.exec(statement.order_by(SessionDetail.create_time.desc()).limit(limit)).all()
    return results

def update_session_detail(session: Session, detail_id: str, update_data: Dict[str, Any]) -> Optional[SessionDetail]:
    """
    更新会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID
        update_data: 要更新的数据字典

    Returns:
        更新后的会话详情模型实例，如果不存在则返回None
    """
    # 先获取会话详情
    db_detail = get_session_detail_by_id(session, detail_id)
    if not db_detail:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_detail, field):
            setattr(db_detail, field, value)

    session.add(db_detail)
    session.commit()
    session.refresh(db_detail)
    return db_detail

def delete_session_detail(session: Session, detail_id: str) -> bool:
    """
    删除会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID

    Returns:
        是否成功删除
    """
    db_detail = get_session_detail_by_id(session, detail_id)
    if not db_detail:
        return False

    session.delete(db_detail)
    session.commit()
    return True

def delete_session_details_by_session_id(session: Session, session_id: str) -> int:
    """
    通过会话ID删除所有相关的会话详情

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        删除的记录数量
    """
    statement = delete(SessionDetail).where(SessionDetail.session_id == session_id)
    result = session.exec(statement)
    session.commit()
    return result.rowcount

def get_latest_session_detail(session: Session, session_id: str) -> Optional[SessionDetail]:
    """
    获取会话的最新详情

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        最新的会话详情模型实例，如果不存在则返回None
    """
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id).order_by(SessionDetail.create_time.desc()).limit(1)
    result = session.exec(statement).first()
    return result

def count_session_details(session: Session, session_id: str) -> int:
    """
    统计会话的详情数量

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        会话详情的数量
    """
    statement = select(func.count()).select_from(SessionDetail).where(SessionDetail.session_id == session_id)
    result = session.exec(statement).one()
    return result

def get_user_house_combinations(session: Session, dialog_carrier: str, page: int = 1, pagesize: int = 10) -> List[Dict[str, Any]]:
    """
    获取所有用户和房源的组合信息，通过session_detail表的dialog_carrier字段过滤，
    然后从api_input字段中提取user和houses_id信息进行分组
    
    Args:
        session: 数据库会话
        dialog_carrier: 对话承载人
        page: 页码（从1开始）
        pagesize: 每页条数
        
    Returns:
        用户和房源组合的列表
    """
    from sqlalchemy import text
    import json
    
    # 计算偏移量
    offset = (page - 1) * pagesize
    
    # 使用原生SQL查询，因为需要解析JSON字段
    sql = text("""
        SELECT DISTINCT 
            JSON_EXTRACT(api_input, '$.user') as user,
            JSON_EXTRACT(api_input, '$.inputs.houses_id') as houses_id
        FROM session_detail 
        WHERE dialog_carrier LIKE :dialog_carrier 
        AND JSON_EXTRACT(api_input, '$.user') IS NOT NULL 
        AND JSON_EXTRACT(api_input, '$.inputs.houses_id') IS NOT NULL
        ORDER BY user, houses_id
        LIMIT :pagesize OFFSET :offset
    """)
    
    result = session.execute(sql, {
        'dialog_carrier': f'%{dialog_carrier}%',
        'pagesize': pagesize,
        'offset': offset
    }).fetchall()
    
    # 转换结果为字典列表
    combinations = []
    for row in result:
        user = row[0]
        houses_id = row[1]
        if user and houses_id:
            combinations.append({
                "user": user.strip('"'),  # 去掉JSON字符串的引号
                "houses_id": int(houses_id) if houses_id.isdigit() else houses_id.strip('"')
            })
    
    return combinations

def get_user_house_combinations_count(session: Session, dialog_carrier: str) -> int:
    """
    获取用户和房源组合的总数量
    
    Args:
        session: 数据库会话
        dialog_carrier: 对话承载人
        
    Returns:
        组合的总数量
    """
    from sqlalchemy import text
    
    sql = text("""
        SELECT COUNT(DISTINCT CONCAT(
            JSON_EXTRACT(api_input, '$.user'), 
            '-', 
            JSON_EXTRACT(api_input, '$.inputs.houses_id')
        )) as total_count
        FROM session_detail 
        WHERE dialog_carrier LIKE :dialog_carrier 
        AND JSON_EXTRACT(api_input, '$.user') IS NOT NULL 
        AND JSON_EXTRACT(api_input, '$.inputs.houses_id') IS NOT NULL
    """)
    
    result = session.execute(sql, {
        'dialog_carrier': f'%{dialog_carrier}%'
    }).fetchone()
    
    return result[0] if result else 0

def search_session_details_by_user_house_with_pagination(session: Session, user_id: str, dialog_carrier: str, house_id: str = None, page: int = 1, pagesize: int = 10) -> Dict[str, Any]:
    """
    根据用户ID、对话承载人和房源ID查询会话详情（带分页）
    
    Args:
        session: 数据库会话
        user_id: 用户ID
        dialog_carrier: 对话承载人
        house_id: 房源ID（可选）
        page: 页码（从1开始）
        pagesize: 每页条数
        
    Returns:
        包含分页信息的会话详情数据
    """
    from sqlalchemy import text
    import json
    
    # 计算偏移量
    offset = (page - 1) * pagesize
    
    # 构建基础查询条件
    where_conditions = [
        "s.user_id = :user_id",
        "sd.dialog_carrier LIKE :dialog_carrier",
        "JSON_EXTRACT(sd.api_input, '$.user') IS NOT NULL"
    ]
    
    params = {
        'user_id': user_id,
        'dialog_carrier': f'%{dialog_carrier}%',
        'pagesize': pagesize,
        'offset': offset
    }
    
    # 如果提供了house_id，添加房源ID过滤条件
    if house_id:
        where_conditions.append("JSON_EXTRACT(sd.api_input, '$.inputs.houses_id') = :house_id")
        params['house_id'] = house_id
    
    where_clause = " AND ".join(where_conditions)
    
    # 查询数据
    sql = text(f"""
        SELECT sd.*
        FROM session_detail sd
        JOIN session s ON s.id = sd.session_id
        WHERE {where_clause}
        ORDER BY sd.create_time DESC
        LIMIT :pagesize OFFSET :offset
    """)
    
    result = session.execute(sql, params).fetchall()
    
    # 转换结果为字典列表
    session_details = []
    for row in result:
        session_detail = {
            "id": row[0],
            "session_id": row[1],
            "api_input": row[2],
            "user_question": row[3],
            "ai_response": row[4],
            "final_response": row[5],
            "dialog_carrier": row[6],
            "create_time": row[7],
            "update_time": row[8]
        }
        session_details.append(session_detail)
    
    # 查询总数
    count_sql = text(f"""
        SELECT COUNT(*)
        FROM session_detail sd
        JOIN session s ON s.id = sd.session_id
        WHERE {where_clause}
    """)
    
    count_result = session.execute(count_sql, {k: v for k, v in params.items() if k not in ['pagesize', 'offset']}).fetchone()
    total_count = count_result[0] if count_result else 0
    
    return {
        "data": session_details,
        "total": total_count,
        "page": page,
        "pagesize": pagesize
    }