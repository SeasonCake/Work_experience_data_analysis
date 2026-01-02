"""
可视化仪表板模块 (Dashboard)
功能：生成交互式HTML报告，展示大型工业项目（化工/制造行业）
      从在建到运行的完整演进过程
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[WARN] plotly未安装，将使用基础HTML模式")


class Dashboard:
    """可视化仪表板生成器"""
    
    # 颜色配置
    COLORS = {
        # 用工阶段（区域）
        '在建区域': '#3498db',
        '运行区域': '#2ecc71',
        # 兼容旧名称
        '建设期': '#3498db',
        '运行期': '#2ecc71',
        # 建设期工种大类
        '土建类': '#3498db',
        '安装类': '#9b59b6',
        '特种施工': '#e74c3c',
        '辅助施工': '#95a5a6',
        # 运行期工种大类
        '生产操作': '#2ecc71',
        '设备运维': '#e67e22',
        '特种设备': '#e74c3c',
        '安全环保': '#1abc9c',
        '质量检测': '#f39c12',
        # 状态颜色
        '在场': '#27ae60',
        '已退场': '#7f8c8d',
        '入场': '#27ae60',
        '退场': '#e74c3c',
        # 证书状态
        '已过期': '#e74c3c',
        '7天内到期': '#e67e22',
        '30天内到期': '#f39c12',
        '90天内到期': '#3498db',
        '正常': '#27ae60',
    }
    
    def __init__(self, df_contractors, df_training=None, df_blacklist=None, 
                 df_entry_exit=None, check_results=None):
        """初始化仪表板"""
        self.df = df_contractors.copy()
        self.df_training = df_training
        self.df_blacklist = df_blacklist
        self.df_entry_exit = df_entry_exit
        self.check_results = check_results
        self.today = datetime.now().date()
        self.report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self._preprocess_data()
    
    def _preprocess_data(self):
        """预处理数据"""
        # 日期转换
        for col in ['有效期至', '入场日期', '退场日期', '发证日期', '培训日期']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce').dt.date
        
        # 计算证书到期天数
        if '有效期至' in self.df.columns:
            self.df['距离到期天数'] = self.df['有效期至'].apply(
                lambda x: (x - self.today).days if pd.notna(x) else None
            )
            
            def categorize_expiry(days):
                if days is None:
                    return '无证书要求'
                elif days < 0:
                    return '已过期'
                elif days <= 7:
                    return '7天内到期'
                elif days <= 30:
                    return '30天内到期'
                elif days <= 90:
                    return '90天内到期'
                return '正常'
            
            self.df['到期状态'] = self.df['距离到期天数'].apply(categorize_expiry)
    
    def get_daily_summary(self):
        """获取每日监控摘要"""
        # 只统计在场人员
        df_active = self.df[self.df['人员状态'] == '在场']
        
        # 兼容新旧术语
        construction_count = len(df_active[df_active['用工阶段'].isin(['建设期', '在建区域'])])
        operation_count = len(df_active[df_active['用工阶段'].isin(['运行期', '运行区域'])])
        
        summary = {
            '报告时间': self.report_time,
            '人员总数': len(self.df),
            '当前在场': len(df_active),
            '已退场': len(self.df[self.df['人员状态'] == '已退场']),
            '在建区域人员': construction_count,
            '运行区域人员': operation_count,
            '特种作业人员': len(df_active[df_active['是否特种作业'] == True]),
        }
        
        # 证书到期统计（特种作业人员）
        special_active = df_active[df_active['是否特种作业'] == True]
        if '到期状态' in special_active.columns:
            expiry_stats = special_active['到期状态'].value_counts().to_dict()
            summary['已过期'] = expiry_stats.get('已过期', 0)
            summary['7天内到期'] = expiry_stats.get('7天内到期', 0)
            summary['30天内到期'] = expiry_stats.get('30天内到期', 0)
            summary['证书正常'] = expiry_stats.get('正常', 0)
        
        return summary
    
    def get_critical_personnel(self, days_threshold=7):
        """获取紧急预警人员（已到期或即将到期）"""
        mask = (
            (self.df['人员状态'] == '在场') &
            (self.df['是否特种作业'] == True) &
            (self.df['距离到期天数'].notna()) &
            (self.df['距离到期天数'] <= days_threshold)
        )
        
        critical_df = self.df[mask].copy()
        critical_df = critical_df.sort_values('距离到期天数')
        
        columns = ['人员ID', '姓名', '联系电话', '所属单位', '工种', '工种大类',
                   '证书类型', '有效期至', '距离到期天数', '到期状态']
        return critical_df[[c for c in columns if c in critical_df.columns]]
    
    def get_phase_evolution_data(self):
        """获取项目阶段演进数据"""
        phases = ['2023-H1', '2023-H2', '2024-H1', '2024-H2', '2025-H1', '2025-H2', '2026-H1']
        
        evolution_data = []
        for phase in phases:
            phase_df = self.df[self.df['入场阶段'] == phase]
            if len(phase_df) == 0:
                continue
            
            # 兼容新旧术语
            construction = len(phase_df[phase_df['用工阶段'].isin(['建设期', '在建区域'])])
            operation = len(phase_df[phase_df['用工阶段'].isin(['运行期', '运行区域'])])
            
            evolution_data.append({
                '阶段': phase,
                '在建区域人员': construction,
                '运行区域人员': operation,
                '总人数': construction + operation
            })
        
        return pd.DataFrame(evolution_data)
    
    def get_work_category_distribution(self, current_only=True):
        """获取工种大类分布"""
        if current_only:
            df_work = self.df[self.df['人员状态'] == '在场']
        else:
            df_work = self.df
        
        dist = df_work.groupby(['工种大类', '用工阶段']).size().reset_index(name='人数')
        return dist
    
    def get_entry_exit_trend(self):
        """获取进退场趋势数据"""
        if self.df_entry_exit is None:
            return None
        
        df_ee = self.df_entry_exit.copy()
        df_ee['日期'] = pd.to_datetime(df_ee['日期'])
        df_ee['月份'] = df_ee['日期'].dt.to_period('M')
        
        # 按月份和类型统计
        monthly = df_ee.groupby(['月份', '类型', '用工阶段']).size().reset_index(name='人数')
        monthly['月份'] = monthly['月份'].astype(str)
        
        return monthly
    
    def get_training_trend_by_phase(self):
        """获取培训趋势数据（按阶段）"""
        if self.df_training is None:
            return None
        
        df_train = self.df_training.copy()
        df_train['培训日期'] = pd.to_datetime(df_train['培训日期'])
        df_train['季度'] = df_train['培训日期'].dt.to_period('Q')
        
        # 确保"是否合格"是布尔类型（从Excel读取可能变成字符串或其他类型）
        if df_train['是否合格'].dtype == object:
            df_train['是否合格'] = df_train['是否合格'].map({'True': True, 'False': False, True: True, False: False})
        df_train['是否合格'] = df_train['是否合格'].astype(bool)
        
        # 按季度统计 - 分开计算避免lambda问题
        count_df = df_train.groupby(['季度', '用工阶段']).size().reset_index(name='培训人次')
        
        # 平均成绩
        score_df = df_train.groupby(['季度', '用工阶段'])['培训成绩'].mean().reset_index(name='平均成绩')
        
        # 合格率 (是否合格的True占比 * 100)
        pass_df = df_train.groupby(['季度', '用工阶段'])['是否合格'].mean().reset_index(name='合格率')
        pass_df['合格率'] = pass_df['合格率'] * 100  # 转为百分比
        
        # 合并
        quarterly = count_df.merge(score_df, on=['季度', '用工阶段']).merge(pass_df, on=['季度', '用工阶段'])
        quarterly['季度'] = quarterly['季度'].astype(str)
        
        # 调试输出 - 详细显示每个季度的数据
        print(f"\n[DEBUG] 培训趋势数据:")
        print(f"  总培训记录: {len(df_train)}")
        print(f"  季度数: {quarterly['季度'].nunique()}")
        print(f"\n  按季度详细数据:")
        for _, row in quarterly.sort_values('季度').iterrows():
            print(f"    {row['季度']} | {row['用工阶段']:<8} | 人次: {row['培训人次']:>4} | 合格率: {row['合格率']:.1f}%")
        
        return quarterly
    
    def generate_html_report(self, output_path='outputs/dashboard.html'):
        """生成完整的HTML仪表板报告"""
        summary = self.get_daily_summary()
        critical_personnel = self.get_critical_personnel(days_threshold=7)
        personnel_30days = self.get_critical_personnel(days_threshold=30)
        phase_evolution = self.get_phase_evolution_data()
        work_dist = self.get_work_category_distribution()
        entry_exit_trend = self.get_entry_exit_trend()
        training_trend = self.get_training_trend_by_phase()
        
        if PLOTLY_AVAILABLE:
            html_content = self._generate_plotly_report(
                summary, critical_personnel, personnel_30days,
                phase_evolution, work_dist, entry_exit_trend, training_trend
            )
        else:
            html_content = self._generate_basic_report(summary, critical_personnel)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] 可视化仪表板已生成: {output_path}")
        return output_path
    
    def _generate_plotly_report(self, summary, critical_personnel, personnel_30days,
                                 phase_evolution, work_dist, entry_exit_trend, training_trend):
        """使用Plotly生成交互式报告"""
        current_date = datetime.now().strftime('%Y.%m.%d')
        
        # ========== 图表1: 综合趋势图（培训人次 + 退场趋势）==========
        # 准备退场数据
        exit_by_quarter = None
        if entry_exit_trend is not None and len(entry_exit_trend) > 0:
            exit_data = entry_exit_trend[entry_exit_trend['类型'] == '退场'].copy()
            if len(exit_data) > 0:
                exit_data['季度'] = pd.to_datetime(exit_data['月份']).dt.to_period('Q').astype(str)
                exit_by_quarter = exit_data.groupby(['季度', '用工阶段'])['人数'].sum().reset_index()
        
        # 培训数据处理
        if training_trend is not None and len(training_trend) > 0:
            all_quarters = sorted(training_trend['季度'].unique())
            
            construction_data = training_trend[training_trend['用工阶段'] == '在建区域'].set_index('季度')
            operation_data = training_trend[training_trend['用工阶段'] == '运行区域'].set_index('季度')
            
            construction_counts = [construction_data.loc[q, '培训人次'] if q in construction_data.index else 0 for q in all_quarters]
            operation_counts = [operation_data.loc[q, '培训人次'] if q in operation_data.index else 0 for q in all_quarters]
            construction_rates = [construction_data.loc[q, '合格率'] if q in construction_data.index else 0 for q in all_quarters]
            operation_rates = [operation_data.loc[q, '合格率'] if q in operation_data.index else 0 for q in all_quarters]
            
            # 退场数据按季度
            exit_construction = []
            exit_operation = []
            if exit_by_quarter is not None:
                exit_construct_df = exit_by_quarter[exit_by_quarter['用工阶段'] == '在建区域'].set_index('季度')
                exit_operate_df = exit_by_quarter[exit_by_quarter['用工阶段'] == '运行区域'].set_index('季度')
                exit_construction = [exit_construct_df.loc[q, '人数'] if q in exit_construct_df.index else 0 for q in all_quarters]
                exit_operation = [exit_operate_df.loc[q, '人数'] if q in exit_operate_df.index else 0 for q in all_quarters]
            else:
                exit_construction = [0] * len(all_quarters)
                exit_operation = [0] * len(all_quarters)
            
            # 创建3列子图：培训人次、退场人次、合格率
            fig_combined = make_subplots(
                rows=1, cols=3,
                subplot_titles=('培训人次趋势', '退场人次趋势', '培训合格率'),
                horizontal_spacing=0.08
            )
            
            # 培训人次
            fig_combined.add_trace(go.Bar(x=all_quarters, y=construction_counts, name='在建区域', marker_color='#3498db', text=construction_counts, textposition='outside'), row=1, col=1)
            fig_combined.add_trace(go.Bar(x=all_quarters, y=operation_counts, name='运行区域', marker_color='#2ecc71', text=operation_counts, textposition='outside'), row=1, col=1)
            
            # 退场人次
            fig_combined.add_trace(go.Bar(x=all_quarters, y=exit_construction, name='在建区域', marker_color='#3498db', text=exit_construction, textposition='outside', showlegend=False, opacity=0.7), row=1, col=2)
            fig_combined.add_trace(go.Bar(x=all_quarters, y=exit_operation, name='运行区域', marker_color='#2ecc71', text=exit_operation, textposition='outside', showlegend=False, opacity=0.7), row=1, col=2)
            
            # 合格率
            fig_combined.add_trace(go.Bar(x=all_quarters, y=construction_rates, name='在建区域', marker_color='#3498db', text=[f'{r:.1f}%' for r in construction_rates], textposition='outside', showlegend=False), row=1, col=3)
            fig_combined.add_trace(go.Bar(x=all_quarters, y=operation_rates, name='运行区域', marker_color='#2ecc71', text=[f'{r:.1f}%' for r in operation_rates], textposition='outside', showlegend=False), row=1, col=3)
            
            fig_combined.update_layout(
                height=450,
                showlegend=True,
                barmode='group',
                legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center')
            )
            fig_combined.update_xaxes(tickangle=45, categoryorder='array', categoryarray=all_quarters)
            fig_combined.update_yaxes(title_text="培训人次", row=1, col=1)
            fig_combined.update_yaxes(title_text="退场人数", row=1, col=2)
            fig_combined.update_yaxes(title_text="合格率(%)", row=1, col=3, range=[90, 100])
            
            combined_chart = fig_combined.to_html(full_html=False, include_plotlyjs=False)
        else:
            combined_chart = "<p>暂无趋势数据</p>"
        
        # ========== 图表2: 工种分布（环形图 + 矩形树图）==========
        if len(work_dist) > 0:
            category_summary = work_dist.groupby('工种大类')['人数'].sum().reset_index()
            category_summary = category_summary.sort_values('人数', ascending=False)
            
            # 定义更丰富的颜色
            treemap_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
                              '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']
            color_map = {cat: treemap_colors[i % len(treemap_colors)] for i, cat in enumerate(category_summary['工种大类'])}
            colors = [color_map.get(cat, '#95a5a6') for cat in category_summary['工种大类']]
            
            # 计算总人数
            total_workers = category_summary['人数'].sum()
            
            # 环形图（饼图）- 优化布局防止文字重叠
            fig_pie = go.Figure(data=[go.Pie(
                labels=category_summary['工种大类'].tolist(),
                values=category_summary['人数'].tolist(),
                marker=dict(colors=colors),
                textinfo='value+percent',
                textposition='inside',
                hole=0.55,
                textfont=dict(size=10, color='white'),
                insidetextorientation='horizontal',
                sort=False
            )])
            fig_pie.update_layout(
                title=dict(text='工种分布', font=dict(size=14), y=0.98),
                height=420,
                showlegend=True,
                legend=dict(orientation='h', y=-0.08, x=0.5, xanchor='center', font=dict(size=10)),
                annotations=[dict(text=f'<b>{total_workers}</b><br>人', x=0.5, y=0.5, font_size=22, showarrow=False)],
                margin=dict(t=40, b=70, l=20, r=20)
            )
            work_pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)
            
            # 矩形树图 (Treemap) - 类似股票热力图
            fig_treemap = go.Figure(go.Treemap(
                labels=category_summary['工种大类'].tolist(),
                values=category_summary['人数'].tolist(),
                parents=[''] * len(category_summary),
                marker=dict(
                    colors=colors,
                    line=dict(width=2, color='#1a1a2e')
                ),
                textinfo='label+value+percent entry',
                textfont=dict(size=13, color='white'),
                hovertemplate='<b>%{label}</b><br>人数: %{value}<br>占比: %{percentEntry:.1%}<extra></extra>'
            ))
            fig_treemap.update_layout(
                title=dict(text='矩形树图', font=dict(size=14), y=0.98),
                height=420,
                margin=dict(t=40, l=10, r=10, b=10)
            )
            work_treemap_chart = fig_treemap.to_html(full_html=False, include_plotlyjs=False)
        else:
            work_pie_chart = "<p>暂无工种数据</p>"
            work_treemap_chart = "<p>暂无工种数据</p>"
        
        # ========== 图表3: 特种作业人员证书状态（饼图 + 表格）==========
        special_df = self.df[(self.df['是否特种作业'] == True) & (self.df['人员状态'] == '在场')].copy()
        special_total = len(special_df)
        
        if '到期状态' in special_df.columns and special_total > 0:
            expiry_dist = special_df['到期状态'].value_counts().reset_index()
            expiry_dist.columns = ['状态', '人数']
            
            # 确保所有状态都存在
            all_status = ['已过期', '7天内到期', '30天内到期', '90天内到期', '正常']
            for status in all_status:
                if status not in expiry_dist['状态'].values:
                    expiry_dist = pd.concat([expiry_dist, pd.DataFrame({'状态': [status], '人数': [0]})], ignore_index=True)
            
            order = ['已过期', '7天内到期', '30天内到期', '90天内到期', '正常']
            expiry_dist['排序'] = expiry_dist['状态'].apply(lambda x: order.index(x) if x in order else 99)
            expiry_dist = expiry_dist.sort_values('排序').drop('排序', axis=1)
            
            # 过滤掉人数为0的状态（饼图不显示0）
            expiry_dist_pie = expiry_dist[expiry_dist['人数'] > 0]
            
            expiry_colors_map = {
                '已过期': '#e74c3c',
                '7天内到期': '#e67e22', 
                '30天内到期': '#f39c12',
                '90天内到期': '#3498db',
                '正常': '#27ae60'
            }
            expiry_colors = [expiry_colors_map.get(s, '#95a5a6') for s in expiry_dist_pie['状态']]
            
            # 饼图显示证书状态分布 - 优化布局防止文字重叠
            fig_expiry = go.Figure(data=[go.Pie(
                labels=expiry_dist_pie['状态'].tolist(),
                values=expiry_dist_pie['人数'].tolist(),
                marker=dict(colors=expiry_colors),
                textinfo='value+percent',
                textposition='inside',
                hole=0.5,
                textfont=dict(size=11, color='white'),
                insidetextorientation='horizontal'
            )])
            fig_expiry.update_layout(
                title=dict(text=f'证书状态分布', font=dict(size=14), y=0.98),
                height=420,
                showlegend=True,
                legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center', font=dict(size=11)),
                annotations=[dict(text=f'<b>{special_total}</b><br>人', x=0.5, y=0.5, font_size=24, showarrow=False)],
                margin=dict(t=40, b=60, l=20, r=20)
            )
            expiry_chart = fig_expiry.to_html(full_html=False, include_plotlyjs=False)
            
            # 生成持证人员表格（按到期状态分组）
            special_df = special_df.sort_values('距离到期天数')
            cert_personnel_table = self._generate_cert_personnel_table(special_df)
        else:
            expiry_chart = "<p>暂无证书数据</p>"
            cert_personnel_table = "<p>暂无特种作业人员</p>"
            special_total = 0
        
        # ========== 生成紧急预警表格 ==========
        critical_table = self._generate_personnel_table(critical_personnel) if len(critical_personnel) > 0 else "<p class='success'>暂无紧急预警人员</p>"
        full_table = self._generate_personnel_table(personnel_30days) if len(personnel_30days) > 0 else "<p class='success'>暂无30天内到期人员</p>"
        
        # ========== 组装HTML ==========
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>承包商人员准入监控仪表板</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
        
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #3498db;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header .subtitle {{
            color: #bdc3c7;
            font-size: 1.1em;
        }}
        .header .timestamp {{ color: #95a5a6; margin-top: 10px; }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .card.critical {{ background: linear-gradient(135deg, #e74c3c, #c0392b); animation: pulse 2s infinite; }}
        .card.warning {{ background: linear-gradient(135deg, #e67e22, #d35400); }}
        .card.info {{ background: linear-gradient(135deg, #3498db, #2980b9); }}
        .card.success {{ background: linear-gradient(135deg, #27ae60, #1e8449); }}
        .card.construction {{ background: linear-gradient(135deg, #3498db, #2980b9); }}
        .card.operation {{ background: linear-gradient(135deg, #2ecc71, #27ae60); }}
        .card .number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }}
        .card .label {{ font-size: 0.95em; opacity: 0.9; }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }}
            70% {{ box-shadow: 0 0 0 15px rgba(231, 76, 60, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }}
        }}
        
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            animation: fadeInUp 0.5s ease-out;
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .section-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 4px solid #3498db;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title.alert {{ border-left-color: #e74c3c; color: #e74c3c; }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .chart-container {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }}
        .chart-container:hover {{
            background: rgba(255,255,255,0.05);
            border-color: rgba(52, 152, 219, 0.2);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 12px 10px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{ background: rgba(52, 152, 219, 0.3); font-weight: 600; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        tr.expired {{ background: rgba(231, 76, 60, 0.2); }}
        tr.urgent {{ background: rgba(230, 126, 34, 0.2); }}
        
        .status-badge {{
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-expired {{ background: #e74c3c; }}
        .status-urgent {{ background: #e67e22; }}
        .status-warning {{ background: #f39c12; color: #000; }}
        .status-normal {{ background: #27ae60; }}
        
        .success {{ color: #27ae60; text-align: center; padding: 20px; font-size: 1.1em; }}
        
        .filter-bar {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .filter-bar input {{
            padding: 12px 18px;
            border: 2px solid rgba(52, 152, 219, 0.3);
            border-radius: 25px;
            background: rgba(255,255,255,0.08);
            color: #fff;
            font-size: 0.95em;
            width: 320px;
            transition: all 0.3s ease;
        }}
        .filter-bar input:focus {{
            outline: none;
            border-color: #3498db;
            background: rgba(255,255,255,0.12);
            box-shadow: 0 0 15px rgba(52, 152, 219, 0.3);
        }}
        .filter-bar input::placeholder {{ color: rgba(255,255,255,0.4); }}
        
        .legend-item {{
            display: inline-flex;
            align-items: center;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 8px;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            .summary-cards {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        html {{ scroll-behavior: smooth; }}
        
        .footer {{
            text-align: center;
            padding: 30px 0;
            margin-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.5);
            font-size: 0.9em;
        }}
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        /* 表格行hover效果增强 */
        tbody tr {{
            transition: background 0.2s ease;
        }}
        tbody tr:hover {{
            background: rgba(52, 152, 219, 0.1) !important;
        }}
        
        /* 滚动条美化 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(52, 152, 219, 0.5);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(52, 152, 219, 0.7);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>承包商人员准入监控仪表板</h1>
            <p class="subtitle">大型工业项目 | 化工/制造行业 | 项目周期: 2023-2026</p>
            <p class="timestamp">报告生成时间: {self.report_time}</p>
        </header>
        
        <!-- 摘要卡片 -->
        <section class="summary-cards">
            <div class="card info">
                <div class="number">{summary['人员总数']}</div>
                <div class="label">累计人员</div>
            </div>
            <div class="card" style="background: linear-gradient(135deg, #27ae60, #1e8449);">
                <div class="number">{summary['当前在场']}</div>
                <div class="label">当前在场 (截至{current_date})</div>
            </div>
            <div class="card" style="background: linear-gradient(135deg, #3498db, #2980b9);">
                <div class="number">{summary['在建区域人员']}</div>
                <div class="label">在建区域</div>
            </div>
            <div class="card" style="background: linear-gradient(135deg, #2ecc71, #27ae60);">
                <div class="number">{summary['运行区域人员']}</div>
                <div class="label">运行区域</div>
            </div>
            <div class="card critical">
                <div class="number">{summary.get('已过期', 0)}</div>
                <div class="label">证书已过期</div>
            </div>
            <div class="card warning">
                <div class="number">{summary.get('7天内到期', 0)}</div>
                <div class="label">7天内到期</div>
            </div>
            <div class="card" style="background: linear-gradient(135deg, #f39c12, #d68910);">
                <div class="number">{summary.get('30天内到期', 0)}</div>
                <div class="label">30天内到期</div>
            </div>
            <div class="card info">
                <div class="number">{summary.get('特种作业人员', 0)}</div>
                <div class="label">特种作业人员</div>
            </div>
        </section>
        
        <!-- 紧急预警 -->
        <section class="section">
            <h2 class="section-title alert">紧急预警 - 需立即处理 ({len(critical_personnel)}人)</h2>
            {critical_table}
        </section>
        
        <!-- 综合趋势图：培训人次 + 退场趋势 + 合格率 -->
        <section class="section">
            <h2 class="section-title">人员培训与流动趋势 (按季度)</h2>
            <div class="legend-item">
                <span class="legend-color" style="background: #3498db;"></span>
                <span>在建区域</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #2ecc71;"></span>
                <span>运行区域</span>
            </div>
            {combined_chart}
        </section>
        
        <!-- 工种分布：环形图 + 矩形树图（左右布局）-->
        <section class="section">
            <h2 class="section-title">当前在场人员工种分布</h2>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div class="chart-container" style="flex: 0 0 480px; min-width: 400px;">
                    {work_pie_chart}
                </div>
                <div class="chart-container" style="flex: 1; min-width: 500px;">
                    {work_treemap_chart}
                </div>
            </div>
        </section>
        
        <!-- 特种作业人员证书状态 -->
        <section class="section">
            <h2 class="section-title">特种作业人员证书状态 (在场{special_total}人)</h2>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div class="chart-container" style="flex: 0 0 500px; min-width: 400px;">
                    {expiry_chart}
                </div>
                <div class="chart-container" style="flex: 1; min-width: 400px; max-height: 550px; overflow-y: auto;">
                    <h3 style="margin-bottom: 15px; color: #3498db;">持证人员详情</h3>
                    <div class="filter-bar" style="margin-bottom: 10px;">
                        <input type="text" id="certSearchInput" placeholder="搜索姓名、工种、证书类型..." onkeyup="filterCertTable()">
                    </div>
                    <div id="certPersonnelTable">
                        {cert_personnel_table}
                    </div>
                </div>
            </div>
        </section>
        
        <!-- 完整预警列表 -->
        <section class="section">
            <h2 class="section-title">完整预警列表 - 30天内到期 ({len(personnel_30days)}人)</h2>
            <div class="filter-bar">
                <input type="text" id="searchInput" placeholder="搜索姓名、工种、单位..." onkeyup="filterTable()">
            </div>
            {full_table}
        </section>
        
        <!-- 页脚 -->
        <footer class="footer">
            <p>承包商人员准入自动化监控系统 | 数据更新时间: {self.report_time}</p>
            <p style="margin-top: 8px; font-size: 0.85em;">
                © 2024-2026 Contractor Access Automation · Safety Management | 
                <a href="#">使用指南</a> · 
                <a href="#">问题反馈</a>
            </p>
        </footer>
    </div>
    
    <script>
        function filterTable() {{
            var input = document.getElementById("searchInput");
            var filter = input.value.toLowerCase();
            var tables = document.querySelectorAll("section:last-of-type table tbody tr");
            tables.forEach(function(row) {{
                var text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? "" : "none";
            }});
        }}
        
        function filterCertTable() {{
            var input = document.getElementById("certSearchInput");
            var filter = input.value.toLowerCase();
            var container = document.getElementById("certPersonnelTable");
            var groups = container.querySelectorAll(".cert-group");
            
            groups.forEach(function(group) {{
                var rows = group.querySelectorAll("table tbody tr");
                var hasVisibleRows = false;
                
                rows.forEach(function(row) {{
                    var text = row.textContent.toLowerCase();
                    if (filter === "" || text.includes(filter)) {{
                        row.style.display = "";
                        hasVisibleRows = true;
                    }} else {{
                        row.style.display = "none";
                    }}
                }});
                
                // 如果该分组没有匹配的行，隐藏整个分组
                group.style.display = hasVisibleRows ? "" : "none";
            }});
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _generate_personnel_table(self, df):
        """生成人员表格HTML"""
        if len(df) == 0:
            return "<p>暂无数据</p>"
        
        rows_html = ""
        for _, row in df.iterrows():
            days = row.get('距离到期天数', None)
            status = row.get('到期状态', '')
            
            row_class = ""
            if days is not None:
                if days < 0:
                    row_class = "expired"
                elif days <= 7:
                    row_class = "urgent"
            
            badge_class = "status-normal"
            if status == '已过期':
                badge_class = "status-expired"
            elif status == '7天内到期':
                badge_class = "status-urgent"
            elif status == '30天内到期':
                badge_class = "status-warning"
            
            days_display = "N/A"
            if days is not None:
                if days < 0:
                    days_display = f"已过期{abs(int(days))}天"
                else:
                    days_display = f"{int(days)}天"
            
            rows_html += f"""
            <tr class="{row_class}">
                <td>{row.get('人员ID', '')}</td>
                <td><strong>{row.get('姓名', '')}</strong></td>
                <td>{row.get('联系电话', '')}</td>
                <td>{row.get('所属单位', '')[:15]}...</td>
                <td>{row.get('工种', '')}</td>
                <td>{row.get('工种大类', '')}</td>
                <td>{row.get('证书类型', '')}</td>
                <td>{row.get('有效期至', '')}</td>
                <td><strong>{days_display}</strong></td>
                <td><span class="status-badge {badge_class}">{status}</span></td>
            </tr>
            """
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>人员ID</th>
                    <th>姓名</th>
                    <th>联系电话</th>
                    <th>所属单位</th>
                    <th>工种</th>
                    <th>大类</th>
                    <th>证书类型</th>
                    <th>有效期至</th>
                    <th>剩余</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        """
    
    def _generate_cert_personnel_table(self, df):
        """生成持证人员表格HTML（按状态分组，可折叠）"""
        if len(df) == 0:
            return "<p>暂无数据</p>"
        
        # 按状态分组
        status_groups = {
            '已过期': df[df['到期状态'] == '已过期'],
            '7天内到期': df[df['到期状态'] == '7天内到期'],
            '30天内到期': df[df['到期状态'] == '30天内到期'],
            '90天内到期': df[df['到期状态'] == '90天内到期'],
            '正常': df[df['到期状态'] == '正常']
        }
        
        status_colors = {
            '已过期': '#e74c3c',
            '7天内到期': '#e67e22',
            '30天内到期': '#f39c12',
            '90天内到期': '#3498db',
            '正常': '#27ae60'
        }
        
        html_parts = []
        for status_name, group_df in status_groups.items():
            if len(group_df) == 0:
                continue
            
            color = status_colors.get(status_name, '#95a5a6')
            rows_html = ""
            
            # 只显示前20条，避免表格过长
            show_df = group_df.head(20)
            for _, row in show_df.iterrows():
                days = row.get('距离到期天数', None)
                days_display = "N/A"
                if days is not None:
                    if days < 0:
                        days_display = f"已过期{abs(int(days))}天"
                    else:
                        days_display = f"{int(days)}天"
                
                rows_html += f"""
                <tr>
                    <td>{row.get('姓名', '')}</td>
                    <td>{row.get('工种', '')}</td>
                    <td>{row.get('证书类型', '')}</td>
                    <td>{row.get('有效期至', '')}</td>
                    <td><strong>{days_display}</strong></td>
                    <td>{row.get('所属单位', '')[:12]}...</td>
                </tr>
                """
            
            more_text = f"（显示前20条，共{len(group_df)}条）" if len(group_df) > 20 else ""
            
            html_parts.append(f"""
            <div class="cert-group" style="margin-bottom: 20px;">
                <h4 style="color: {color}; margin-bottom: 10px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                    <span style="display: inline-block; width: 12px; height: 12px; background: {color}; border-radius: 3px; margin-right: 8px;"></span>
                    {status_name}: {len(group_df)}人 {more_text}
                </h4>
                <table style="font-size: 0.85em;">
                    <thead>
                        <tr>
                            <th>姓名</th>
                            <th>工种</th>
                            <th>证书类型</th>
                            <th>有效期至</th>
                            <th>剩余</th>
                            <th>所属单位</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            """)
        
        return "".join(html_parts)
    
    def _generate_basic_report(self, summary, critical_personnel):
        """生成基础HTML报告（无需Plotly）"""
        critical_table = self._generate_personnel_table(critical_personnel) if len(critical_personnel) > 0 else "<p class='success'>暂无紧急预警人员</p>"
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>承包商人员准入监控仪表板</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #3498db; }}
        .card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 10px; display: inline-block; text-align: center; min-width: 150px; }}
        .card.critical {{ background: #e74c3c; }}
        .card .number {{ font-size: 2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; }}
        th {{ background: rgba(52, 152, 219, 0.3); }}
        .success {{ color: #27ae60; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>承包商人员准入监控仪表板</h1>
        <p style="text-align: center; color: #95a5a6;">报告时间: {self.report_time}</p>
        <div style="text-align: center;">
            <div class="card"><div class="number">{summary['当前在场']}</div><div>当前在场</div></div>
            <div class="card"><div class="number">{summary['建设期人员']}</div><div>建设期</div></div>
            <div class="card"><div class="number">{summary['运行期人员']}</div><div>运行期</div></div>
            <div class="card critical"><div class="number">{summary.get('已过期', 0)}</div><div>已过期</div></div>
        </div>
        <h2 style="color: #e74c3c; margin-top: 30px;">紧急预警 ({len(critical_personnel)}人)</h2>
        {critical_table}
    </div>
</body>
</html>
"""
    
    def print_daily_summary(self):
        """打印每日监控摘要"""
        summary = self.get_daily_summary()
        critical = self.get_critical_personnel(days_threshold=7)
        
        print("\n" + "="*70)
        print("          每日监控摘要 - " + self.report_time)
        print("="*70)
        
        print(f"\n[人员总览]")
        print(f"  累计人员: {summary['人员总数']} | 当前在场: {summary['当前在场']} | 已退场: {summary['已退场']}")
        print(f"  在建区域: {summary['在建区域人员']} 人 | 运行区域: {summary['运行区域人员']} 人")
        print(f"  特种作业人员: {summary['特种作业人员']} 人")
        
        print(f"\n[证书预警] (特种作业人员)")
        if summary.get('已过期', 0) > 0:
            print(f"  [!!!] 已过期: {summary['已过期']} 人 - 需立即处理!")
        if summary.get('7天内到期', 0) > 0:
            print(f"  [!!]  7天内到期: {summary['7天内到期']} 人 - 紧急!")
        if summary.get('30天内到期', 0) > 0:
            print(f"  [!]   30天内到期: {summary['30天内到期']} 人")
        print(f"  [OK]  证书正常: {summary.get('证书正常', 0)} 人")
        
        if len(critical) > 0:
            print(f"\n[紧急预警名单] 共 {len(critical)} 人:")
            print("-"*70)
            for _, row in critical.head(15).iterrows():
                days = row.get('距离到期天数', 0)
                if days < 0:
                    status = f"已过期{abs(int(days))}天"
                else:
                    status = f"{int(days)}天后到期"
                print(f"  {row['姓名']:<8} | {row['工种']:<10} | {row.get('工种大类', ''):<8} | {status}")
            if len(critical) > 15:
                print(f"  ... 还有 {len(critical)-15} 人，详见HTML报告")
        
        print("="*70)


def main():
    """测试函数"""
    print("Dashboard模块已加载")
    print("请通过main.py运行完整流程")


if __name__ == "__main__":
    main()
