"""
Risk Analyzer
功能：风险分析逻辑，包括帕累托分析、整改率计算、趋势分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
from pathlib import Path


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self, df: pd.DataFrame, config_path: str = None):
        """
        初始化分析器
        
        Args:
            df: 隐患数据DataFrame
            config_path: areas.json配置文件路径
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'data' / 'areas.json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def get_summary_stats(self, period: str = 'all') -> Dict:
        """
        获取汇总统计
        
        Args:
            period: 'all', 'week', 'month', 'year'
            
        Returns:
            Dict: 汇总统计数据
        """
        df = self._filter_by_period(period)
        
        total = len(df)
        rectified = len(df[df['status'] == '已整改'])
        in_progress = len(df[df['status'] == '整改中'])
        overdue = len(df[df['status'] == '逾期'])
        
        high_risk = len(df[df['risk_level'] == 'High'])
        medium_risk = len(df[df['risk_level'] == 'Medium'])
        low_risk = len(df[df['risk_level'] == 'Low'])
        
        # 计算整改率
        rectify_rate = rectified / total * 100 if total > 0 else 0
        
        # 平均整改天数
        rectified_df = df[df['rectify_days'].notna()]
        avg_rectify_days = rectified_df['rectify_days'].mean() if len(rectified_df) > 0 else 0
        
        return {
            'total': total,
            'rectified': rectified,
            'in_progress': in_progress,
            'overdue': overdue,
            'rectify_rate': round(rectify_rate, 1),
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'avg_rectify_days': round(avg_rectify_days, 1),
            'avg_risk_score': round(df['risk_score'].mean(), 2) if total > 0 else 0
        }
    
    def _filter_by_period(self, period: str) -> pd.DataFrame:
        """按时间段筛选数据"""
        today = datetime.now()
        
        if period == 'week':
            start = today - timedelta(days=7)
        elif period == 'month':
            start = today - timedelta(days=30)
        elif period == 'year':
            start = today - timedelta(days=365)
        else:
            return self.df
        
        return self.df[self.df['date'] >= start]
    
    def get_pareto_analysis(self, by: str = 'hazard_type') -> pd.DataFrame:
        """
        帕累托分析
        
        Args:
            by: 分析维度 ('hazard_type', 'hazard_category', 'area_name')
            
        Returns:
            DataFrame: 包含数量、百分比、累计百分比
        """
        counts = self.df[by].value_counts().reset_index()
        counts.columns = [by, 'count']
        
        total = counts['count'].sum()
        counts['percentage'] = (counts['count'] / total * 100).round(1)
        counts['cumulative_percentage'] = counts['percentage'].cumsum().round(1)
        
        # 标记80%分界线
        counts['is_vital_few'] = counts['cumulative_percentage'] <= 80
        
        return counts
    
    def get_area_risk_matrix(self) -> pd.DataFrame:
        """
        获取区域-隐患类型风险矩阵
        
        Returns:
            DataFrame: 行为区域，列为隐患大类，值为加权风险分
        """
        # 创建透视表（数量）
        pivot_count = pd.pivot_table(
            self.df,
            values='hazard_id',
            index='area_name',
            columns='hazard_category',
            aggfunc='count',
            fill_value=0
        )
        
        # 创建透视表（平均风险分）
        pivot_risk = pd.pivot_table(
            self.df,
            values='risk_score',
            index='area_name',
            columns='hazard_category',
            aggfunc='mean',
            fill_value=0
        )
        
        # 加权风险 = 数量 × 平均风险分 / 10
        weighted_risk = (pivot_count * pivot_risk / 10).round(1)
        
        return {
            'count_matrix': pivot_count,
            'risk_matrix': pivot_risk.round(2),
            'weighted_matrix': weighted_risk
        }
    
    def get_weekly_trend(self, weeks: int = 12) -> pd.DataFrame:
        """
        获取周度趋势数据
        
        Args:
            weeks: 显示最近多少周
            
        Returns:
            DataFrame: 周度统计
        """
        df = self.df.copy()
        
        # 创建年周排序键
        df['year'] = df['date'].dt.year
        df['week_num'] = df['date'].dt.isocalendar().week
        df['year_week'] = df['date'].dt.strftime('%Y-W%V')
        df['sort_key'] = df['year'] * 100 + df['week_num']
        
        weekly = df.groupby(['sort_key', 'year_week']).agg({
            'hazard_id': 'count',
            'risk_score': 'mean',
            'status': lambda x: (x == '已整改').sum()
        }).reset_index()
        
        weekly.columns = ['sort_key', 'week', 'total', 'avg_risk', 'rectified']
        weekly = weekly.sort_values('sort_key').tail(weeks)
        weekly['rectify_rate'] = (weekly['rectified'] / weekly['total'] * 100).round(1)
        weekly['avg_risk'] = weekly['avg_risk'].round(2)
        
        return weekly[['week', 'total', 'avg_risk', 'rectified', 'rectify_rate']]
    
    def get_monthly_trend(self, months: int = 12) -> pd.DataFrame:
        """
        获取月度趋势数据
        
        Args:
            months: 显示最近多少个月
            
        Returns:
            DataFrame: 月度统计
        """
        df = self.df.copy()
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        monthly = df.groupby('year_month').agg({
            'hazard_id': 'count',
            'risk_score': 'mean',
            'status': lambda x: (x == '已整改').sum()
        }).reset_index()
        
        monthly.columns = ['month', 'total', 'avg_risk', 'rectified']
        monthly = monthly.sort_values('month').tail(months)
        monthly['rectify_rate'] = (monthly['rectified'] / monthly['total'] * 100).round(1)
        monthly['avg_risk'] = monthly['avg_risk'].round(2)
        
        return monthly
    
    def get_quarterly_trend(self) -> pd.DataFrame:
        """
        获取季度趋势数据
        
        Returns:
            DataFrame: 季度统计（隐患总数、整改数、整改率）
            注：整改率统计的是截至目前每个季度发现的隐患的整改状态
        """
        df = self.df.copy()
        
        # 创建季度标签
        df['year'] = df['date'].dt.year
        df['quarter'] = df['date'].dt.quarter
        df['year_quarter'] = df['year'].astype(str) + 'Q' + df['quarter'].astype(str)
        df['sort_key'] = df['year'] * 10 + df['quarter']
        
        # 按季度分组，统计截至目前的整改状态
        quarterly = df.groupby(['sort_key', 'year_quarter']).agg({
            'hazard_id': 'count',
            'risk_score': 'mean',
            'status': lambda x: (x == '已整改').sum()  # 统计当前状态为"已整改"的数量
        }).reset_index()
        
        quarterly.columns = ['sort_key', 'quarter', 'total', 'avg_risk', 'rectified']
        quarterly = quarterly.sort_values('sort_key')
        
        # 计算整改率（截至目前的整改情况）
        quarterly['rectify_rate'] = (quarterly['rectified'] / quarterly['total'] * 100).round(1)
        quarterly['avg_risk'] = quarterly['avg_risk'].round(2)
        
        # 过滤掉数据量太少的季度（通常是当前季度刚开始，数据不足）
        # 如果最后一个季度的隐患数量少于平均值的20%，则排除
        if len(quarterly) > 1:
            avg_total = quarterly['total'].mean()
            last_quarter_total = quarterly.iloc[-1]['total']
            
            # 如果最后一个季度数据量太少（< 平均值的20%），则排除
            if last_quarter_total < avg_total * 0.2:
                quarterly = quarterly.iloc[:-1]
        
        return quarterly[['quarter', 'total', 'avg_risk', 'rectified', 'rectify_rate']]
    
    def get_area_summary(self, days: int = None) -> pd.DataFrame:
        """
        获取各区域汇总数据
        
        Args:
            days: 分析最近N天的数据，None表示全部
        
        Returns:
            DataFrame: 各区域的隐患数量、风险分数、整改率等
        """
        df = self.df.copy()
        
        # 如果指定天数，筛选数据
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= cutoff_date]
        
        area_stats = df.groupby('area_name').agg({
            'hazard_id': 'count',
            'risk_score': ['mean', 'sum'],
            'status': lambda x: (x == '已整改').sum()
        }).reset_index()
        
        area_stats.columns = ['area_name', 'total', 'avg_risk', 'total_risk', 'rectified']
        area_stats['rectify_rate'] = (area_stats['rectified'] / area_stats['total'] * 100).round(1)
        area_stats['avg_risk'] = area_stats['avg_risk'].round(2)
        
        # 添加风险等级分布
        high_counts = df[df['risk_level'] == 'High'].groupby('area_name').size()
        area_stats['high_risk_count'] = area_stats['area_name'].map(high_counts).fillna(0).astype(int)
        
        # 按风险排序
        area_stats = area_stats.sort_values('total_risk', ascending=False)
        
        return area_stats
    
    def get_3d_surface_data(self) -> Dict:
        """
        获取3D曲面图数据
        X轴: 区域
        Y轴: 时间（月份）
        Z轴: 风险分数总和
        
        Returns:
            Dict: 包含x, y, z数据
        """
        df = self.df.copy()
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        # 创建透视表
        pivot = pd.pivot_table(
            df,
            values='risk_score',
            index='area_name',
            columns='year_month',
            aggfunc='sum',
            fill_value=0
        )
        
        # 准备3D数据
        areas = pivot.index.tolist()
        months = pivot.columns.tolist()
        z_data = pivot.values.tolist()
        
        return {
            'x': months,  # 时间轴
            'y': areas,   # 区域轴
            'z': z_data,  # 风险分数
            'x_label': '时间',
            'y_label': '区域',
            'z_label': '累计风险分'
        }
    
    def get_3d_category_surface_data(self) -> Dict:
        """
        获取3D曲面图数据（区域 × 隐患类型）
        
        Returns:
            Dict: 包含x, y, z数据
        """
        # 创建透视表
        pivot = pd.pivot_table(
            self.df,
            values='risk_score',
            index='area_name',
            columns='hazard_category',
            aggfunc='sum',
            fill_value=0
        )
        
        areas = pivot.index.tolist()
        categories = pivot.columns.tolist()
        z_data = pivot.values.tolist()
        
        return {
            'x': categories,
            'y': areas,
            'z': z_data,
            'x_label': '隐患类型',
            'y_label': '区域',
            'z_label': '累计风险分'
        }
    
    def get_recent_alerts(self, days: int = 7, top_n: int = 20) -> pd.DataFrame:
        """
        获取近7天新发现的中高风险隐患（预警）
        用于：关注新发现的、需要立即处理的隐患
        
        Args:
            days: 最近多少天
            top_n: 返回前N条
            
        Returns:
            DataFrame: 近期中高风险隐患列表
        """
        today = datetime.now()
        start = today - timedelta(days=days)
        
        # 近7天发现的中高风险隐患
        recent = self.df[
            (self.df['date'] >= start) & 
            (self.df['risk_level'].isin(['High', 'Medium']))
        ].copy()
        
        # 按风险等级和分数排序（High优先，然后按分数）
        level_order = {'High': 0, 'Medium': 1}
        recent['level_order'] = recent['risk_level'].map(level_order)
        recent = recent.sort_values(
            ['level_order', 'risk_score', 'date'], 
            ascending=[True, False, False]
        )
        
        return recent.head(top_n)[[
            'date', 'area_name', 'hazard_category', 'hazard_type',
            'description', 'risk_level', 'risk_score', 'status'
        ]]
    
    def get_overdue_hazards(self, min_days: int = 7, top_n: int = 50) -> pd.DataFrame:
        """
        获取超过指定天数仍未整改的隐患（滞留跟踪）
        用于：跟踪长期未整改的隐患，督促整改
        
        Args:
            min_days: 最少滞留天数（默认7天）
            top_n: 返回前N条
            
        Returns:
            DataFrame: 滞留未整改隐患列表
        """
        today = datetime.now()
        cutoff_date = today - timedelta(days=min_days)
        
        # 筛选：未整改 且 发现日期超过min_days天
        df = self.df[
            (self.df['status'] != '已整改') & 
            (self.df['date'] < cutoff_date)
        ].copy()
        
        # 计算滞留天数
        df['overdue_days'] = (today - df['date']).dt.days
        
        # 按风险等级和滞留天数排序（High > Medium > Low，然后按滞留天数）
        level_order = {'High': 0, 'Medium': 1, 'Low': 2}
        df['level_order'] = df['risk_level'].map(level_order)
        df = df.sort_values(
            ['level_order', 'overdue_days'], 
            ascending=[True, False]
        )
        
        return df.head(top_n)[[
            'hazard_id', 'date', 'area_name', 'hazard_type',
            'risk_level', 'risk_score', 'overdue_days', 'responsible', 'status'
        ]]
    
    def get_all_hazards_with_status(self, top_n: int = None) -> pd.DataFrame:
        """
        获取所有隐患记录（按状态和日期排序）
        用于：展示可筛选的完整隐患列表
        
        Args:
            top_n: 返回前N条，None表示返回全部
            
        Returns:
            DataFrame: 所有隐患记录
        """
        df = self.df.copy()
        today = datetime.now()
        
        # 计算处理天数
        df['overdue_days'] = (today - df['date']).dt.days
        
        # 按状态和日期排序（已整改优先，最新的在前）
        status_order = {'已整改': 0, '整改中': 1, '逾期': 2}
        level_order = {'High': 0, 'Medium': 1, 'Low': 2}
        
        df['status_order'] = df['status'].map(status_order).fillna(3)
        df['level_order'] = df['risk_level'].map(level_order)
        
        df = df.sort_values(
            ['status_order', 'date'],
            ascending=[True, False]  # 已整改优先，日期新的在前
        )
        
        result = df[[
            'hazard_id', 'date', 'area_name', 'hazard_type',
            'risk_level', 'risk_score', 'overdue_days', 'responsible', 'status'
        ]]
        
        if top_n:
            return result.head(top_n)
        return result


if __name__ == '__main__':
    # 测试
    from data_generator import HazardDataGenerator
    
    generator = HazardDataGenerator()
    df = generator.generate_all_data()
    
    analyzer = RiskAnalyzer(df)
    
    print("\n=== 汇总统计 ===")
    stats = analyzer.get_summary_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n=== 帕累托分析 (隐患类型) ===")
    pareto = analyzer.get_pareto_analysis('hazard_type')
    print(pareto.head(10).to_string())
    
    print("\n=== 区域风险排名 ===")
    area_summary = analyzer.get_area_summary()
    print(area_summary.to_string())

