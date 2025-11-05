import copy
import logging
from string import Template
from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.dao.apiInfoDao import get_info_by_api_code
from src.exception.aiException import AIException
from src.myHttp.utils.myHttpUtils import normal_post, post_with_query_params, form_data_post
from sqlmodel import Session

from src.pojo.bo.aiBo import NormalLLMRequestModel, ModelConfig
from src.service.aiCodeService import get_code_value_by_code
from src.utils.dataUtils import translate_dict_keys_4_list, translate_dict_keys_4_dict

logger = logging.getLogger(__name__)

async def erp_execute_sql(sql, session: Session):
    """
    执行SQL
    :param sql:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_EXEC_SQL_API_CODE.value)
    if isinstance(sql,str):
        sql = {"sql": sql}
    else:
        sql = sql.model_dump()
    response = await normal_post(api_info.api_url, data=sql, headers={})
    return response['data']

async def erp_generate_popi(data: dict, session: Session):
    """
    生成POPI
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_GEN_POPI_API_CODE.value)
    response = await post_with_query_params(api_info.api_url, params=data, headers=data)
    erp_response_check(response)
    return response['data']

async def erp_generate_pi(data: dict, session: Session):
    """
    生成PI
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_GEN_PI_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers=data)
    erp_response_check(response)
    if "msg" in response and response['msg'] != "success":
        return response['msg']
    return response['data']


async def erp_order_search(data: dict, session: Session):
    """
    订单查询
    :param data:
    :param session:
    :return:
    """
    response = await erp_order_search_without_check(data, session)
    erp_response_check(response)
    return get_data_from_erp_page_response(response)

async def erp_order_search_without_check(data: dict, session: Session):
    """
    订单查询 不带校验
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_ORDER_SEARCH_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    return response

async def erp_user_sale_info(data: dict, session: Session):
    """
    销售情况查询
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_USER_SALE_INFO_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    erp_response_check(response)
    # lcl 结果返回结果调整
    return response['data']
    # if isinstance(response['data'],list):
    #     return response['data']
    # return list(response['data'].values())

async def erp_detect_order_type(data: dict, session: Session):
    """
    订单类型分析
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.DETECT_ORDER_TYPE_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    erp_response_check(response)
    # lcl 结果返回结果调整
    return response['data']

async def erp_inventory_detail_search(data: dict, session: Session):
    """
    库存详情查询
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    erp_response_check(response)
    return response['data']

async def erp_inventory_detail_search_by_cn(data: dict, session: Session):
    """
    库存详情查询，翻译为中文字段
    :param data:
    :param session:
    :return:
    """
    response = await erp_inventory_detail_search(data, session)
    r1 = copy.deepcopy(response['stockDetails'])
    del response['stockDetails']
    result1 = translate_dict_keys_4_dict(response, get_code_value_by_code(session,
                                                                          CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value + "_1"))
    result2 = translate_dict_keys_4_list(r1, get_code_value_by_code(session,
                                                                    CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value + "_2"))
    result1['库存明细'] = result2
    return result1




def get_data_from_erp_page_response(response):
    """
    从erp的分页查询结果中只取数据
    :param response:  erp分页查询结果
    :return:  纯净数据
    """
    return response['data']['list']

def erp_response_check(response):
    """
    erp接口返回结果检查, code 为 0 1 时是正常的
    :param response: erp接口返回结果
    :return: 无
    """
    if response['code'] not in [1,0] :
        raise AIException.quick_raise(f"ERP接口异常:{response['msg']}")

def get_inventory_analysis_prompt(data,prompt_text:str) -> list[dict]:
    prompt_template = Template(prompt_text)
    prompt = prompt_template.substitute(data=data)
    messages = [PromptContent.as_system(prompt),
                PromptContent.as_user("基于我提供的数据,帮我进行库存分析. 以下是我提供的数据:\n" + str(data))]
    return messages

async def inventory_analysis(data,prompt_text:str,model: str,stream: bool = True) -> str:
    """
    库存详情分析，根据库存详情数据进行库存分析
    :param stream: 流式输出？
    :param data: 库存详情数据
    :param prompt_text: 提示词
    :param model: 调用模型
    :return: 分析结果
    """
    messages = get_inventory_analysis_prompt(data,prompt_text)

    result = await do_api_2_llm(ModelConfig(model=model, messages=messages, stream=stream))
    return result

async def erp_seller_sale_info_analysis(llm_params: NormalLLMRequestModel,sale_data: str, session: Session):
    """
    销售人员销售情况分析
    :param llm_params: LLM的擦拭农户
    :param sale_data:销售数据
    :param session:
    :return:
    """
    prompt_text = get_code_value_by_code(session=session, code_value=CodeEnum.ERP_SELLER_WORK_ANALYSIS_PROMPT_CODE.value)
    llm_params.messages = [PromptContent.as_system(prompt_text),
                                            PromptContent.as_user(llm_params.query),
                                            PromptContent.as_assistant(sale_data)]
    return await do_api_2_llm(llm_params)

async def get_user_house_combinations(dialog_carrier: str, page: int, pagesize: int, session: Session):
    """
    获取所有用户和房源的组合信息（带分页信息）
    
    Args:
        dialog_carrier: 对话承载人
        page: 页码（从1开始）
        pagesize: 每页条数
        session: 数据库会话
        
    Returns:
        包含分页信息的用户和房源组合数据
    """
    from src.dao.sessionDetailDao import get_user_house_combinations, get_user_house_combinations_count
    
    try:
        # 获取数据
        data = get_user_house_combinations(session, dialog_carrier, page, pagesize)
        
        # 获取总数
        total_count = get_user_house_combinations_count(session, dialog_carrier)
        
        # 返回包含分页信息的结果
        return {
            "data": data,
            "total": total_count,
            "page": page,
            "pagesize": pagesize
        }
    except Exception as e:
        logger.error(f"获取用户房源组合信息失败: {str(e)}")
        raise AIException(500, f"获取用户房源组合信息失败: {str(e)}")

async def get_user_house_combinations_with_pagination(dialog_carrier: str, page: int, pagesize: int, session: Session):
    """
    获取所有用户和房源的组合信息（带分页信息）
    
    Args:
        dialog_carrier: 对话承载人
        page: 页码（从1开始）
        pagesize: 每页条数
        session: 数据库会话
        
    Returns:
        包含分页信息的用户和房源组合数据
    """
    from src.dao.sessionDetailDao import get_user_house_combinations, get_user_house_combinations_count
    
    try:
        # 获取数据
        data = get_user_house_combinations(session, dialog_carrier, page, pagesize)
        
        # 获取总数
        total_count = get_user_house_combinations_count(session, dialog_carrier)
        
        # 计算分页信息
        total_pages = (total_count + pagesize - 1) // pagesize
        
        return {
            "data": data,
            "pagination": {
                "page": page,
                "pagesize": pagesize,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        logger.error(f"获取用户房源组合信息失败: {str(e)}")
        raise AIException(500, f"获取用户房源组合信息失败: {str(e)}")

async def get_order_history_with_pagination(user_id: str, dialog_carrier: str, house_id: str = None, page: int = 1, pagesize: int = 10, session: Session = None):
    """
    获取订单历史记录（带分页）
    
    Args:
        user_id: 用户ID
        dialog_carrier: 对话承载人
        house_id: 房源ID（可选）
        page: 页码（从1开始）
        pagesize: 每页条数
        session: 数据库会话
        
    Returns:
        包含分页信息的订单历史数据
    """
    from src.dao.sessionDetailDao import search_session_details_by_user_house_with_pagination
    
    try:
        result = search_session_details_by_user_house_with_pagination(
            session=session,
            user_id=user_id,
            dialog_carrier=dialog_carrier,
            house_id=house_id,
            page=page,
            pagesize=pagesize
        )
        return result
    except Exception as e:
        logger.error(f"获取订单历史记录失败: {str(e)}")
        raise AIException(500, f"获取订单历史记录失败: {str(e)}")