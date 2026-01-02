"""
Hazard Risk Dashboard - 隐患排查与风险可视化系统
主程序入口

功能：
1. 生成模拟隐患数据（历史+近期）
2. 执行风险分析
3. 生成交互式仪表板
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import webbrowser

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_generator import HazardDataGenerator, print_data_summary
from risk_analyzer import RiskAnalyzer
from dashboard_generator import DashboardGenerator


def print_banner():
    """打印启动横幅"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║     隐患排查与风险可视化系统                                       ║
    ║     Hazard Risk Monitoring Dashboard                             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


def main():
    """主函数"""
    print_banner()
    
    print("="*70)
    print("隐患排查与风险可视化系统")
    print("="*70)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 检查数据目录
    data_dir = Path(__file__).parent / 'data'
    output_dir = Path(__file__).parent / 'outputs'
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已有数据文件
    hazards_file = data_dir / 'hazards.csv'
    
    if hazards_file.exists():
        print(f"\n步骤 1/4: 加载现有数据")
        print(f"  检测到数据文件: {hazards_file}")
        import pandas as pd
        df = pd.read_csv(hazards_file)
        df['date'] = pd.to_datetime(df['date'])
        print(f"  [OK] 已加载 {len(df)} 条隐患记录")
    else:
        print(f"\n步骤 1/4: 生成模拟数据")
        generator = HazardDataGenerator()
        df = generator.generate_all_data()
        generator.save_data(df, data_dir)
    
    # 打印数据摘要
    print_data_summary(df)
    
    # 风险分析
    print("\n" + "="*70)
    print("步骤 2/4: 风险分析")
    print("="*70)
    
    analyzer = RiskAnalyzer(df)
    
    # 汇总统计
    stats = analyzer.get_summary_stats()
    print("\n[整体统计]")
    print(f"  累计隐患: {stats['total']:,} 条")
    print(f"  已整改: {stats['rectified']:,} 条")
    print(f"  整改率: {stats['rectify_rate']}%")
    print(f"  平均风险分: {stats['avg_risk_score']}")
    
    # 帕累托分析
    pareto = analyzer.get_pareto_analysis('hazard_type')
    vital_few = pareto[pareto['is_vital_few'] == True]
    print(f"\n[帕累托分析]")
    print(f"  关键少数 (占80%问题): {len(vital_few)} 种隐患类型")
    for _, row in vital_few.head(5).iterrows():
        print(f"    - {row['hazard_type']}: {row['count']}条 ({row['percentage']}%)")
    
    # 区域风险
    area_summary = analyzer.get_area_summary()
    print(f"\n[高风险区域 TOP 3]")
    for _, row in area_summary.head(3).iterrows():
        print(f"    - {row['area_name']}: 风险总分={row['total_risk']:.0f}, 高风险={row['high_risk_count']}条")
    
    # 生成报告
    print("\n" + "="*70)
    print("步骤 3/4: 生成Excel报告")
    print("="*70)
    
    # 保存分析结果到Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 区域汇总
    area_report_path = output_dir / f'area_summary_{timestamp}.xlsx'
    area_summary.to_excel(area_report_path, index=False, engine='openpyxl')
    print(f"  [OK] 区域分析报告: {area_report_path}")
    
    # 滞留隐患（超过7天未整改）
    overdue = analyzer.get_overdue_hazards(7)
    overdue_path = output_dir / f'overdue_hazards_{timestamp}.xlsx'
    overdue.to_excel(overdue_path, index=False, engine='openpyxl')
    print(f"  [OK] 滞留隐患清单: {overdue_path} ({len(overdue)}条)")
    
    # 生成仪表板
    print("\n" + "="*70)
    print("步骤 4/4: 生成可视化仪表板")
    print("="*70)
    
    dashboard = DashboardGenerator(df)
    dashboard_path = dashboard.generate_html_report()
    
    # 自动打开仪表板
    print(f"\n正在打开仪表板: {dashboard_path}")
    webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
    
    # 完成
    print("\n" + "="*70)
    print("所有任务执行完成！")
    print("="*70)
    
    print(f"\n输出文件位置: {output_dir}")
    print("\n生成的文件:")
    for f in output_dir.glob(f'*{timestamp}*'):
        size = f.stat().st_size / 1024
        ext = f.suffix.upper()[1:]
        print(f"  [{ext}] {f.name} ({size:.1f} KB)")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()

