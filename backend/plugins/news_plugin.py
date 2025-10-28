"""
新闻推送插件 - 提供最新新闻资讯推送功能
"""
import os
import requests
from typing import Dict, Any, List
from .base_plugin import BasePlugin
import logging

logger = logging.getLogger(__name__)


class NewsPlugin(BasePlugin):
    """新闻推送插件 - 使用NewsAPI"""
    
    def __init__(self, api_key: str = None):
        # 如果没有提供API key，尝试从环境变量获取
        api_key = api_key or os.getenv("NEWS_API_KEY") or os.getenv("NEWS_API_TOKEN")
        
        super().__init__(
            name="get_latest_news",
            description="获取最新新闻，可按类别（科技、健康、娱乐、科学等）筛选",
            api_key=api_key
        )
        
        # 使用免费的新闻API服务
        # 备选方案：NewsAPI、天行API、聚合数据等
        self.base_url = "https://newsapi.org/v2/top-headlines"
        
        # 支持的新闻类别
        self.supported_categories = [
            "general",      # 综合
            "technology",   # 科技
            "health",       # 健康
            "entertainment", # 娱乐
            "science",      # 科学
            "sports",       # 体育
            "business"      # 商业
        ]
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        """返回 Function Calling 的 JSON Schema"""
        return {
            "name": "get_latest_news",
            "description": "获取最新新闻资讯，可根据用户兴趣推送科技、健康、娱乐等不同类别的新闻。帮助用户了解时事动态。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["general", "technology", "health", "entertainment", "science", "sports", "business"],
                        "description": "新闻类别：general(综合)、technology(科技)、health(健康)、entertainment(娱乐)、science(科学)、sports(体育)、business(商业)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "返回的新闻数量，默认3条",
                        "default": 3
                    }
                },
                "required": []
            }
        }
    
    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        category = kwargs.get("category", "general")
        if category and category not in self.supported_categories:
            logger.warning(f"不支持的新闻类别: {category}")
            return False
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行新闻查询"""
        if not self.enabled:
            return {"error": "插件已禁用"}
        
        category = kwargs.get("category", "general")
        count = kwargs.get("count", 3)
        
        if not self.validate_params(**kwargs):
            return {"error": "参数验证失败"}
        
        try:
            # 如果没有配置API key，返回模拟数据
            if not self.api_key:
                logger.warning("News API key未配置，返回模拟数据")
                return self._get_mock_news(category, count)
            
            return self._query_news_api(category, count)
        
        except Exception as e:
            logger.error(f"新闻查询失败: {e}")
            return {"error": f"查询失败: {str(e)}"}
    
    def _query_news_api(self, category: str, count: int) -> Dict[str, Any]:
        """调用 NewsAPI 查询新闻"""
        try:
            params = {
                'category': category,
                'language': 'zh',
                'pageSize': min(count, 10),  # 限制最多10条
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"News API错误: {response.status_code}")
                return self._get_mock_news(category, count)
            
            data = response.json()
            
            articles = []
            for item in data.get("articles", [])[:count]:
                articles.append({
                    "title": item.get("title", "无标题"),
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "source": item.get("source", {}).get("name", "")
                })
            
            return {
                "category": category,
                "count": len(articles),
                "articles": articles
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"News API请求异常: {e}")
            return self._get_mock_news(category, count)
    
    def _get_mock_news(self, category: str, count: int) -> Dict[str, Any]:
        """返回模拟新闻数据（当API不可用时）"""
        mock_news = {
            "general": [
                {"title": "科技发展趋势分析", "description": "探讨当前科技发展的最新趋势和未来展望", "source": "科技日报"},
                {"title": "全球气候变化应对措施", "description": "各国政府出台新政策应对气候变化挑战", "source": "环球时报"},
                {"title": "心理健康意识提升", "description": "社会对心理健康问题关注度显著提高", "source": "健康时报"}
            ],
            "technology": [
                {"title": "AI技术新突破", "description": "人工智能领域取得重大进展", "source": "科技快讯"},
                {"title": "5G网络全面覆盖", "description": "5G技术在更多城市实现商用", "source": "通信世界"},
                {"title": "区块链应用拓展", "description": "区块链技术在多个行业落地应用", "source": "数字经济"}
            ],
            "health": [
                {"title": "心理健康科普", "description": "普及心理健康知识，提高公众认知", "source": "健康生活"},
                {"title": "运动与健康研究", "description": "最新研究揭示运动对心理健康的益处", "source": "健康科学"},
                {"title": "营养均衡建议", "description": "专家建议如何通过饮食改善情绪", "source": "营养健康"}
            ],
            "entertainment": [
                {"title": "影剧新作推荐", "description": "近期热播影视作品盘点", "source": "娱乐周刊"},
                {"title": "音乐治愈力量", "description": "研究显示音乐对情绪的正面影响", "source": "音乐之声"},
                {"title": "文化艺术活动", "description": "各地文化活动精彩纷呈", "source": "文化报道"}
            ]
        }
        
        category_news = mock_news.get(category, mock_news["general"])
        
        articles = []
        for i, news in enumerate(category_news[:count]):
            articles.append({
                "title": news["title"],
                "description": news["description"],
                "source": news.get("source", "新闻来源"),
                "url": f"https://example.com/news/{category}/{i+1}",
                "published_at": "2024-01-01T00:00:00Z"
            })
        
        return {
            "category": category,
            "count": len(articles),
            "articles": articles,
            "note": "当前返回模拟数据，请配置 NewsAPI 密钥以获取真实新闻"
        }
