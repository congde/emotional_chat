#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户反馈分析工具
分析用户反馈，识别常见问题，生成改进建议
"""

import json
from typing import List, Dict, Any
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from backend.database import DatabaseManager


class FeedbackAnalyzer:
    """反馈分析器"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def analyze_all_feedback(self, days: int = 30) -> Dict[str, Any]:
        """
        分析所有反馈数据
        
        Args:
            days: 分析最近多少天的数据
            
        Returns:
            分析结果字典
        """
        # 获取所有反馈
        all_feedbacks = self.db_manager.get_all_feedback(limit=10000)
        
        # 过滤时间范围
        cutoff_date = datetime.now() - timedelta(days=days)
        feedbacks = [f for f in all_feedbacks if f.created_at >= cutoff_date]
        
        if not feedbacks:
            return {
                "status": "no_data",
                "message": "没有找到反馈数据"
            }
        
        # 基础统计
        total_count = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total_count if total_count > 0 else 0
        
        # 按类型统计
        type_counter = Counter(f.feedback_type for f in feedbacks)
        
        # 按评分分组
        rating_distribution = Counter(f.rating for f in feedbacks)
        
        # 识别问题严重程度
        problem_severity = {
            'critical': [],  # 严重问题（评分1-2）
            'moderate': [],  # 中等问题（评分3）
            'minor': []      # 轻微问题（评分4-5但有负面反馈）
        }
        
        for feedback in feedbacks:
            if feedback.rating <= 2:
                problem_severity['critical'].append(feedback)
            elif feedback.rating == 3:
                problem_severity['moderate'].append(feedback)
            elif feedback.rating >= 4 and feedback.feedback_type in ['irrelevant', 'lack_empathy', 'overstepping']:
                problem_severity['minor'].append(feedback)
        
        # 分析各类问题
        problem_analysis = {
            'irrelevant': self._analyze_irrelevant_issues(
                [f for f in feedbacks if f.feedback_type == 'irrelevant']
            ),
            'lack_empathy': self._analyze_empathy_issues(
                [f for f in feedbacks if f.feedback_type == 'lack_empathy']
            ),
            'overstepping': self._analyze_overstepping_issues(
                [f for f in feedbacks if f.feedback_type == 'overstepping']
            )
        }
        
        # 生成总体报告
        report = {
            "analysis_date": datetime.now().isoformat(),
            "days_analyzed": days,
            "total_feedbacks": total_count,
            "average_rating": round(avg_rating, 2),
            "feedback_by_type": dict(type_counter),
            "rating_distribution": dict(rating_distribution),
            "problem_severity": {
                "critical_count": len(problem_severity['critical']),
                "moderate_count": len(problem_severity['moderate']),
                "minor_count": len(problem_severity['minor'])
            },
            "problem_analysis": problem_analysis,
            "recommendations": self._generate_recommendations(problem_analysis, type_counter)
        }
        
        return report
    
    def _analyze_irrelevant_issues(self, feedbacks: List) -> Dict[str, Any]:
        """分析答非所问的问题"""
        if not feedbacks:
            return {"count": 0, "examples": [], "patterns": []}
        
        patterns = []
        examples = []
        
        for feedback in feedbacks[:10]:  # 取前10个示例
            examples.append({
                "user_message": feedback.user_message[:100] if feedback.user_message else "",
                "bot_response": feedback.bot_response[:100] if feedback.bot_response else "",
                "comment": feedback.comment[:100] if feedback.comment else "",
                "rating": feedback.rating
            })
        
        # 识别常见模式
        keywords_in_comments = []
        for f in feedbacks:
            if f.comment:
                keywords_in_comments.extend(self._extract_keywords(f.comment))
        
        keyword_counter = Counter(keywords_in_comments)
        patterns = [
            {"keyword": k, "frequency": v} 
            for k, v in keyword_counter.most_common(10)
        ]
        
        return {
            "count": len(feedbacks),
            "average_rating": round(sum(f.rating for f in feedbacks) / len(feedbacks), 2),
            "examples": examples,
            "patterns": patterns,
            "severity": "high" if len(feedbacks) > 10 else "medium" if len(feedbacks) > 5 else "low"
        }
    
    def _analyze_empathy_issues(self, feedbacks: List) -> Dict[str, Any]:
        """分析缺乏共情的问题"""
        if not feedbacks:
            return {"count": 0, "examples": [], "patterns": []}
        
        examples = []
        for feedback in feedbacks[:10]:
            examples.append({
                "user_message": feedback.user_message[:100] if feedback.user_message else "",
                "bot_response": feedback.bot_response[:100] if feedback.bot_response else "",
                "comment": feedback.comment[:100] if feedback.comment else "",
                "rating": feedback.rating
            })
        
        # 识别缺乏共情的模式
        empathy_keywords = ['冷漠', '机械', '没有感情', '不理解', '敷衍', '套话']
        pattern_matches = defaultdict(int)
        
        for f in feedbacks:
            if f.comment:
                for keyword in empathy_keywords:
                    if keyword in f.comment:
                        pattern_matches[keyword] += 1
        
        patterns = [
            {"keyword": k, "frequency": v} 
            for k, v in sorted(pattern_matches.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "count": len(feedbacks),
            "average_rating": round(sum(f.rating for f in feedbacks) / len(feedbacks), 2),
            "examples": examples,
            "patterns": patterns,
            "severity": "high" if len(feedbacks) > 10 else "medium" if len(feedbacks) > 5 else "low"
        }
    
    def _analyze_overstepping_issues(self, feedbacks: List) -> Dict[str, Any]:
        """分析越界提供建议的问题"""
        if not feedbacks:
            return {"count": 0, "examples": [], "patterns": []}
        
        examples = []
        for feedback in feedbacks[:10]:
            examples.append({
                "user_message": feedback.user_message[:100] if feedback.user_message else "",
                "bot_response": feedback.bot_response[:100] if feedback.bot_response else "",
                "comment": feedback.comment[:100] if feedback.comment else "",
                "rating": feedback.rating
            })
        
        # 识别越界建议的模式
        overstepping_keywords = ['应该', '必须', '建议你', '你应该', '最好', '直接建议', '命令', '指导']
        pattern_matches = defaultdict(int)
        
        for f in feedbacks:
            if f.bot_response:
                for keyword in overstepping_keywords:
                    if keyword in f.bot_response:
                        pattern_matches[keyword] += 1
        
        patterns = [
            {"keyword": k, "frequency": v} 
            for k, v in sorted(pattern_matches.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "count": len(feedbacks),
            "average_rating": round(sum(f.rating for f in feedbacks) / len(feedbacks), 2),
            "examples": examples,
            "patterns": patterns,
            "severity": "high" if len(feedbacks) > 10 else "medium" if len(feedbacks) > 5 else "low"
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取，可以后续优化为使用NLP工具
        common_words = ['的', '了', '是', '在', '有', '和', '我', '你', '他', '她', '它', '这', '那', '就', '不', '很', '太']
        words = [w for w in text.split() if len(w) > 1 and w not in common_words]
        return words[:5]  # 返回前5个关键词
    
    def _generate_recommendations(self, problem_analysis: Dict, type_counter: Counter) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 针对答非所问的建议
        if problem_analysis['irrelevant']['count'] > 5:
            severity = problem_analysis['irrelevant']['severity']
            recommendations.append({
                "issue": "答非所问",
                "severity": severity,
                "priority": "high" if severity == "high" else "medium",
                "recommendation": "增强上下文理解能力，确保回复与用户问题直接相关。建议在Prompt中增加'请直接回应用户的问题，避免答非所问'的指令。",
                "action_items": [
                    "检查对话历史的使用是否充分",
                    "增加更多相关性检查的示例",
                    "调整Prompt中的响应格式要求"
                ]
            })
        
        # 针对缺乏共情的建议
        if problem_analysis['lack_empathy']['count'] > 5:
            severity = problem_analysis['lack_empathy']['severity']
            recommendations.append({
                "issue": "缺乏共情",
                "severity": severity,
                "priority": "high",
                "recommendation": "强化情感识别和共情表达。在Prompt中增加更多情感共鸣的示例，要求先识别情绪，再表达理解。",
                "action_items": [
                    "在系统Prompt中强调共情的重要性",
                    "增加情感识别和回应的示例",
                    "使用更温暖、更人性化的语言",
                    "避免使用机械化的套话"
                ]
            })
        
        # 针对越界建议的建议
        if problem_analysis['overstepping']['count'] > 5:
            severity = problem_analysis['overstepping']['severity']
            recommendations.append({
                "issue": "越界提供建议",
                "severity": severity,
                "priority": "medium",
                "recommendation": "明确角色定位，避免提供专业建议。在Prompt中强调'只倾听和陪伴，不提供具体建议'的原则。",
                "action_items": [
                    "修改Prompt中的禁止行为清单",
                    "增加边界示例（什么可以说，什么不能说）",
                    "减少使用'应该'、'建议'等指导性词汇",
                    "当用户寻求建议时，引导其寻求专业帮助"
                ]
            })
        
        # 如果整体评分偏低
        total_feedbacks = sum(type_counter.values())
        negative_feedbacks = sum(count for ftype, count in type_counter.items() 
                                 if ftype in ['irrelevant', 'lack_empathy', 'overstepping'])
        
        if total_feedbacks > 0 and negative_feedbacks / total_feedbacks > 0.3:
            recommendations.append({
                "issue": "整体满意度较低",
                "severity": "high",
                "priority": "high",
                "recommendation": "需要进行全面的Prompt优化。考虑重新设计系统角色定位和行为准则。",
                "action_items": [
                    "收集更多用户期望的反馈",
                    "进行A/B测试对比不同Prompt的效果",
                    "邀请心理学专家审核Prompt设计",
                    "增加更多正面示例"
                ]
            })
        
        return recommendations
    
    def generate_detailed_report(self, output_file: str = None) -> str:
        """
        生成详细的分析报告
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            报告文本
        """
        analysis = self.analyze_all_feedback()
        
        report_lines = [
            "=" * 80,
            "用户反馈分析报告",
            "=" * 80,
            f"\n生成时间: {analysis.get('analysis_date', 'N/A')}",
            f"分析周期: 最近 {analysis.get('days_analyzed', 'N/A')} 天",
            f"\n总反馈数: {analysis.get('total_feedbacks', 0)}",
            f"平均评分: {analysis.get('average_rating', 0)}/5.0",
            "\n" + "=" * 80,
            "\n## 反馈类型分布",
            "-" * 80
        ]
        
        # 反馈类型分布
        feedback_by_type = analysis.get('feedback_by_type', {})
        for ftype, count in feedback_by_type.items():
            percentage = (count / analysis['total_feedbacks'] * 100) if analysis['total_feedbacks'] > 0 else 0
            report_lines.append(f"{ftype:20s}: {count:5d} ({percentage:5.1f}%)")
        
        # 评分分布
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 评分分布",
            "-" * 80
        ])
        rating_dist = analysis.get('rating_distribution', {})
        for rating in sorted(rating_dist.keys()):
            count = rating_dist[rating]
            percentage = (count / analysis['total_feedbacks'] * 100) if analysis['total_feedbacks'] > 0 else 0
            stars = "★" * rating + "☆" * (5 - rating)
            report_lines.append(f"{stars:20s}: {count:5d} ({percentage:5.1f}%)")
        
        # 问题严重程度
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 问题严重程度",
            "-" * 80
        ])
        problem_severity = analysis.get('problem_severity', {})
        report_lines.append(f"严重问题 (评分1-2):  {problem_severity.get('critical_count', 0)}")
        report_lines.append(f"中等问题 (评分3):    {problem_severity.get('moderate_count', 0)}")
        report_lines.append(f"轻微问题 (评分4-5):  {problem_severity.get('minor_count', 0)}")
        
        # 问题详细分析
        problem_analysis = analysis.get('problem_analysis', {})
        
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 答非所问问题分析",
            "-" * 80
        ])
        irrelevant = problem_analysis.get('irrelevant', {})
        report_lines.append(f"问题数量: {irrelevant.get('count', 0)}")
        report_lines.append(f"平均评分: {irrelevant.get('average_rating', 0)}")
        report_lines.append(f"严重程度: {irrelevant.get('severity', 'N/A')}")
        
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 缺乏共情问题分析",
            "-" * 80
        ])
        lack_empathy = problem_analysis.get('lack_empathy', {})
        report_lines.append(f"问题数量: {lack_empathy.get('count', 0)}")
        report_lines.append(f"平均评分: {lack_empathy.get('average_rating', 0)}")
        report_lines.append(f"严重程度: {lack_empathy.get('severity', 'N/A')}")
        
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 越界建议问题分析",
            "-" * 80
        ])
        overstepping = problem_analysis.get('overstepping', {})
        report_lines.append(f"问题数量: {overstepping.get('count', 0)}")
        report_lines.append(f"平均评分: {overstepping.get('average_rating', 0)}")
        report_lines.append(f"严重程度: {overstepping.get('severity', 'N/A')}")
        
        # 改进建议
        report_lines.extend([
            "\n" + "=" * 80,
            "\n## 改进建议",
            "=" * 80
        ])
        
        recommendations = analysis.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report_lines.extend([
                f"\n### 建议 {i}: {rec.get('issue', 'N/A')}",
                f"严重程度: {rec.get('severity', 'N/A')}",
                f"优先级: {rec.get('priority', 'N/A')}",
                f"\n建议内容:",
                rec.get('recommendation', 'N/A'),
                f"\n行动项:"
            ])
            for action in rec.get('action_items', []):
                report_lines.append(f"  - {action}")
        
        report_lines.append("\n" + "=" * 80)
        report_lines.append("报告结束")
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)
        
        # 如果指定了输出文件，保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def export_feedback_data(self, output_file: str):
        """
        导出反馈数据为JSON格式
        
        Args:
            output_file: 输出文件路径
        """
        analysis = self.analyze_all_feedback()
        
        # 同时导出原始反馈数据
        all_feedbacks = self.db_manager.get_all_feedback(limit=10000)
        raw_data = []
        
        for f in all_feedbacks:
            raw_data.append({
                "id": f.id,
                "session_id": f.session_id,
                "user_id": f.user_id,
                "feedback_type": f.feedback_type,
                "rating": f.rating,
                "comment": f.comment,
                "user_message": f.user_message,
                "bot_response": f.bot_response,
                "created_at": f.created_at.isoformat(),
                "is_resolved": f.is_resolved
            })
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "analysis": analysis,
            "raw_feedbacks": raw_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def __del__(self):
        """清理数据库连接"""
        if hasattr(self, 'db_manager'):
            self.db_manager.__exit__(None, None, None)


if __name__ == "__main__":
    """命令行工具：生成反馈分析报告"""
    import argparse
    
    parser = argparse.ArgumentParser(description="用户反馈分析工具")
    parser.add_argument('--days', type=int, default=30, help='分析最近多少天的数据（默认30天）')
    parser.add_argument('--output', type=str, default='feedback_analysis_report.txt', help='报告输出文件')
    parser.add_argument('--export-json', type=str, help='导出JSON数据文件')
    
    args = parser.parse_args()
    
    print("🔍 开始分析用户反馈...")
    analyzer = FeedbackAnalyzer()
    
    # 生成报告
    report = analyzer.generate_detailed_report(output_file=args.output)
    print(f"\n✅ 报告已生成: {args.output}")
    print("\n" + report)
    
    # 导出JSON数据
    if args.export_json:
        analyzer.export_feedback_data(args.export_json)
        print(f"\n✅ 数据已导出: {args.export_json}")

