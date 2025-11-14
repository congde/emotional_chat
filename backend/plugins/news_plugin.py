"""
新闻推送插件 - 提供最新新闻资讯推送功能
"""
import os
import requests
import re
from typing import Dict, Any, List
from .base_plugin import BasePlugin
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# 尝试导入feedparser用于RSS解析
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    logger.warning("feedparser未安装，RSS功能将不可用。可以使用 pip install feedparser 安装")


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
            "science"       # 科学
        ]
        
        # RSS源配置（免费，无需API key）
        # 使用中文新闻RSS源
        self.rss_feeds = {
            "technology": [
                "https://www.ithome.com/rss/",  # IT之家
                "https://www.techcrunch.com/feed/",  # TechCrunch
                "https://rsshub.app/36kr/newsflashes",  # 36氪快讯（需要RSSHub）
            ],
            "general": [
                "https://www.ithome.com/rss/",  # IT之家（综合科技）
                "https://rsshub.app/36kr/newsflashes",  # 36氪
            ],
            "science": [
                "https://www.ithome.com/rss/",  # IT之家（科技相关）
                "https://rsshub.app/36kr/newsflashes",
            ],
            "health": [
                "https://www.ithome.com/rss/",  # 通用源
            ],
            "entertainment": [
                "https://www.ithome.com/rss/",  # 通用源
            ]
        }
        
        # 如果RSSHub不可用，使用备用RSS源
        self.fallback_rss_feeds = {
            "technology": [
                "https://www.ithome.com/rss/",
                "https://techcrunch.com/feed/",
            ],
            "general": [
                "https://www.ithome.com/rss/",
            ],
            "science": [
                "https://www.ithome.com/rss/",
            ],
            "health": [
                "https://www.ithome.com/rss/",
            ],
            "entertainment": [
                "https://www.ithome.com/rss/",
            ]
        }
        
        # 免费新闻API（GNews - 有免费额度）
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.gnews_base_url = "https://gnews.io/api/v4"
    
    @property
    def function_schema(self) -> Dict[str, Any]:
        """返回 Function Calling 的 JSON Schema"""
        return {
            "name": "get_latest_news",
            "description": "获取最新新闻资讯",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["general", "technology", "health", "entertainment", "science"]
                    },
                    "count": {
                        "type": "integer",
                        "default": 3
                    }
                }
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
            # 优先尝试使用GNews API（免费额度）
            if self.gnews_api_key:
                result = self._query_gnews_api(category, count)
                if result and "error" not in result:
                    return result
            
            # 尝试使用NewsAPI
            if self.api_key:
                result = self._query_news_api(category, count)
                if result and "error" not in result:
                    return result
            
            # 尝试使用RSS源（免费，无需API key）
            if FEEDPARSER_AVAILABLE:
                result = self._query_rss_feeds(category, count)
                if result and "error" not in result:
                    return result
            
            # 如果都失败，返回模拟数据
            logger.warning("所有新闻源都不可用，返回模拟数据")
            return self._get_mock_news(category, count)
        
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
            return {"error": f"News API请求失败: {str(e)}"}
    
    def _query_gnews_api(self, category: str, count: int) -> Dict[str, Any]:
        """使用GNews API查询新闻（免费额度）"""
        try:
            # GNews的类别映射
            category_map = {
                "technology": "technology",
                "health": "health",
                "entertainment": "entertainment",
                "science": "science",
                "general": "general"
            }
            
            gnews_category = category_map.get(category, "general")
            
            params = {
                'token': self.gnews_api_key,
                'lang': 'zh',
                'country': 'cn',
                'topic': gnews_category,
                'max': min(count, 10)
            }
            
            url = f"{self.gnews_base_url}/top-headlines"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"GNews API错误: {response.status_code}")
                return {"error": f"GNews API错误: {response.status_code}"}
            
            data = response.json()
            
            articles = []
            for item in data.get("articles", [])[:count]:
                articles.append({
                    "title": item.get("title", "无标题"),
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "source": item.get("source", {}).get("name", "GNews")
                })
            
            return {
                "category": category,
                "count": len(articles),
                "articles": articles,
                "source": "GNews API"
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"GNews API请求异常: {e}")
            return {"error": f"GNews API请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"GNews API解析异常: {e}")
            return {"error": f"GNews API解析失败: {str(e)}"}
    
    def _query_rss_feeds(self, category: str, count: int) -> Dict[str, Any]:
        """使用RSS源查询新闻（免费，无需API key）"""
        if not FEEDPARSER_AVAILABLE:
            return {"error": "feedparser未安装，无法使用RSS功能"}
        
        try:
            # 优先使用主要RSS源，如果失败则使用备用源
            feeds = self.rss_feeds.get(category, self.rss_feeds.get("general", []))
            if not feeds:
                feeds = self.fallback_rss_feeds.get(category, self.fallback_rss_feeds.get("general", []))
            
            if not feeds:
                return {"error": f"没有找到类别 {category} 的RSS源"}
            
            all_articles = []
            
            # 从多个RSS源获取新闻
            for feed_url in feeds:
                try:
                    # 设置超时和User-Agent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    feed = feedparser.parse(feed_url)
                    
                    if feed.bozo and feed.bozo_exception:
                        logger.warning(f"RSS解析警告: {feed_url} - {feed.bozo_exception}")
                        # 继续尝试其他源
                        continue
                    
                    # 如果没有条目，跳过
                    if not feed.entries:
                        logger.warning(f"RSS源没有条目: {feed_url}")
                        continue
                    
                    for entry in feed.entries:
                        # 根据类别过滤（简单关键词匹配）
                        title = entry.get("title", "")
                        summary = entry.get("summary", entry.get("description", ""))
                        
                        # 对于科技类别，如果RSS源本身就是科技类，则直接使用
                        # 简单的类别匹配
                        if category == "general" or self._matches_category(title + " " + summary, category):
                            # 清理HTML标签
                            description = summary[:200] if summary else ""
                            if description:
                                # 简单清理HTML标签
                                description = re.sub(r'<[^>]+>', '', description)
                            
                            all_articles.append({
                                "title": title,
                                "description": description,
                                "url": entry.get("link", ""),
                                "published_at": entry.get("published", entry.get("updated", "")),
                                "source": feed.feed.get("title", "RSS Feed")
                            })
                            
                            if len(all_articles) >= count:
                                break
                    
                    if len(all_articles) >= count:
                        break
                        
                except Exception as e:
                    logger.warning(f"解析RSS源失败 {feed_url}: {e}")
                    continue
            
            if not all_articles:
                return {"error": "未能从RSS源获取新闻"}
            
            return {
                "category": category,
                "count": len(all_articles),
                "articles": all_articles[:count],
                "source": "RSS Feeds"
            }
        
        except Exception as e:
            logger.error(f"RSS查询异常: {e}")
            return {"error": f"RSS查询失败: {str(e)}"}
    
    def _matches_category(self, text: str, category: str) -> bool:
        """简单判断文本是否匹配类别"""
        text_lower = text.lower()
        
        category_keywords = {
            "technology": ["tech", "ai", "artificial intelligence", "technology", "tech", "software", "hardware", "computer", "digital", "科技", "技术", "人工智能", "AI"],
            "health": ["health", "medical", "medicine", "wellness", "healthcare", "健康", "医疗", "医学", "保健"],
            "entertainment": ["entertainment", "movie", "music", "celebrity", "show", "娱乐", "电影", "音乐", "明星"],
            "science": ["science", "research", "study", "discovery", "scientific", "科学", "研究", "发现"],
            "general": []  # 综合类别匹配所有
        }
        
        if category == "general":
            return True
        
        keywords = category_keywords.get(category, [])
        return any(keyword in text_lower for keyword in keywords)
    
    def _get_mock_news(self, category: str, count: int) -> Dict[str, Any]:
        """返回模拟新闻数据（当API不可用时）"""
        mock_news = {
            "general": [
                {"title": "科技发展趋势分析", "description": "探讨当前科技发展的最新趋势和未来展望", "source": "科技日报"},
                {"title": "全球气候变化应对措施", "description": "各国政府出台新政策应对气候变化挑战", "source": "环球时报"},
                {"title": "心理健康意识提升", "description": "社会对心理健康问题关注度显著提高", "source": "健康时报"},
                {"title": "科技创新推动经济发展", "description": "新技术应用为经济增长注入新动力", "source": "经济观察"},
                {"title": "社会关注度持续升温", "description": "多个热点话题引发广泛讨论", "source": "新闻周刊"}
            ],
            "technology": [
                {"title": "AI技术新突破", "description": "人工智能领域取得重大进展，大模型能力持续提升", "source": "科技快讯"},
                {"title": "5G网络全面覆盖", "description": "5G技术在更多城市实现商用，网络速度大幅提升", "source": "通信世界"},
                {"title": "区块链应用拓展", "description": "区块链技术在多个行业落地应用，提升数据安全性", "source": "数字经济"},
                {"title": "量子计算新进展", "description": "量子计算机在特定领域展现强大计算能力", "source": "前沿科技"},
                {"title": "新能源汽车技术突破", "description": "电池技术和充电效率实现重大提升", "source": "汽车科技"}
            ],
            "health": [
                {"title": "心理健康科普", "description": "普及心理健康知识，提高公众认知和重视程度", "source": "健康生活"},
                {"title": "运动与健康研究", "description": "最新研究揭示运动对心理健康的显著益处", "source": "健康科学"},
                {"title": "营养均衡建议", "description": "专家建议如何通过饮食改善情绪和提升幸福感", "source": "营养健康"},
                {"title": "睡眠质量改善方法", "description": "研究显示规律作息对身心健康的重要影响", "source": "健康指南"},
                {"title": "慢性病预防新发现", "description": "早期干预措施可有效降低慢性病发病率", "source": "医学前沿"}
            ],
            "entertainment": [
                {"title": "影剧新作推荐", "description": "近期热播影视作品盘点，多部作品引发观众热议", "source": "娱乐周刊"},
                {"title": "音乐治愈力量", "description": "研究显示音乐对情绪的正面影响，音乐疗法受关注", "source": "音乐之声"},
                {"title": "文化艺术活动", "description": "各地文化活动精彩纷呈，丰富市民精神生活", "source": "文化报道"},
                {"title": "明星动态更新", "description": "多位艺人发布新作品，粉丝期待值高涨", "source": "娱乐新闻"},
                {"title": "综艺节目创新", "description": "新形式综艺节目获得观众好评，收视率创新高", "source": "电视周刊"}
            ],
            "science": [
                {"title": "太空探索新发现", "description": "最新太空任务揭示宇宙奥秘，拓展人类认知边界", "source": "科学探索"},
                {"title": "生物医学突破", "description": "基因编辑技术在疾病治疗领域取得重要进展", "source": "医学研究"},
                {"title": "气候变化研究", "description": "科学家发现新的气候模式，为应对策略提供依据", "source": "环境科学"},
                {"title": "新材料研发成功", "description": "新型材料在多个领域展现巨大应用潜力", "source": "材料科学"},
                {"title": "海洋生物新发现", "description": "深海探索发现多种未知生物，丰富生物多样性认知", "source": "海洋科学"}
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
