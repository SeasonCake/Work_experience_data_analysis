"""
Dashboard Generator
功能：生成完整的HTML仪表板
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict

from risk_analyzer import RiskAnalyzer
from visualizer import HazardVisualizer


class DashboardGenerator:
    """仪表板生成器"""
    
    def __init__(self, df: pd.DataFrame, config_path: str = None):
        """
        初始化
        
        Args:
            df: 隐患数据
            config_path: 配置文件路径
        """
        self.df = df
        self.analyzer = RiskAnalyzer(df, config_path)
        self.visualizer = HazardVisualizer(config_path)
        self.generated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_html_report(self, output_path: str = None) -> str:
        """
        生成完整HTML报告
        
        Args:
            output_path: 输出路径
            
        Returns:
            str: HTML文件路径
        """
        print("\n正在生成可视化仪表板...")
        
        # 获取各类数据
        stats = self.analyzer.get_summary_stats()
        stats_week = self.analyzer.get_summary_stats('week')
        
        pareto_type = self.analyzer.get_pareto_analysis('hazard_type')
        
        quarterly_trend = self.analyzer.get_quarterly_trend()
        area_summary = self.analyzer.get_area_summary(days=30)  # 30天数据用于热力图
        
        surface_time = self.analyzer.get_3d_surface_data()
        surface_category = self.analyzer.get_3d_category_surface_data()
        
        # 近7天中高风险预警（新发现的）
        recent_alerts = self.analyzer.get_recent_alerts(7, 15)
        # 获取所有隐患记录（可筛选，不限制数量）
        all_hazards = self.analyzer.get_all_hazards_with_status()
        
        # 计算区域风险分数（用于热力图）
        # 使用总风险分数，更直观地反映风险严重程度
        area_risks = {}
        for _, row in area_summary.iterrows():
            area_name = row['area_name']
            # 在配置中找到对应的code
            for area in self.visualizer.config['areas']:
                if area['name'] == area_name:
                    # 使用总风险分数直接作为热力图的值
                    area_risks[area['code']] = row['total_risk']
                    break
        
        # 生成图表
        factory_heatmap = self.visualizer.create_factory_heatmap(area_risks)
        pareto_chart = self.visualizer.create_pareto_chart(pareto_type, 'hazard_type')
        trend_chart = self.visualizer.create_trend_chart(quarterly_trend, 'quarter')
        
        surface_plot = self.visualizer.create_3d_surface_plot(
            surface_time, '风险响应面图 (区域 × 时间)'
        )
        surface_plot2 = self.visualizer.create_3d_surface_plot(
            surface_category, '风险响应面图 (区域 × 隐患类型)'
        )
        
        risk_pie = self.visualizer.create_risk_level_pie({
            'High': stats['high_risk'],
            'Medium': stats['medium_risk'],
            'Low': stats['low_risk']
        })
        
        treemap = self.visualizer.create_category_treemap(self.df, days=90)  # 90天数据
        
        # 生成表格HTML
        alerts_table = self._generate_alerts_table(recent_alerts)
        all_hazards_table = self._generate_all_hazards_table(all_hazards)
        
        # 组装HTML
        html = self._build_html(
            stats=stats,
            stats_week=stats_week,
            factory_heatmap=factory_heatmap,
            pareto_chart=pareto_chart,
            trend_chart=trend_chart,
            surface_plot=surface_plot,
            surface_plot2=surface_plot2,
            risk_pie=risk_pie,
            treemap=treemap,
            alerts_table=alerts_table,
            all_hazards_table=all_hazards_table
        )
        
        # 保存文件
        if output_path is None:
            output_dir = Path(__file__).parent.parent / 'outputs'
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f'risk_dashboard_{timestamp}.html'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  [OK] 仪表板已生成: {output_path}")
        
        return str(output_path)
    
    def _generate_alerts_table(self, df: pd.DataFrame) -> str:
        """生成预警表格HTML（带排序功能）"""
        if len(df) == 0:
            return "<p>暂无预警数据</p>"
        
        rows = ""
        for _, row in df.iterrows():
            level_class = row['risk_level'].lower()
            # 状态样式：已整改、整改中、逾期
            status = row['status']
            if status == '已整改':
                status_class = 'rectified'
            elif status == '逾期':
                status_class = 'overdue'
            else:  # 整改中
                status_class = 'in-progress'
            
            date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else row['date']
            rows += f"""
            <tr class="{level_class}" data-date="{date_str}" data-score="{row['risk_score']}" data-level="{row['risk_level']}">
                <td data-sort="{date_str}">{date_str}</td>
                <td>{row['area_name']}</td>
                <td>{row['hazard_category']}</td>
                <td>{row['hazard_type']}</td>
                <td class="desc" title="{row['description']}">{row['description'][:40]}...</td>
                <td data-sort="{3 if row['risk_level']=='High' else 2 if row['risk_level']=='Medium' else 1}"><span class="badge {level_class}">{row['risk_level']}</span></td>
                <td data-sort="{row['risk_score']}"><strong>{row['risk_score']}</strong>/10</td>
                <td><span class="status {status_class}">{status}</span></td>
            </tr>
            """
        
        return f"""
        <table class="data-table sortable" id="alertsTable">
            <thead>
                <tr>
                    <th class="sortable-header" data-sort-col="0" data-sort-type="date">发现日期 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="1" data-sort-type="string">区域 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="2" data-sort-type="string">大类 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="3" data-sort-type="string">类型 <span class="sort-icon">⇅</span></th>
                    <th>描述</th>
                    <th class="sortable-header" data-sort-col="5" data-sort-type="number">风险等级 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="6" data-sort-type="number">风险系数 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="7" data-sort-type="string">整改状态 <span class="sort-icon">⇅</span></th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """
    
    def _generate_all_hazards_table(self, df: pd.DataFrame) -> str:
        """生成所有隐患记录表格（可筛选状态，带分页和排序）"""
        if len(df) == 0:
            return "<p>暂无隐患记录</p>"
        
        total_count = len(df)
        rows = ""
        for idx, (_, row) in enumerate(df.iterrows()):
            level_class = row['risk_level'].lower()
            status = row['status']
            days = row.get('overdue_days', 0)
            
            # 状态样式：已整改、整改中、逾期
            if status == '已整改':
                status_class = 'rectified'
            elif status == '逾期':
                status_class = 'overdue'
            else:  # 整改中
                status_class = 'in-progress'
            
            # 超过90天标记为逾期样式
            urgency_class = ''
            if status != '已整改' and days > 90:
                urgency_class = 'critical'
            elif status != '已整改' and days > 60:
                urgency_class = 'warning'
            
            # 整改天数显示
            if status == '已整改':
                days_display = f"<span class='days-rectified'>已完成</span>"
                days_sort = -1  # 已完成的排在最后
            else:
                days_display = f"<strong class='days-{urgency_class if urgency_class else 'normal'}'>{days}</strong>天"
                days_sort = days
            
            date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])[:10]
            level_sort = 3 if row['risk_level']=='High' else 2 if row['risk_level']=='Medium' else 1
            
            rows += f"""
            <tr class="{level_class} {urgency_class}" data-status="{status}" data-row-index="{idx}" data-date="{date_str}" data-level="{level_sort}" data-days="{days_sort}">
                <td data-sort="{row['hazard_id']}">{row['hazard_id']}</td>
                <td data-sort="{date_str}">{date_str}</td>
                <td>{row['area_name']}</td>
                <td>{row['hazard_type']}</td>
                <td data-sort="{level_sort}"><span class="badge {level_class}">{row['risk_level']}</span></td>
                <td data-sort="{days_sort}">{days_display}</td>
                <td>{row['responsible']}</td>
                <td data-sort="{0 if status=='已整改' else 1 if status=='整改中' else 2}"><span class="status {status_class}">{status}</span></td>
            </tr>
            """
        
        return f"""
        <table class="data-table sortable" id="allHazardsTable" data-total="{total_count}">
            <thead>
                <tr>
                    <th class="sortable-header" data-sort-col="0" data-sort-type="string">编号 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="1" data-sort-type="date">发现日期 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="2" data-sort-type="string">区域 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="3" data-sort-type="string">类型 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="4" data-sort-type="number">风险等级 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="5" data-sort-type="number">处理时间 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="6" data-sort-type="string">责任人 <span class="sort-icon">⇅</span></th>
                    <th class="sortable-header" data-sort-col="7" data-sort-type="number">状态 <span class="sort-icon">⇅</span></th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <div class="load-more-container">
            <button id="loadMoreBtn" class="load-more-btn" onclick="loadMore()">
                展开更多 <span id="loadMoreInfo">(已显示 <span id="currentShown">50</span> / {total_count} 条)</span>
            </button>
        </div>
        """
    
    def _build_html(self, **kwargs) -> str:
        """构建完整HTML"""
        stats = kwargs['stats']
        stats_week = kwargs['stats_week']
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>隐患排查与风险监控仪表板</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #ecf0f1;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 2.2em;
            font-weight: 600;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        header .subtitle {{
            color: #95a5a6;
            font-size: 1em;
        }}
        
        /* 统计卡片 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .stat-card .value {{
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #95a5a6;
            font-size: 0.9em;
        }}
        
        .stat-card .change {{
            font-size: 0.85em;
            margin-top: 8px;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        
        .stat-card.primary .value {{ color: #3498db; }}
        .stat-card.success .value {{ color: #2ecc71; }}
        .stat-card.warning .value {{ color: #f39c12; }}
        .stat-card.danger .value {{ color: #e74c3c; }}
        
        /* 图表区域 */
        .charts-section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(52, 152, 219, 0.5);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title::before {{
            content: '';
            width: 4px;
            height: 24px;
            background: #3498db;
            border-radius: 2px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        
        .chart-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        
        .chart-card.full-width {{
            grid-column: span 2;
        }}
        
        /* 3D图表特殊样式 */
        .chart-3d {{
            background: linear-gradient(145deg, rgba(26,26,46,0.9), rgba(15,52,96,0.9));
        }}
        
        /* 表格样式 */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        .data-table th {{
            background: rgba(52, 152, 219, 0.3);
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        .data-table tr:hover {{
            background: rgba(255,255,255,0.08);
        }}
        
        /* 排序功能样式 */
        .sortable-header {{
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
            white-space: nowrap;
        }}
        
        .sortable-header:hover {{
            background: rgba(52, 152, 219, 0.5);
        }}
        
        .sort-icon {{
            font-size: 0.8em;
            opacity: 0.5;
            margin-left: 5px;
            transition: opacity 0.2s;
        }}
        
        .sortable-header:hover .sort-icon {{
            opacity: 1;
        }}
        
        .sortable-header.sort-asc .sort-icon::after {{
            content: '↑';
        }}
        
        .sortable-header.sort-desc .sort-icon::after {{
            content: '↓';
        }}
        
        .sortable-header.sort-asc .sort-icon,
        .sortable-header.sort-desc .sort-icon {{
            opacity: 1;
            color: #3498db;
        }}
        
        .data-table tr.high {{ border-left: 3px solid #e74c3c; }}
        .data-table tr.medium {{ border-left: 3px solid #f39c12; }}
        .data-table tr.low {{ border-left: 3px solid #2ecc71; }}
        .data-table tr.overdue {{ background: rgba(231, 76, 60, 0.1); }}
        
        .data-table .desc {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        /* 徽章 */
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.high {{ background: rgba(231, 76, 60, 0.8); }}
        .badge.medium {{ background: rgba(243, 156, 18, 0.8); }}
        .badge.low {{ background: rgba(46, 204, 113, 0.8); }}
        
        .status {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }}
        
        .status.rectified {{ background: rgba(46, 204, 113, 0.3); color: #2ecc71; }}
        .status.in-progress {{ background: rgba(243, 156, 18, 0.3); color: #f39c12; }}
        .status.overdue {{ background: rgba(231, 76, 60, 0.4); color: #e74c3c; font-weight: bold; }}
        
        /* 滞留天数高亮 */
        .days-critical {{ color: #e74c3c; font-size: 1.1em; }}
        .days-warning {{ color: #f39c12; }}
        .days-normal {{ color: #3498db; }}
        .days-rectified {{ color: #2ecc71; font-weight: normal; }}
        
        /* 滞留行样式 */
        .data-table tr.critical {{ background: rgba(231, 76, 60, 0.15); }}
        .data-table tr.warning {{ background: rgba(243, 156, 18, 0.1); }}
        
        /* 状态筛选按钮 */
        .status-filter {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #3498db;
            background: transparent;
            color: #ecf0f1;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }}
        .filter-btn:hover {{
            background: rgba(52, 152, 219, 0.2);
        }}
        .filter-btn.active {{
            background: #3498db;
            color: #fff;
        }}
        .filter-btn.rectified-btn {{
            border-color: #2ecc71;
        }}
        .filter-btn.rectified-btn:hover {{
            background: rgba(46, 204, 113, 0.2);
        }}
        .filter-btn.rectified-btn.active {{
            background: #2ecc71;
        }}
        .filter-btn.inprogress-btn {{
            border-color: #f39c12;
        }}
        .filter-btn.inprogress-btn:hover {{
            background: rgba(243, 156, 18, 0.2);
        }}
        .filter-btn.inprogress-btn.active {{
            background: #f39c12;
        }}
        .filter-btn.overdue-btn {{
            border-color: #e74c3c;
        }}
        .filter-btn.overdue-btn:hover {{
            background: rgba(231, 76, 60, 0.2);
        }}
        .filter-btn.overdue-btn.active {{
            background: #e74c3c;
        }}
        
        /* 筛选栏布局优化 */
        .filter-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        /* 展开更多按钮 */
        .load-more-container {{
            text-align: center;
            margin-top: 20px;
            padding: 15px;
        }}
        .load-more-btn {{
            padding: 12px 30px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }}
        .load-more-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }}
        .load-more-btn:disabled {{
            background: #7f8c8d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        #loadMoreInfo {{
            font-size: 0.85em;
            opacity: 0.9;
        }}
        
        /* Section描述 */
        .section-desc {{
            color: #95a5a6;
            font-size: 0.9em;
            margin-top: -15px;
            margin-bottom: 15px;
        }}
        
        /* 搜索框 */
        .filter-bar {{
            margin-bottom: 15px;
        }}
        
        .filter-bar input {{
            padding: 10px 15px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 0.95em;
            width: 300px;
        }}
        
        .filter-bar input:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 8px rgba(52, 152, 219, 0.5);
        }}
        
        /* 页脚 */
        footer {{
            text-align: center;
            padding: 30px;
            margin-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        /* 响应式 */
        @media (max-width: 1200px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            .chart-card.full-width {{ grid-column: span 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>隐患排查与风险监控仪表板</h1>
            <p class="subtitle">Hazard Risk Monitoring Dashboard | 数据更新: {self.generated_time}</p>
        </header>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="value">{stats['total']:,}</div>
                <div class="label">累计隐患总数</div>
                <div class="change">本周新增: {stats_week['total']}</div>
            </div>
            <div class="stat-card success">
                <div class="value">{stats['rectify_rate']}%</div>
                <div class="label">整改率</div>
                <div class="change">{'达标' if stats['rectify_rate'] >= 85 else '未达标 (目标85%)'}</div>
            </div>
            <div class="stat-card warning">
                <div class="value">{stats['overdue'] + stats['in_progress']}</div>
                <div class="label">待整改隐患</div>
                <div class="change">整改中: {stats['in_progress']} / 逾期: {stats['overdue']}</div>
            </div>
            <div class="stat-card danger">
                <div class="value">{stats['high_risk']}</div>
                <div class="label">高风险隐患</div>
                <div class="change">占比: {stats['high_risk']/stats['total']*100:.1f}%</div>
            </div>
            <div class="stat-card primary">
                <div class="value">{stats['avg_risk_score']}</div>
                <div class="label">平均风险分</div>
                <div class="change">满分10分</div>
            </div>
            <div class="stat-card success">
                <div class="value">{stats['avg_rectify_days']}</div>
                <div class="label">平均整改天数</div>
                <div class="change">天</div>
            </div>
        </div>
        
        <!-- 厂区热力图 & 帕累托图 -->
        <section class="charts-section">
            <h2 class="section-title">风险概览</h2>
            <div class="charts-grid">
                <div class="chart-card">
                    {kwargs['factory_heatmap']}
                </div>
                <div class="chart-card">
                    {kwargs['pareto_chart']}
                </div>
            </div>
        </section>
        
        <!-- 隐患分布（矩形树图） & 整改趋势 -->
        <section class="charts-section">
            <h2 class="section-title">隐患分布与整改趋势</h2>
            <div class="charts-grid">
                <div class="chart-card">
                    {kwargs['treemap']}
                </div>
                <div class="chart-card">
                    {kwargs['trend_chart']}
                </div>
            </div>
        </section>
        
        <!-- 3D曲面图 -->
        <section class="charts-section">
            <h2 class="section-title">3D风险响应面分析</h2>
            <div class="charts-grid">
                <div class="chart-card chart-3d">
                    {kwargs['surface_plot']}
                </div>
                <div class="chart-card chart-3d">
                    {kwargs['surface_plot2']}
                </div>
            </div>
        </section>
        
        <!-- 近7天中高风险预警（新发现的） -->
        <section class="charts-section">
            <h2 class="section-title">近7天中高风险预警</h2>
            <p class="section-desc">近7天新发现的中、高风险隐患，需优先处理</p>
            <div class="chart-card full-width">
                <div class="filter-bar">
                    <input type="text" id="alertSearch" placeholder="搜索区域、类型、描述..." onkeyup="filterTable('alertSearch', 'alertTable')">
                </div>
                <div id="alertTable">
                    {kwargs['alerts_table']}
                </div>
            </div>
        </section>
        
        <!-- 隐患记录总览（可筛选状态） -->
        <section class="charts-section">
            <h2 class="section-title">隐患记录总览</h2>
            <p class="section-desc">所有隐患记录，可按状态筛选（超90天未整改标记为逾期）</p>
            <div class="chart-card full-width">
                <div class="filter-bar">
                    <div class="status-filter">
                        <button class="filter-btn active" onclick="filterByStatus('all')">全部</button>
                        <button class="filter-btn rectified-btn" onclick="filterByStatus('已整改')">已整改</button>
                        <button class="filter-btn inprogress-btn" onclick="filterByStatus('整改中')">整改中</button>
                        <button class="filter-btn overdue-btn" onclick="filterByStatus('逾期')">逾期</button>
                    </div>
                    <input type="text" id="allHazardsSearch" placeholder="搜索编号、区域、类型..." onkeyup="filterTable('allHazardsSearch', 'allHazardsContainer')">
                </div>
                <div id="allHazardsContainer">
                    {kwargs['all_hazards_table']}
                </div>
            </div>
        </section>
        
        <footer>
            <p>Hazard Risk Dashboard v1.0 | Generated: {self.generated_time}</p>
            <p>数据范围: 2024年1月 - 至今 | 共 {stats['total']:,} 条隐患记录</p>
        </footer>
    </div>
    
    <script>
        function filterTable(inputId, tableId) {{
            var input = document.getElementById(inputId);
            var filter = input.value.toLowerCase();
            var container = document.getElementById(tableId);
            var rows = container.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {{
                var text = row.textContent.toLowerCase();
                var currentStatus = row.getAttribute('data-status') || '';
                var statusFilter = window.currentStatusFilter || 'all';
                var matchesText = text.includes(filter);
                var matchesStatus = statusFilter === 'all' || currentStatus === statusFilter;
                row.style.display = (matchesText && matchesStatus) ? '' : 'none';
            }});
        }}
        
        window.currentStatusFilter = 'all';
        window.currentVisibleCount = 50;  // 默认显示50条
        window.loadIncrement = 100;  // 每次加载100条
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initPagination();
            filterByStatus('all');
        }});
        
        function initPagination() {{
            var table = document.getElementById('allHazardsTable');
            var rows = table.querySelectorAll('tbody tr');
            var total = rows.length;
            
            // 初始只显示前50条
            rows.forEach(function(row, index) {{
                if (index >= window.currentVisibleCount) {{
                    row.classList.add('hidden-row');
                }}
            }});
            
            updateLoadMoreButton();
        }}
        
        function loadMore() {{
            var table = document.getElementById('allHazardsTable');
            var rows = table.querySelectorAll('tbody tr');
            var currentFilter = window.currentStatusFilter;
            
            var newLimit = window.currentVisibleCount + window.loadIncrement;
            window.currentVisibleCount = newLimit;
            
            // 重新应用筛选和分页
            applyFiltersAndPagination();
        }}
        
        function applyFiltersAndPagination() {{
            var container = document.getElementById('allHazardsContainer');
            var rows = container.querySelectorAll('tbody tr');
            var searchInput = document.getElementById('allHazardsSearch');
            var searchFilter = searchInput ? searchInput.value.toLowerCase() : '';
            var statusFilter = window.currentStatusFilter;
            
            var visibleIndex = 0;
            rows.forEach(function(row) {{
                var rowStatus = row.getAttribute('data-status');
                var text = row.textContent.toLowerCase();
                var matchesStatus = statusFilter === 'all' || rowStatus === statusFilter;
                var matchesText = text.includes(searchFilter);
                
                if (matchesStatus && matchesText) {{
                    if (visibleIndex < window.currentVisibleCount) {{
                        row.style.display = '';
                        row.classList.remove('hidden-row');
                    }} else {{
                        row.style.display = 'none';
                        row.classList.add('hidden-row');
                    }}
                    visibleIndex++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            updateLoadMoreButton();
        }}
        
        function updateLoadMoreButton() {{
            var container = document.getElementById('allHazardsContainer');
            var rows = container.querySelectorAll('tbody tr');
            var statusFilter = window.currentStatusFilter;
            var searchInput = document.getElementById('allHazardsSearch');
            var searchFilter = searchInput ? searchInput.value.toLowerCase() : '';
            
            // 计算符合筛选条件的总数
            var matchingTotal = 0;
            rows.forEach(function(row) {{
                var rowStatus = row.getAttribute('data-status');
                var text = row.textContent.toLowerCase();
                var matchesStatus = statusFilter === 'all' || rowStatus === statusFilter;
                var matchesText = text.includes(searchFilter);
                if (matchesStatus && matchesText) matchingTotal++;
            }});
            
            var shown = Math.min(window.currentVisibleCount, matchingTotal);
            document.getElementById('currentShown').textContent = shown;
            
            var btn = document.getElementById('loadMoreBtn');
            var info = document.getElementById('loadMoreInfo');
            
            if (shown >= matchingTotal) {{
                btn.disabled = true;
                btn.textContent = '已显示全部 (' + matchingTotal + ' 条)';
            }} else {{
                btn.disabled = false;
                btn.innerHTML = '展开更多 <span id="loadMoreInfo">(已显示 <span id="currentShown">' + shown + '</span> / ' + matchingTotal + ' 条)</span>';
            }}
        }}
        
        function filterByStatus(status) {{
            window.currentStatusFilter = status;
            window.currentVisibleCount = 50;  // 切换筛选时重置为50条
            
            var buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(function(btn) {{
                btn.classList.remove('active');
                if (btn.textContent === status || (status === 'all' && btn.textContent === '全部')) {{
                    btn.classList.add('active');
                }}
            }});
            
            applyFiltersAndPagination();
        }}
        
        function updateStats() {{
            var container = document.getElementById('allHazardsContainer');
            var rows = container.querySelectorAll('tbody tr');
            var visible = 0;
            rows.forEach(function(row) {{
                if (row.style.display !== 'none') visible++;
            }});
        }}
        
        // ========== 表格排序功能 ==========
        document.addEventListener('DOMContentLoaded', function() {{
            // 为所有可排序表头添加点击事件
            document.querySelectorAll('.sortable-header').forEach(function(header) {{
                header.addEventListener('click', function() {{
                    var table = this.closest('table');
                    var colIndex = parseInt(this.getAttribute('data-sort-col'));
                    var sortType = this.getAttribute('data-sort-type') || 'string';
                    var currentDirection = this.classList.contains('sort-asc') ? 'asc' : 
                                          this.classList.contains('sort-desc') ? 'desc' : 'none';
                    
                    // 清除其他列的排序状态
                    table.querySelectorAll('.sortable-header').forEach(function(h) {{
                        h.classList.remove('sort-asc', 'sort-desc');
                        h.querySelector('.sort-icon').textContent = '⇅';
                    }});
                    
                    // 设置新的排序方向
                    var newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                    this.classList.add('sort-' + newDirection);
                    this.querySelector('.sort-icon').textContent = newDirection === 'asc' ? '↑' : '↓';
                    
                    // 执行排序
                    sortTable(table, colIndex, sortType, newDirection);
                }});
            }});
        }});
        
        function sortTable(table, colIndex, sortType, direction) {{
            var tbody = table.querySelector('tbody');
            var rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort(function(a, b) {{
                var aCell = a.cells[colIndex];
                var bCell = b.cells[colIndex];
                
                // 获取排序值（优先使用data-sort属性）
                var aVal = aCell.getAttribute('data-sort') || aCell.textContent.trim();
                var bVal = bCell.getAttribute('data-sort') || bCell.textContent.trim();
                
                var comparison = 0;
                
                if (sortType === 'number') {{
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                    comparison = aVal - bVal;
                }} else if (sortType === 'date') {{
                    aVal = new Date(aVal);
                    bVal = new Date(bVal);
                    comparison = aVal - bVal;
                }} else {{
                    comparison = aVal.localeCompare(bVal, 'zh-CN');
                }}
                
                return direction === 'asc' ? comparison : -comparison;
            }});
            
            // 重新插入排序后的行
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
            
            // 如果是隐患记录总览表格，需要重新应用分页和筛选
            if (table.id === 'allHazardsTable') {{
                applyFiltersAndPagination();
            }}
        }}
    </script>
</body>
</html>"""


if __name__ == '__main__':
    from data_generator import HazardDataGenerator
    
    generator = HazardDataGenerator()
    df = generator.generate_all_data()
    
    dashboard = DashboardGenerator(df)
    dashboard.generate_html_report()

