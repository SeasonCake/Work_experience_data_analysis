"""
Visualizer Module
功能：生成各类可视化图表，包括3D Surface Plot
"""

import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, List


class HazardVisualizer:
    """隐患可视化器"""
    
    # 颜色方案
    COLORS = {
        'primary': '#3498db',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#9b59b6',
        'dark': '#1a1a2e',
        'light': '#ecf0f1',
        'High': '#e74c3c',
        'Medium': '#f39c12',
        'Low': '#2ecc71'
    }
    
    # 区域颜色
    AREA_COLORS = [
        '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#2ecc71',
        '#1abc9c', '#34495e', '#95a5a6', '#e67e22'
    ]
    
    def __init__(self, config_path: str = None):
        """初始化"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'data' / 'areas.json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def create_factory_heatmap(self, area_risks: Dict[str, float]) -> str:
        """
        创建厂区风险热力图（多边形布局）- 美化版
        
        Args:
            area_risks: {area_code: risk_score}
            
        Returns:
            str: Plotly HTML
        """
        fig = go.Figure()
        
        # 绘制厂区外边界 - 添加阴影效果
        boundary = self.config['factory_boundary']
        boundary_x = [p[0] for p in boundary] + [boundary[0][0]]
        boundary_y = [p[1] for p in boundary] + [boundary[0][1]]
        
        # 阴影层
        fig.add_trace(go.Scatter(
            x=[x + 0.05 for x in boundary_x],
            y=[y - 0.05 for y in boundary_y],
            mode='lines',
            line=dict(color='rgba(0,0,0,0.3)', width=8),
            fill='toself',
            fillcolor='rgba(0,0,0,0.15)',
            name='阴影',
            hoverinfo='skip',
            showlegend=False
        ))
        
        # 主边界
        fig.add_trace(go.Scatter(
            x=boundary_x,
            y=boundary_y,
            mode='lines',
            line=dict(color='#2c3e50', width=4),
            fill='toself',
            fillcolor='rgba(52, 73, 94, 0.4)',
            name='厂区边界',
            hoverinfo='skip',
            showlegend=False
        ))
        
        # 计算风险颜色映射
        max_risk = max(area_risks.values()) if area_risks else 1
        min_risk = min(area_risks.values()) if area_risks else 0
        risk_values = list(area_risks.values())
        
        def get_risk_color(risk: float) -> tuple:
            """根据风险值返回颜色和归一化值"""
            if max_risk == min_risk:
                normalized = 0.5
            else:
                normalized = (risk - min_risk) / (max_risk - min_risk)
            
            # 绿色 -> 黄色 -> 橙色 -> 红色（更丰富的颜色过渡）
            if normalized < 0.33:
                # 绿色到黄绿
                t = normalized / 0.33
                r = int(46 + (158 - 46) * t)
                g = int(204 + (193 - 204) * t)
                b = int(113 + (45 - 113) * t)
            elif normalized < 0.66:
                # 黄绿到橙色
                t = (normalized - 0.33) / 0.33
                r = int(158 + (243 - 158) * t)
                g = int(193 + (156 - 193) * t)
                b = int(45 + (18 - 45) * t)
            else:
                # 橙色到红色
                t = (normalized - 0.66) / 0.34
                r = int(243 + (192 - 243) * t)
                g = int(156 + (57 - 156) * t)
                b = int(18 + (43 - 18) * t)
            
            return f'rgb({r},{g},{b})', normalized
        
        # 按风险值排序绘制区域（低风险先绘制，高风险后绘制以便显示在上层）
        sorted_areas = sorted(self.config['areas'], 
                             key=lambda a: area_risks.get(a['code'], 0))
        
        for area in sorted_areas:
            code = area['code']
            name = area['name']
            polygon = area['polygon']
            center = area['center']
            risk = area_risks.get(code, 0)
            
            poly_x = [p[0] for p in polygon] + [polygon[0][0]]
            poly_y = [p[1] for p in polygon] + [polygon[0][1]]
            
            color, normalized = get_risk_color(risk)
            
            # 区域阴影
            fig.add_trace(go.Scatter(
                x=[x + 0.02 for x in poly_x],
                y=[y - 0.02 for y in poly_y],
                mode='lines',
                line=dict(color='rgba(0,0,0,0.2)', width=1),
                fill='toself',
                fillcolor='rgba(0,0,0,0.1)',
                hoverinfo='skip',
                showlegend=False
            ))
            
            # 区域填充 - 添加边框高亮
            border_color = '#1a1a2e' if normalized > 0.5 else '#34495e'
            fig.add_trace(go.Scatter(
                x=poly_x,
                y=poly_y,
                mode='lines',
                line=dict(color=border_color, width=3),
                fill='toself',
                fillcolor=color,
                name=name,
                text=f"<b>{name}</b><br>累计风险分: {risk:.0f}<br>风险等级: {'高' if normalized > 0.66 else '中' if normalized > 0.33 else '低'}",
                hoverinfo='text',
                hoverlabel=dict(
                    bgcolor='rgba(0,0,0,0.8)',
                    font_size=13,
                    font_color='white'
                ),
                showlegend=False
            ))
            
            # 区域标签 - 美化样式（统一圆角卡片风格）
            text_color = 'white' if normalized > 0.4 else '#1a1a2e'
            bg_color = 'rgba(30,30,50,0.85)' if normalized > 0.4 else 'rgba(255,255,255,0.92)'
            border_col = 'rgba(255,255,255,0.3)' if normalized > 0.4 else 'rgba(0,0,0,0.2)'
            
            fig.add_annotation(
                x=center[0],
                y=center[1],
                text=f"<b>{name}</b><br><span style='font-size:18px; font-weight:bold'>{risk:.0f}</span>",
                showarrow=False,
                font=dict(size=11, color=text_color, family='Microsoft YaHei'),
                bgcolor=bg_color,
                bordercolor=border_col,
                borderwidth=2,
                borderpad=8,
                opacity=0.98
            )
        
        # 计算统计信息
        max_risk_val = max(risk_values) if risk_values else 0
        min_risk_val = min(risk_values) if risk_values else 0
        avg_risk_val = sum(risk_values) / len(risk_values) if risk_values else 0
        
        fig.update_layout(
            title=dict(
                text=f'厂区风险热力图（近30天累计风险分 · 最高{max_risk_val:.0f}分）',
                font=dict(size=16, color='#3498db', family='Microsoft YaHei'),
                x=0.5,
                xanchor='center'
            ),
            showlegend=False,
            xaxis=dict(visible=False, scaleanchor='y'),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=520,
            margin=dict(l=30, r=30, t=60, b=30),
            hoverlabel=dict(
                bgcolor='rgba(0,0,0,0.8)',
                font_size=12
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_pareto_chart(self, pareto_data: pd.DataFrame, 
                           by_column: str = 'hazard_type') -> str:
        """
        创建帕累托图（垂直柱状图 + 累计百分比曲线）
        
        Args:
            pareto_data: 帕累托分析数据（已按数量降序排列）
            by_column: 分析维度列名
            
        Returns:
            str: Plotly HTML
        """
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 确保数据按降序排列（数量从大到小）
        pareto_data = pareto_data.sort_values('count', ascending=False).reset_index(drop=True)
        
        # 获取类型列表（保持降序顺序）
        categories = pareto_data[by_column].tolist()
        
        # 柱状图颜色 - 关键少数用红色，其他用灰色
        colors = ['#e74c3c' if row['is_vital_few'] else '#3498db' 
                  for _, row in pareto_data.iterrows()]
        
        # 柱状图 - 垂直柱状图
        fig.add_trace(
            go.Bar(
                x=categories,
                y=pareto_data['count'].tolist(),
                name='隐患数量',
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=1)
                ),
                text=pareto_data['count'].tolist(),
                textposition='outside',
                textfont=dict(size=11, color='#2c3e50'),
                hovertemplate='<b>%{x}</b><br>数量: %{y}<br>占比: %{customdata:.1f}%<extra></extra>',
                customdata=pareto_data['percentage'].tolist(),
                width=0.7  # 柱子宽度
            ),
            secondary_y=False
        )
        
        # 累计百分比曲线
        fig.add_trace(
            go.Scatter(
                x=categories,
                y=pareto_data['cumulative_percentage'].tolist(),
                name='累计百分比',
                mode='lines+markers',
                line=dict(color='#2c3e50', width=3),
                marker=dict(size=8, symbol='diamond', color='#2c3e50'),
                hovertemplate='<b>%{x}</b><br>累计占比: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )
        
        # 80%参考线
        fig.add_hline(
            y=80, line_dash="dash", line_color="#e74c3c", line_width=2,
            annotation_text="80%关键线（红色为关键少数）", 
            annotation_position="top right",
            annotation_font_size=11,
            annotation_font_color="#e74c3c",
            secondary_y=True
        )
        
        # 计算关键少数的数量
        vital_few_count = pareto_data['is_vital_few'].sum()
        total_count = len(pareto_data)
        
        fig.update_layout(
            title=dict(
                text=f'隐患类型帕累托分析（红色={vital_few_count}类贡献80%问题）',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='隐患类型',
                tickangle=45,
                tickfont=dict(size=10),
                categoryorder='array',  # 强制按传入顺序排列
                categoryarray=categories,  # 明确指定顺序
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='隐患数量',
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.2)'
            ),
            yaxis2=dict(
                title='累计百分比 (%)', 
                range=[0, 105],
                gridcolor='rgba(0,0,0,0)'  # 隐藏次Y轴网格线
            ),
            legend=dict(
                orientation='h', 
                yanchor='bottom', 
                y=1.02, 
                x=0.5, 
                xanchor='center'
            ),
            bargap=0.15,  # 柱子间距
            height=500,
            margin=dict(l=60, r=60, b=150, t=80),
            plot_bgcolor='rgba(248,249,250,1)',  # 浅灰背景
            paper_bgcolor='white'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_heatmap_matrix(self, matrix_data: pd.DataFrame, 
                              title: str = '区域-隐患类型热力图') -> str:
        """
        创建热力图矩阵
        
        Args:
            matrix_data: 透视表数据
            title: 图表标题
            
        Returns:
            str: Plotly HTML
        """
        # 确保数据是数值类型
        z_data = matrix_data.values.astype(float)
        x_labels = matrix_data.columns.tolist()
        y_labels = matrix_data.index.tolist()
        
        # 创建文本标注矩阵
        text_data = [[f'{val:.0f}' for val in row] for row in z_data]
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale='RdYlGn_r',
            text=text_data,
            texttemplate='%{text}',
            textfont=dict(size=11, color='white'),
            hovertemplate='区域: %{y}<br>类型: %{x}<br>数值: %{z:.1f}<extra></extra>',
            showscale=True,
            colorbar=dict(title=dict(text='风险值', side='right'))
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(
                tickangle=45, 
                title='隐患类型',
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title='区域',
                tickfont=dict(size=10)
            ),
            height=420,
            margin=dict(l=100, r=50, b=120, t=50)
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_trend_chart(self, trend_data: pd.DataFrame, 
                          x_col: str = 'week',
                          target_rate: float = 85) -> str:
        """
        创建趋势图（垂直柱状图 + 整改率曲线）
        
        Args:
            trend_data: 趋势数据
            x_col: X轴列名
            target_rate: 目标整改率
            
        Returns:
            str: Plotly HTML
        """
        # 根据x_col判断时间粒度
        time_label_map = {
            'week': '周度',
            'month': '月度',
            'quarter': '季度'
        }
        time_label = time_label_map.get(x_col, '')
        
        # 确保数据按时间顺序排列
        trend_data = trend_data.copy()
        
        # 获取时间列表（保持时间顺序）
        time_categories = trend_data[x_col].tolist()
        total_values = trend_data['total'].tolist()
        rate_values = trend_data['rectify_rate'].tolist()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 隐患数量柱状图 - 垂直柱状图
        fig.add_trace(
            go.Bar(
                x=time_categories,
                y=total_values,
                name='隐患总数',
                marker=dict(
                    color='rgba(52, 152, 219, 0.8)',
                    line=dict(color='rgba(52, 152, 219, 1)', width=1)
                ),
                text=total_values,
                textposition='outside',
                textfont=dict(size=11, color='#2c3e50'),
                hovertemplate='<b>%{x}</b><br>隐患数: %{y}<extra></extra>',
                width=0.6
            ),
            secondary_y=False
        )
        
        # 整改率曲线
        fig.add_trace(
            go.Scatter(
                x=time_categories,
                y=rate_values,
                name='整改率',
                mode='lines+markers',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=10, color='#2ecc71', symbol='circle'),
                text=[f'{r:.1f}%' for r in rate_values],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>整改率: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )
        
        # 目标线
        fig.add_hline(
            y=target_rate, line_dash="dash", line_color="#e74c3c", line_width=2,
            annotation_text=f"目标: {target_rate}%",
            annotation_position="right",
            annotation_font_color="#e74c3c",
            secondary_y=True
        )
        
        # 计算整改率的合理范围
        min_rate = min(rate_values) if rate_values else 0
        max_rate = max(rate_values) if rate_values else 100
        
        # 设置Y轴范围
        if min_rate > 80:
            y2_range = [70, 105]
        elif min_rate > 50:
            y2_range = [40, 105]
        else:
            y2_range = [0, 105]
        
        # 计算隐患数量的合理范围
        max_total = max(total_values) if total_values else 100
        y1_max = int(max_total * 1.3)  # 留出空间显示数字
        
        fig.update_layout(
            title=dict(
                text=f'隐患整改率趋势（{time_label}统计）', 
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='时间', 
                tickangle=45,
                categoryorder='array',  # 强制按传入顺序排列
                categoryarray=time_categories,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='隐患数量',
                range=[0, y1_max],
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis2=dict(
                title='整改率 (%)', 
                range=y2_range,
                gridcolor='rgba(0,0,0,0)'  # 隐藏次Y轴网格线
            ),
            legend=dict(
                orientation='h', 
                yanchor='bottom', 
                y=1.02,
                x=0.5,
                xanchor='center'
            ),
            bargap=0.2,
            height=450,
            margin=dict(l=60, r=60, b=100, t=80),
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='white'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_3d_surface_plot(self, surface_data: Dict, 
                               title: str = '风险响应面图') -> str:
        """
        创建3D曲面图
        
        Args:
            surface_data: 包含x, y, z数据的字典
            title: 图表标题
            
        Returns:
            str: Plotly HTML
        """
        x = surface_data['x']  # 时间/类型
        y = surface_data['y']  # 区域
        z = surface_data['z']  # 风险分数
        
        x_label = surface_data.get('x_label', 'X')
        y_label = surface_data.get('y_label', 'Y')
        z_label = surface_data.get('z_label', 'Z')
        
        fig = go.Figure(data=[go.Surface(
            z=z,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(
                title=dict(text='风险分', side='right'),
                thickness=20,
                len=0.7
            ),
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True
                )
            ),
            opacity=0.95
        )])
        
        # 创建索引用于轴标签映射
        x_idx = list(range(len(x)))
        y_idx = list(range(len(y)))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            scene=dict(
                xaxis=dict(
                    title=dict(text=x_label, font=dict(size=12)),
                    ticktext=x,
                    tickvals=x_idx,
                    tickangle=45,
                    tickfont=dict(size=9),
                    gridcolor='rgba(0,0,0,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(248,249,250,0.8)'
                ),
                yaxis=dict(
                    title=dict(text=y_label, font=dict(size=12)),
                    ticktext=y,
                    tickvals=y_idx,
                    tickfont=dict(size=10),
                    gridcolor='rgba(0,0,0,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(248,249,250,0.8)'
                ),
                zaxis=dict(
                    title=dict(text=z_label, font=dict(size=12)),
                    gridcolor='rgba(0,0,0,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(248,249,250,0.8)'
                ),
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.0)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1.5, y=1, z=0.7)
            ),
            height=550,
            margin=dict(l=10, r=10, t=60, b=10),
            paper_bgcolor='white'
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_risk_level_pie(self, level_counts: Dict[str, int]) -> str:
        """
        创建风险等级饼图
        
        Args:
            level_counts: {level: count}
            
        Returns:
            str: Plotly HTML
        """
        labels = list(level_counts.keys())
        values = list(level_counts.values())
        colors = [self.COLORS.get(l, '#95a5a6') for l in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textfont=dict(size=12),
            hovertemplate='%{label}<br>数量: %{value}<br>占比: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='风险等级分布', font=dict(size=16)),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.1),
            height=350,
            margin=dict(l=20, r=20, t=50, b=50)
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_area_bar_chart(self, area_summary: pd.DataFrame) -> str:
        """
        创建区域对比柱状图
        
        Args:
            area_summary: 区域汇总数据
            
        Returns:
            str: Plotly HTML
        """
        fig = go.Figure()
        
        # 按风险分排序
        area_summary = area_summary.sort_values('total_risk', ascending=True)
        
        # 水平柱状图
        fig.add_trace(go.Bar(
            y=area_summary['area_name'],
            x=area_summary['total'],
            name='隐患总数',
            orientation='h',
            marker_color='rgba(52, 152, 219, 0.7)',
            text=area_summary['total'],
            textposition='outside',
            hovertemplate='%{y}<br>隐患数: %{x}<extra></extra>'
        ))
        
        # 高风险数量
        fig.add_trace(go.Bar(
            y=area_summary['area_name'],
            x=area_summary['high_risk_count'],
            name='高风险数',
            orientation='h',
            marker_color='rgba(231, 76, 60, 0.8)',
            text=area_summary['high_risk_count'],
            textposition='inside',
            hovertemplate='%{y}<br>高风险: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text='各区域隐患对比', font=dict(size=16)),
            barmode='overlay',
            xaxis=dict(title='数量'),
            yaxis=dict(title=''),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            height=400,
            margin=dict(l=100)
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_category_treemap(self, df: pd.DataFrame, days: int = 90) -> str:
        """
        创建隐患类型矩形树图（最近N天数据）
        
        Args:
            df: 隐患数据
            days: 统计最近N天的数据
            
        Returns:
            str: Plotly HTML
        """
        from datetime import datetime, timedelta
        
        # 筛选最近N天数据
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        cutoff_date = datetime.now() - timedelta(days=days)
        df_filtered = df[df['date'] >= cutoff_date]
        
        if len(df_filtered) == 0:
            df_filtered = df  # 如果筛选后没数据，使用全部
        
        actual_days = (datetime.now() - df_filtered['date'].min()).days
        
        # 按大类和具体类型聚合
        type_agg = df_filtered.groupby(['hazard_category', 'hazard_type']).agg({
            'hazard_id': 'count',
            'risk_score': 'mean'
        }).reset_index()
        type_agg.columns = ['category', 'type', 'count', 'avg_risk']
        
        # 添加百分比信息
        total_count = type_agg['count'].sum()
        type_agg['percentage'] = (type_agg['count'] / total_count * 100).round(1)
        
        # 直接使用px.treemap
        fig = px.treemap(
            type_agg,
            path=['category', 'type'],
            values='count',
            color='avg_risk',
            color_continuous_scale='RdYlGn_r',
            color_continuous_midpoint=5,
            custom_data=['avg_risk', 'percentage']
        )
        
        fig.update_traces(
            textinfo='label+value+percent parent',
            textfont=dict(size=12),
            marker=dict(
                line=dict(width=2, color='white'),
                colorscale='RdYlGn_r'
            ),
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{customdata[1]:.1f}%<br>平均风险: %{customdata[0]:.1f}/10<extra></extra>',
            # 使用自动对比色，plotly会根据背景自动选择
            textposition='middle center'
        )
        
        fig.update_layout(
            title=dict(
                text=f'隐患类型分布（近{actual_days}天，共{total_count}条）',
                font=dict(size=16)
            ),
            height=450,
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_colorbar=dict(title='平均风险分')
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)


if __name__ == '__main__':
    # 测试
    from data_generator import HazardDataGenerator
    from risk_analyzer import RiskAnalyzer
    
    generator = HazardDataGenerator()
    df = generator.generate_all_data()
    
    analyzer = RiskAnalyzer(df)
    visualizer = HazardVisualizer()
    
    # 测试3D曲面图
    surface_data = analyzer.get_3d_surface_data()
    html = visualizer.create_3d_surface_plot(surface_data)
    print(f"3D Surface Plot HTML长度: {len(html)}")

