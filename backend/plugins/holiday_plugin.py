"""
节假日查询插件 - 提供节假日信息查询功能
"""
import os
import requests
import time
from datetime import datetime, date
from typing import Dict, Any, Optional
from .base_plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)


class HolidayPlugin(BasePlugin):
    """节假日查询插件 - 支持查询节假日、工作日、调休等信息"""
    
    def __init__(self, api_key: str = None):
        # 优先使用配置的API密钥（如果有）
        api_key = api_key or os.getenv("HOLIDAY_API_KEY") or os.getenv("JIEJIARI_API_KEY")
        
        # 默认使用免费的节假日API（政府平台数据）
        self.use_paid_api = bool(api_key)
        self.api_key = api_key
        
        # 免费API端点列表（按优先级排序）
        # 1. 起零数据 - 中国法定节假日（2014-2026）
        self.free_api_base = "https://api.istero.com/holiday"
        # 2. jiejiariapi - 节假日查询
        self.alt_api_base = "https://jiejiariapi.com/v1"
        # 3. 备用API
        self.backup_api_base = "https://timor.tech/api/holiday/info"
        
        # 如果配置了API key，可以使用其他付费API
        self.paid_api_base = None
        
        if not self.use_paid_api:
            logger.info("未配置节假日API密钥，将使用免费的节假日API（政府平台数据）")
        
        super().__init__(
            name="get_holiday_info",
            description="查询指定日期的节假日信息，包括是否为节假日、工作日、调休等信息，帮助用户规划出行。数据来源于政府平台，无需调用大模型。",
            api_key=api_key
        )
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        """返回 Function Calling 的 JSON Schema"""
        return {
            "name": "get_holiday_info",
            "description": "查询指定日期的节假日信息。当用户提到出游、旅行、假期安排时，可以查询日期是否为节假日、工作日或调休，帮助用户规划行程。",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，格式：YYYY-MM-DD 或 YYYYMMDD，例如：2024-10-01 或 20241001。如果不提供，默认查询今天"
                    },
                    "year": {
                        "type": "string",
                        "description": "年份，格式：YYYY，例如：2024。用于查询整年的节假日信息"
                    }
                },
                "required": []
            }
        }
    
    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        date_str = kwargs.get("date")
        year = kwargs.get("year")
        
        # 至少需要提供date或year之一
        if not date_str and not year:
            # 如果没有提供参数，默认查询今天，这是允许的
            return True
        
        # 验证日期格式
        if date_str:
            try:
                # 尝试解析日期
                if len(date_str) == 8:  # YYYYMMDD
                    datetime.strptime(date_str, "%Y%m%d")
                elif len(date_str) == 10:  # YYYY-MM-DD
                    datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    logger.warning(f"无效的日期格式: {date_str}")
                    return False
            except ValueError:
                logger.warning(f"无效的日期: {date_str}")
                return False
        
        # 验证年份格式
        if year:
            try:
                year_int = int(year)
                if year_int < 2000 or year_int > 2100:
                    logger.warning(f"年份超出范围: {year}")
                    return False
            except ValueError:
                logger.warning(f"无效的年份: {year}")
                return False
        
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行节假日查询"""
        if not self.enabled:
            return {"error": "插件已禁用"}
        
        if not self.validate_params(**kwargs):
            return {"error": "参数验证失败"}
        
        try:
            date_str = kwargs.get("date")
            year = kwargs.get("year")
            
            # 如果没有提供日期，默认查询今天
            if not date_str and not year:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            if date_str:
                return self._query_date(date_str)
            elif year:
                return self._query_year(year)
            else:
                return {"error": "需要提供date或year参数"}
        
        except Exception as e:
            logger.error(f"节假日查询失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    def _query_date(self, date_str: str) -> Dict[str, Any]:
        """查询指定日期的节假日信息（直接调用政府平台API，无需大模型）"""
        # 重试配置
        max_retries = 3
        timeout = 20
        retry_delay = 2
        
        # 标准化日期格式
        if len(date_str) == 8:  # YYYYMMDD
            date_obj = datetime.strptime(date_str, "%Y%m%d").date()
            date_formatted = date_obj.strftime("%Y-%m-%d")
            date_compact = date_str
        elif len(date_str) == 10:  # YYYY-MM-DD
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_formatted = date_str
            date_compact = date_str.replace("-", "")
        else:
            return {"error": f"无效的日期格式: {date_str}"}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; HolidayBot/1.0)",
            "Accept": "application/json"
        }
        
        # API端点列表（按优先级尝试）
        api_endpoints = [
            # 1. 起零数据 - 中国法定节假日（政府数据）
            {
                "url": f"{self.free_api_base}",
                "params": {"date": date_compact},
                "method": "get",
                "parser": "istero"
            },
            # 2. mxnzp - 备用API
            {
                "url": f"{self.alt_api_base}",
                "params": {"date": date_compact},
                "method": "get",
                "parser": "mxnzp"
            }
        ]
        
        last_exception = None
        for attempt in range(max_retries):
            # 尝试每个API端点
            for api_config in api_endpoints:
                try:
                    logger.debug(f"节假日API请求 (尝试 {attempt + 1}/{max_retries}, API: {api_config['url']}): {date_formatted}")
                    
                    if api_config["method"] == "get":
                        if api_config["params"]:
                            response = requests.get(api_config["url"], params=api_config["params"], headers=headers, timeout=timeout)
                        else:
                            response = requests.get(api_config["url"], headers=headers, timeout=timeout)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # 解析不同API的响应格式
                            parser_type = api_config.get("parser", "default")
                            result = self._parse_holiday_response(data, date_obj, date_formatted, parser_type)
                            if result and "error" not in result:
                                logger.debug(f"节假日API查询成功: {date_formatted} (API: {api_config['url']})")
                                return result
                            else:
                                # 解析失败，尝试下一个API
                                continue
                        except ValueError as e:
                            # JSON解析失败
                            logger.debug(f"API响应不是有效JSON: {e}")
                            continue
                    else:
                        logger.debug(f"API {api_config['url']} 返回状态码: {response.status_code}")
                        continue  # 尝试下一个API
                        
                except requests.exceptions.Timeout as e:
                    logger.debug(f"API {api_config['url']} 请求超时: {e}")
                    continue  # 尝试下一个API
                    
                except requests.exceptions.ConnectionError as e:
                    logger.debug(f"API {api_config['url']} 连接错误: {e}")
                    continue  # 尝试下一个API
                    
                except requests.exceptions.RequestException as e:
                    logger.debug(f"API {api_config['url']} 请求异常: {e}")
                    continue  # 尝试下一个API
                    
                except Exception as e:
                    logger.debug(f"API {api_config['url']} 解析异常: {e}")
                    continue  # 尝试下一个API
            
            # 所有API都失败，等待后重试
            if attempt < max_retries - 1:
                logger.warning(f"所有节假日API都失败，等待后重试 (尝试 {attempt + 1}/{max_retries})")
                time.sleep(retry_delay * (attempt + 1))
        
        # 所有重试都失败，使用本地判断作为fallback
        logger.warning(f"所有节假日API都不可用，使用本地fallback判断: {date_formatted}")
        return self._fallback_holiday_check(date_obj, date_formatted)
    
    def _query_year(self, year: str) -> Dict[str, Any]:
        """查询整年的节假日信息"""
        try:
            year_int = int(year)
            # 查询该年的主要节假日
            holidays = []
            
            # 主要节假日（固定日期）
            fixed_holidays = [
                (1, 1, "元旦"),
                (5, 1, "劳动节"),
                (10, 1, "国庆节"),
            ]
            
            for month, day, name in fixed_holidays:
                try:
                    holiday_date = date(year_int, month, day)
                    holidays.append({
                        "date": holiday_date.strftime("%Y-%m-%d"),
                        "name": name,
                        "type": "法定节假日"
                    })
                except ValueError:
                    pass
            
            return {
                "year": year,
                "holidays": holidays,
                "total": len(holidays),
                "note": "仅包含固定日期节假日，动态节假日（如春节、清明）需要查询具体日期"
            }
        except Exception as e:
            logger.error(f"查询年份节假日失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    def _parse_holiday_response(self, data: Dict, date_obj: date, date_str: str, parser_type: str = "default") -> Dict[str, Any]:
        """解析不同API的响应格式"""
        # 解析起零数据API格式
        if parser_type == "istero" or ("code" in data and data.get("code") == 0):
            holiday_data = data.get("data", {})
            return {
                "date": date_str,
                "is_holiday": holiday_data.get("isHoliday", False) or holiday_data.get("is_holiday", False),
                "holiday_name": holiday_data.get("holidayName", "") or holiday_data.get("holiday_name", ""),
                "is_workday": holiday_data.get("isWorkday", False) or holiday_data.get("is_workday", False),
                "is_weekend": date_obj.weekday() >= 5,
                "weekday": date_obj.strftime("%A"),
                "note": "使用起零数据API（政府数据）"
            }
        
        # 解析mxnzp格式
        if parser_type == "mxnzp" or ("code" in data and data.get("code") == 1):
            holiday_data = data.get("data", {})
            return {
                "date": date_str,
                "is_holiday": holiday_data.get("type", 0) == 1,  # type: 0=工作日, 1=节假日, 2=周末
                "holiday_name": holiday_data.get("name", "") or holiday_data.get("holidayName", ""),
                "is_workday": holiday_data.get("type", 0) == 0,
                "is_weekend": holiday_data.get("type", 0) == 2 or date_obj.weekday() >= 5,
                "weekday": date_obj.strftime("%A"),
                "note": "使用mxnzp API"
            }
        
        # 通用格式解析
        is_holiday = data.get("isHoliday", False) or data.get("is_holiday", False) or data.get("holiday", False)
        holiday_name = data.get("holidayName", "") or data.get("holiday_name", "") or data.get("name", "")
        is_workday = data.get("isWorkday", False) or data.get("is_workday", False) or data.get("workday", False)
        
        return {
            "date": date_str,
            "is_holiday": is_holiday,
            "holiday_name": holiday_name,
            "is_workday": is_workday,
            "is_weekend": date_obj.weekday() >= 5,
            "weekday": date_obj.strftime("%A"),
            "raw_data": data,
            "note": "使用通用解析"
        }
    
    def _fallback_holiday_check(self, date_obj: date, date_str: str) -> Dict[str, Any]:
        """当API不可用时的本地fallback判断（基于政府发布的节假日数据）"""
        # 简单的本地判断：周末
        is_weekend = date_obj.weekday() >= 5
        
        # 主要固定节假日（基于中国政府发布的法定节假日）
        # 注意：这里只包含固定日期的节假日，动态节假日（如春节、清明）需要查询具体年份
        fixed_holidays = {
            (1, 1): "元旦",
            (5, 1): "劳动节",
            (10, 1): "国庆节",
        }
        
        month_day = (date_obj.month, date_obj.day)
        holiday_name = fixed_holidays.get(month_day, "")
        is_holiday = bool(holiday_name)
        
        # 如果是周末，也标记为节假日（非工作日）
        if is_weekend and not is_holiday:
            holiday_name = "周末"
        
        return {
            "date": date_str,
            "is_holiday": is_holiday or is_weekend,
            "holiday_name": holiday_name if holiday_name else ("周末" if is_weekend else ""),
            "is_workday": not is_holiday and not is_weekend,
            "is_weekend": is_weekend,
            "weekday": date_obj.strftime("%A"),
            "note": "API不可用，使用本地判断（仅支持固定节假日和周末判断，动态节假日需查询API）"
        }

