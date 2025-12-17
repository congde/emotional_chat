#!/usr/bin/env python3
"""
A/B测试数据分析脚本
用于离线分析实验数据，生成报告和可视化
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ab_testing.analyzer import ABTestAnalyzer
from backend.logging_config import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="A/B测试数据分析工具")
    parser.add_argument(
        "--log-file",
        type=str,
        required=True,
        help="事件日志文件路径（JSONL格式）"
    )
    parser.add_argument(
        "--experiment-id",
        type=str,
        required=True,
        help="实验ID"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ab_test_results",
        help="输出目录（默认：ab_test_results）"
    )
    parser.add_argument(
        "--metrics",
        type=str,
        nargs="+",
        default=["user_rating", "response_time", "conversation_interrupted"],
        help="要分析的指标列表"
    )
    parser.add_argument(
        "--generate-charts",
        action="store_true",
        help="生成可视化图表"
    )
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化分析器
    analyzer = ABTestAnalyzer(log_file_path=args.log_file)
    
    # 加载数据
    logger.info(f"加载事件数据: {args.log_file}")
    df = analyzer.load_events()
    logger.info(f"加载了 {len(df)} 条事件记录")
    
    # 过滤实验数据
    df_exp = analyzer.filter_by_experiment(args.experiment_id)
    logger.info(f"实验 {args.experiment_id} 有 {len(df_exp)} 条事件记录")
    
    if df_exp.empty:
        logger.error("实验数据为空，无法进行分析")
        return 1
    
    # 计算指标
    logger.info("计算实验指标...")
    metrics = analyzer.calculate_metrics(
        experiment_id=args.experiment_id,
        metrics=args.metrics
    )
    
    # 保存指标到JSON
    metrics_file = output_dir / f"{args.experiment_id}_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"指标已保存到: {metrics_file}")
    
    # 进行统计检验
    logger.info("进行统计显著性检验...")
    statistical_tests = {}
    groups = sorted(metrics.keys())
    
    if len(groups) >= 2:
        group_a, group_b = groups[0], groups[1]
        
        for metric_name in args.metrics:
            if metric_name in ["user_rating", "response_time"]:
                test_result = analyzer.statistical_test(
                    experiment_id=args.experiment_id,
                    metric=metric_name,
                    group_a=group_a,
                    group_b=group_b
                )
                if "error" not in test_result:
                    statistical_tests[metric_name] = test_result
                    logger.info(
                        f"{metric_name}: p={test_result.get('p_value', 0):.4f}, "
                        f"显著={test_result.get('significant', False)}"
                    )
    
    # 保存统计检验结果
    if statistical_tests:
        tests_file = output_dir / f"{args.experiment_id}_statistical_tests.json"
        with open(tests_file, "w", encoding="utf-8") as f:
            json.dump(statistical_tests, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"统计检验结果已保存到: {tests_file}")
    
    # 生成报告
    logger.info("生成分析报告...")
    report_file = output_dir / f"{args.experiment_id}_report.txt"
    report = analyzer.generate_report(
        experiment_id=args.experiment_id,
        output_path=str(report_file)
    )
    logger.info(f"报告已保存到: {report_file}")
    
    # 生成可视化（如果启用）
    if args.generate_charts:
        logger.info("生成可视化图表...")
        try:
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            sns.set_style("whitegrid")
            
            # 创建图表目录
            charts_dir = output_dir / f"{args.experiment_id}_charts"
            charts_dir.mkdir(exist_ok=True)
            
            # 绘制各指标对比图
            for metric_name in args.metrics:
                if metric_name not in metrics:
                    continue
                
                # 提取数据
                group_data = {}
                for group, group_metrics in metrics.items():
                    if metric_name in group_metrics:
                        metric_data = group_metrics[metric_name]
                        if "values" in metric_data:
                            group_data[group] = metric_data["values"]
                
                if not group_data:
                    continue
                
                # 创建箱线图
                fig, ax = plt.subplots(figsize=(10, 6))
                data_to_plot = [group_data[g] for g in sorted(group_data.keys())]
                labels = sorted(group_data.keys())
                
                bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
                
                # 美化
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
                for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax.set_title(f"{metric_name} 对比", fontsize=14, fontweight='bold')
                ax.set_ylabel(metric_name, fontsize=12)
                ax.set_xlabel("实验组", fontsize=12)
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                chart_file = charts_dir / f"{metric_name}_comparison.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                logger.info(f"图表已保存到: {chart_file}")
            
            logger.info(f"所有图表已保存到: {charts_dir}")
        
        except ImportError:
            logger.warning("matplotlib或seaborn未安装，跳过图表生成")
        except Exception as e:
            logger.error(f"生成图表失败: {e}", exc_info=True)
    
    logger.info("分析完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())

