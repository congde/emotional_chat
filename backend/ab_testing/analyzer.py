#!/usr/bin/env python3
"""
A/B测试数据分析模块
提供统计分析、显著性检验等功能
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from scipy import stats
from pathlib import Path
from backend.logging_config import get_logger

logger = get_logger(__name__)


class ABTestAnalyzer:
    """
    A/B测试数据分析器
    
    提供统计分析、显著性检验、可视化等功能
    """
    
    def __init__(self, log_file_path: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            log_file_path: 事件日志文件路径（JSONL格式）
        """
        self.log_file_path = log_file_path
        self.df: Optional[pd.DataFrame] = None
    
    def load_events(self, log_file_path: Optional[str] = None) -> pd.DataFrame:
        """
        从日志文件加载事件数据
        
        Args:
            log_file_path: 日志文件路径（可选，如果未提供则使用初始化时的路径）
        
        Returns:
            DataFrame包含所有事件
        """
        file_path = log_file_path or self.log_file_path
        if not file_path:
            raise ValueError("必须提供日志文件路径")
        
        events = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析JSON失败: {e}")
        
        self.df = pd.DataFrame(events)
        
        # 转换时间戳
        if "timestamp" in self.df.columns:
            self.df["datetime"] = pd.to_datetime(self.df["timestamp"], unit="s")
        
        return self.df
    
    def filter_by_experiment(
        self,
        experiment_id: str,
        df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        按实验ID过滤数据
        
        Args:
            experiment_id: 实验ID
            df: 数据框（可选，如果未提供则使用self.df）
        
        Returns:
            过滤后的数据框
        """
        data = df if df is not None else self.df
        if data is None:
            raise ValueError("数据未加载，请先调用load_events()")
        
        return data[data["experiment_id"] == experiment_id].copy()
    
    def calculate_metrics(
        self,
        experiment_id: str,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        计算实验指标
        
        Args:
            experiment_id: 实验ID
            metrics: 要计算的指标列表，可选：
                - "user_rating": 用户评分
                - "response_time": 响应时间
                - "conversation_interrupted": 对话中断率
                - "session_duration": 会话时长
                - "message_count": 消息数量
        
        Returns:
            包含各组指标的字典
        """
        if metrics is None:
            metrics = ["user_rating", "response_time", "conversation_interrupted"]
        
        df_exp = self.filter_by_experiment(experiment_id)
        if df_exp.empty:
            return {}
        
        results = {}
        groups = df_exp["group"].unique()
        
        for group in groups:
            df_group = df_exp[df_exp["group"] == group]
            group_metrics = {}
            
            # 用户评分
            if "user_rating" in metrics:
                ratings = self._extract_ratings(df_group)
                if ratings:
                    group_metrics["user_rating"] = {
                        "mean": np.mean(ratings),
                        "std": np.std(ratings),
                        "count": len(ratings),
                        "values": ratings
                    }
            
            # 响应时间
            if "response_time" in metrics:
                response_times = self._extract_response_times(df_group)
                if response_times:
                    group_metrics["response_time"] = {
                        "mean": np.mean(response_times),
                        "std": np.std(response_times),
                        "count": len(response_times),
                        "values": response_times
                    }
            
            # 对话中断率
            if "conversation_interrupted" in metrics:
                interrupted_count = len(df_group[df_group["event"] == "conversation_interrupted"])
                total_sessions = len(df_group[df_group["event"] == "session_start"])
                if total_sessions > 0:
                    group_metrics["conversation_interrupted"] = {
                        "rate": interrupted_count / total_sessions,
                        "count": interrupted_count,
                        "total_sessions": total_sessions
                    }
            
            results[group] = group_metrics
        
        return results
    
    def _extract_ratings(self, df: pd.DataFrame) -> List[float]:
        """从数据框中提取评分"""
        ratings = []
        for _, row in df[df["event"] == "user_rating_submitted"].iterrows():
            data = row.get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            rating = data.get("rating")
            if rating is not None:
                ratings.append(float(rating))
        return ratings
    
    def _extract_response_times(self, df: pd.DataFrame) -> List[float]:
        """从数据框中提取响应时间"""
        response_times = []
        for _, row in df[df["event"] == "response_received"].iterrows():
            data = row.get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            rt = data.get("response_time")
            if rt is not None:
                response_times.append(float(rt))
        return response_times
    
    def statistical_test(
        self,
        experiment_id: str,
        metric: str,
        group_a: str = "A",
        group_b: str = "B",
        test_type: str = "t_test"
    ) -> Dict[str, Any]:
        """
        进行统计显著性检验
        
        Args:
            experiment_id: 实验ID
            metric: 指标名称（如 "user_rating", "response_time"）
            group_a: A组名称
            group_b: B组名称
            test_type: 检验类型，可选 "t_test", "mannwhitney", "chi2"
        
        Returns:
            检验结果，包含p值、统计量等
        """
        metrics = self.calculate_metrics(experiment_id, metrics=[metric])
        
        if group_a not in metrics or group_b not in metrics:
            return {"error": "组数据不存在"}
        
        data_a = metrics[group_a].get(metric, {}).get("values", [])
        data_b = metrics[group_b].get(metric, {}).get("values", [])
        
        if not data_a or not data_b:
            return {"error": "数据不足"}
        
        result = {
            "metric": metric,
            "group_a": group_a,
            "group_b": group_b,
            "test_type": test_type,
            "n_a": len(data_a),
            "n_b": len(data_b),
            "mean_a": np.mean(data_a),
            "mean_b": np.mean(data_b),
            "std_a": np.std(data_a),
            "std_b": np.std(data_b)
        }
        
        if test_type == "t_test":
            # 独立样本t检验
            t_stat, p_value = stats.ttest_ind(data_a, data_b)
            result["t_statistic"] = float(t_stat)
            result["p_value"] = float(p_value)
            result["significant"] = p_value < 0.05
        elif test_type == "mannwhitney":
            # Mann-Whitney U检验（非参数）
            u_stat, p_value = stats.mannwhitneyu(data_a, data_b, alternative="two-sided")
            result["u_statistic"] = float(u_stat)
            result["p_value"] = float(p_value)
            result["significant"] = p_value < 0.05
        elif test_type == "chi2":
            # 卡方检验（用于分类数据）
            # 这里需要根据具体指标实现
            pass
        else:
            return {"error": f"不支持的检验类型: {test_type}"}
        
        # 计算效应量（Cohen's d）
        pooled_std = np.sqrt(((len(data_a) - 1) * np.var(data_a) + (len(data_b) - 1) * np.var(data_b)) / 
                           (len(data_a) + len(data_b) - 2))
        if pooled_std > 0:
            cohens_d = (np.mean(data_a) - np.mean(data_b)) / pooled_std
            result["cohens_d"] = float(cohens_d)
            # 解释效应量
            if abs(cohens_d) < 0.2:
                result["effect_size"] = "negligible"
            elif abs(cohens_d) < 0.5:
                result["effect_size"] = "small"
            elif abs(cohens_d) < 0.8:
                result["effect_size"] = "medium"
            else:
                result["effect_size"] = "large"
        
        return result
    
    def generate_report(
        self,
        experiment_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        生成分析报告
        
        Args:
            experiment_id: 实验ID
            output_path: 输出文件路径（可选）
        
        Returns:
            报告文本
        """
        metrics = self.calculate_metrics(experiment_id)
        if not metrics:
            return "实验数据不足，无法生成报告"
        
        report_lines = [
            "=" * 80,
            f"A/B测试分析报告 - {experiment_id}",
            "=" * 80,
            "",
            "## 一、总体表现对比",
            "-" * 80,
            ""
        ]
        
        # 表格头部
        header = f"{'版本':<15} {'样本数':<10} "
        metric_names = []
        for group in metrics.keys():
            group_data = metrics[group]
            for metric_name in group_data.keys():
                if metric_name not in metric_names:
                    metric_names.append(metric_name)
                    header += f"{metric_name:<15} "
        
        report_lines.append(header)
        report_lines.append("-" * 80)
        
        # 各组数据
        for group in sorted(metrics.keys()):
            group_data = metrics[group]
            row = f"{group:<15} "
            
            # 样本数
            sample_count = 0
            for metric_name in metric_names:
                if metric_name in group_data:
                    values = group_data[metric_name].get("values", [])
                    if values:
                        sample_count = max(sample_count, len(values))
            
            row += f"{sample_count:<10} "
            
            # 各指标
            for metric_name in metric_names:
                if metric_name in group_data:
                    metric_data = group_data[metric_name]
                    if "mean" in metric_data:
                        mean = metric_data["mean"]
                        std = metric_data.get("std", 0)
                        row += f"{mean:.2f}±{std:.2f}  "
                    elif "rate" in metric_data:
                        rate = metric_data["rate"]
                        row += f"{rate:.2%}      "
                    else:
                        row += f"{'N/A':<15} "
                else:
                    row += f"{'N/A':<15} "
            
            report_lines.append(row)
        
        report_lines.append("")
        report_lines.append("## 二、详细统计数据")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        # 各组详细统计
        for group in sorted(metrics.keys()):
            group_data = metrics[group]
            report_lines.append(f"### 版本{group}")
            report_lines.append("")
            
            for metric_name, metric_data in group_data.items():
                if "mean" in metric_data:
                    mean = metric_data["mean"]
                    std = metric_data.get("std", 0)
                    count = metric_data.get("count", 0)
                    report_lines.append(
                        f"  {metric_name}: {mean:.2f} ± {std:.2f} (n={count})"
                    )
                elif "rate" in metric_data:
                    rate = metric_data["rate"]
                    count = metric_data.get("count", 0)
                    total = metric_data.get("total_sessions", 0)
                    report_lines.append(
                        f"  {metric_name}: {rate:.2%} (n={count}/{total})"
                    )
            
            report_lines.append("")
        
        # 显著性检验
        if len(metrics) >= 2:
            groups = sorted(metrics.keys())
            group_a, group_b = groups[0], groups[1]
            
            report_lines.append("## 三、统计显著性检验")
            report_lines.append("-" * 80)
            report_lines.append("")
            
            for metric_name in metric_names:
                if metric_name in ["user_rating", "response_time"]:
                    test_result = self.statistical_test(
                        experiment_id, metric_name, group_a, group_b
                    )
                    if "error" not in test_result:
                        p_value = test_result.get("p_value", 1.0)
                        significant = test_result.get("significant", False)
                        report_lines.append(
                            f"### {metric_name}"
                        )
                        report_lines.append(
                            f"  P值: {p_value:.4f} {'(显著)' if significant else '(不显著)'}"
                        )
                        if "cohens_d" in test_result:
                            cohens_d = test_result["cohens_d"]
                            effect_size = test_result.get("effect_size", "")
                            report_lines.append(
                                f"  效应量 (Cohen's d): {cohens_d:.3f} ({effect_size})"
                            )
                        report_lines.append("")
        
        report_lines.append("## 四、结论与建议")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("（根据数据自动生成建议）")
        report_lines.append("")
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            logger.info(f"报告已保存到: {output_path}")
        
        return report_text

