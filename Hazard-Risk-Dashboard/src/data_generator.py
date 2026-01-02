"""
Hazard Data Generator
功能：生成模拟隐患数据，支持权重分布和时间戳策略
"""

import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker('zh_CN')


class HazardDataGenerator:
    """隐患数据生成器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化生成器
        
        Args:
            config_path: areas.json配置文件路径
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'data' / 'areas.json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.areas = self.config['areas']
        self.hazard_types = self.config['hazard_types']
        self.risk_levels = self.config['risk_levels']
        
        # 构建区域权重（风险越高的区域，隐患越多）
        self.area_weights = [area['risk_weight'] for area in self.areas]
        total = sum(self.area_weights)
        self.area_weights = [w/total for w in self.area_weights]
        
        # 构建隐患类型权重
        self.type_weights = [self.hazard_types[t]['weight'] for t in self.hazard_types]
        
        # 构建风险等级权重
        self.level_weights = [self.risk_levels[l]['weight'] for l in self.risk_levels]
        
    def _get_week_number(self, date: datetime) -> int:
        """获取周次"""
        return date.isocalendar()[1]
    
    def _get_quarter(self, date: datetime) -> str:
        """获取季度"""
        return f"{date.year}Q{(date.month-1)//3 + 1}"
    
    def _weighted_choice(self, items: list, weights: list):
        """带权重的随机选择"""
        return random.choices(items, weights=weights, k=1)[0]
    
    def _generate_seasonal_factor(self, date: datetime) -> float:
        """
        生成季节性因子
        - 夏季（6-8月）：隐患多（高温、雷雨）
        - 冬季（12-2月）：隐患多（低温、用电取暖）
        - 春秋：相对平稳
        """
        month = date.month
        if month in [6, 7, 8]:  # 夏季
            return 1.3
        elif month in [12, 1, 2]:  # 冬季
            return 1.2
        elif month in [3, 4, 5]:  # 春季
            return 1.0
        else:  # 秋季
            return 0.9
    
    def _generate_rectify_date(self, discover_date: datetime, risk_level: str) -> datetime:
        """
        生成整改日期（符合实际业务逻辑）
        - High: 必须在1-3天内整改（100%整改率，超过7天未整改不合理）
        - Medium: 3-14天内整改（95%整改率）
        - Low: 7-30天内整改（85%整改率）
        """
        today = datetime.now()
        days_since = (today - discover_date).days
        
        # 高风险：必须整改，1-3天内完成
        if risk_level == 'High':
            if days_since >= 3:
                # 超过3天的高风险一定已整改
                days = random.randint(1, 3)
                return discover_date + timedelta(days=days)
            elif days_since >= 1:
                # 1-3天内，90%已整改
                if random.random() < 0.90:
                    days = random.randint(1, min(days_since, 3))
                    return discover_date + timedelta(days=days)
            # 当天发现的，暂未整改
            return None
        
        # 中风险：95%整改率，3-14天
        elif risk_level == 'Medium':
            if days_since >= 14:
                # 超过14天必须整改
                days = random.randint(3, 14)
                return discover_date + timedelta(days=days)
            elif days_since >= 3:
                if random.random() < 0.92:
                    days = random.randint(3, min(days_since, 14))
                    return discover_date + timedelta(days=days)
            return None
        
        # 低风险：85%整改率，7-30天
        else:
            if days_since >= 30:
                # 超过30天85%已整改
                if random.random() < 0.85:
                    days = random.randint(7, 30)
                    return discover_date + timedelta(days=days)
            elif days_since >= 7:
                if random.random() < 0.80:
                    days = random.randint(7, min(days_since, 30))
                    return discover_date + timedelta(days=days)
            return None
    
    def generate_historical_data(self, year: int = 2024) -> pd.DataFrame:
        """
        生成历史固定数据（整年）
        
        Args:
            year: 年份
            
        Returns:
            DataFrame: 隐患记录
        """
        print(f"\n正在生成 {year} 年历史数据...")
        
        data = []
        hazard_id = 1
        
        # 遍历全年每一天
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            # 计算当天的隐患数量（考虑季节因子）
            seasonal_factor = self._generate_seasonal_factor(current_date)
            
            # 工作日隐患更多
            weekday_factor = 1.0 if current_date.weekday() < 5 else 0.3
            
            # 基础日均隐患数：5-8条
            base_count = random.randint(5, 8)
            daily_count = int(base_count * seasonal_factor * weekday_factor)
            
            for _ in range(daily_count):
                # 选择区域（带权重）
                area = self._weighted_choice(self.areas, self.area_weights)
                
                # 选择隐患大类（带权重）
                hazard_category = self._weighted_choice(
                    list(self.hazard_types.keys()), 
                    self.type_weights
                )
                
                # 选择具体隐患类型（子类带权重）
                subtypes = self.hazard_types[hazard_category]['subtypes']
                subtype_weights = self.hazard_types[hazard_category]['subtype_weights']
                hazard_type = self._weighted_choice(subtypes, subtype_weights)
                
                # 选择风险等级（带权重，高风险区域High概率更大）
                area_risk_factor = area['risk_weight']
                adjusted_level_weights = self.level_weights.copy()
                if area_risk_factor > 1.0:
                    # 高风险区域增加High概率
                    adjusted_level_weights[0] *= area_risk_factor
                
                risk_level = self._weighted_choice(
                    list(self.risk_levels.keys()),
                    adjusted_level_weights
                )
                
                # 风险分数
                score_range = self.risk_levels[risk_level]['score_range']
                risk_score = random.randint(score_range[0], score_range[1])
                
                # 整改日期和状态（根据风险等级区分）
                rectify_date = self._generate_rectify_date(current_date, risk_level)
                days_since = (datetime.now() - current_date).days
                
                if rectify_date:
                    status = '已整改'
                elif risk_level == 'High':
                    # 高风险：超过3天必须已整改或整改中
                    if days_since > 3:
                        rectify_date = current_date + timedelta(days=random.randint(1, 3))
                        status = '已整改'
                    else:
                        status = '整改中'
                elif risk_level == 'Medium':
                    # 中风险：超过90天为逾期，14天内整改中，否则已整改
                    if days_since > 90:
                        # 超过90天，95%已整改，5%逾期
                        if random.random() < 0.95:
                            rectify_date = current_date + timedelta(days=random.randint(7, 30))
                            status = '已整改'
                        else:
                            status = '逾期'
                    elif days_since > 14:
                        if random.random() < 0.92:
                            rectify_date = current_date + timedelta(days=random.randint(3, 14))
                            status = '已整改'
                        else:
                            status = '整改中'
                    else:
                        status = '整改中'
                else:
                    # 低风险：超过90天为逾期，60天内整改
                    if days_since > 90:
                        # 超过90天，92%已整改，8%逾期
                        if random.random() < 0.92:
                            rectify_date = current_date + timedelta(days=random.randint(14, 60))
                            status = '已整改'
                        else:
                            status = '逾期'
                    elif days_since > 60:
                        if random.random() < 0.90:
                            rectify_date = current_date + timedelta(days=random.randint(14, 60))
                            status = '已整改'
                        else:
                            status = '整改中'
                    elif days_since > 30:
                        if random.random() < 0.75:
                            rectify_date = current_date + timedelta(days=random.randint(14, min(days_since, 60)))
                            status = '已整改'
                        else:
                            status = '整改中'
                    else:
                        status = '整改中'
                
                data.append({
                    'hazard_id': f"HZ-{year}-{hazard_id:05d}",
                    'date': current_date.strftime('%Y-%m-%d'),
                    'year': year,
                    'month': current_date.month,
                    'week': self._get_week_number(current_date),
                    'quarter': self._get_quarter(current_date),
                    'weekday': current_date.strftime('%A'),
                    'area_code': area['code'],
                    'area_name': area['name'],
                    'hazard_category': hazard_category,
                    'hazard_type': hazard_type,
                    'description': self._generate_description(hazard_type, area['name']),
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'status': status,
                    'rectify_date': rectify_date.strftime('%Y-%m-%d') if rectify_date else None,
                    'rectify_days': (rectify_date - current_date).days if rectify_date else None,
                    'responsible': fake.name(),
                    'inspector': fake.name(),
                    'data_type': 'historical'
                })
                
                hazard_id += 1
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(data)
        print(f"  [OK] 生成 {len(df)} 条历史隐患记录")
        
        return df
    
    def generate_recent_data(self, start_date: str = '2025-01-01', 
                            end_date: str = None) -> pd.DataFrame:
        """
        生成近期动态数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期，默认为今天
            
        Returns:
            DataFrame: 隐患记录
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
        
        print(f"\n正在生成近期数据 ({start_date} 至 {end.strftime('%Y-%m-%d')})...")
        
        data = []
        hazard_id = 1
        current_date = start
        
        while current_date <= end:
            seasonal_factor = self._generate_seasonal_factor(current_date)
            weekday_factor = 1.0 if current_date.weekday() < 5 else 0.3
            
            # 近期数据日均隐患数略高（体现加强检查）
            base_count = random.randint(6, 10)
            daily_count = int(base_count * seasonal_factor * weekday_factor)
            
            for _ in range(daily_count):
                area = self._weighted_choice(self.areas, self.area_weights)
                hazard_category = self._weighted_choice(
                    list(self.hazard_types.keys()), 
                    self.type_weights
                )
                subtypes = self.hazard_types[hazard_category]['subtypes']
                subtype_weights = self.hazard_types[hazard_category]['subtype_weights']
                hazard_type = self._weighted_choice(subtypes, subtype_weights)
                
                area_risk_factor = area['risk_weight']
                adjusted_level_weights = self.level_weights.copy()
                if area_risk_factor > 1.0:
                    adjusted_level_weights[0] *= area_risk_factor
                
                risk_level = self._weighted_choice(
                    list(self.risk_levels.keys()),
                    adjusted_level_weights
                )
                
                score_range = self.risk_levels[risk_level]['score_range']
                risk_score = random.randint(score_range[0], score_range[1])
                
                # 整改日期和状态（根据风险等级区分）
                rectify_date = self._generate_rectify_date(current_date, risk_level)
                days_since = (datetime.now() - current_date).days
                
                if rectify_date:
                    status = '已整改'
                elif risk_level == 'High':
                    if days_since > 3:
                        rectify_date = current_date + timedelta(days=random.randint(1, 3))
                        status = '已整改'
                    else:
                        status = '整改中'
                elif risk_level == 'Medium':
                    # 中风险：超过90天为逾期
                    if days_since > 90:
                        if random.random() < 0.95:
                            rectify_date = current_date + timedelta(days=random.randint(7, 30))
                            status = '已整改'
                        else:
                            status = '逾期'
                    elif days_since > 14:
                        rectify_date = current_date + timedelta(days=random.randint(3, 14))
                        status = '已整改'
                    else:
                        status = '整改中'
                else:
                    # 低风险：超过90天为逾期，60天内整改
                    if days_since > 90:
                        if random.random() < 0.92:
                            rectify_date = current_date + timedelta(days=random.randint(14, 60))
                            status = '已整改'
                        else:
                            status = '逾期'
                    elif days_since > 60:
                        if random.random() < 0.88:
                            rectify_date = current_date + timedelta(days=random.randint(14, 60))
                            status = '已整改'
                        else:
                            status = '整改中'
                    elif days_since > 30:
                        if random.random() < 0.70:
                            rectify_date = current_date + timedelta(days=random.randint(14, min(days_since, 60)))
                            status = '已整改'
                        else:
                            status = '整改中'
                    else:
                        status = '整改中'
                
                data.append({
                    'hazard_id': f"HZ-{current_date.year}-R{hazard_id:05d}",
                    'date': current_date.strftime('%Y-%m-%d'),
                    'year': current_date.year,
                    'month': current_date.month,
                    'week': self._get_week_number(current_date),
                    'quarter': self._get_quarter(current_date),
                    'weekday': current_date.strftime('%A'),
                    'area_code': area['code'],
                    'area_name': area['name'],
                    'hazard_category': hazard_category,
                    'hazard_type': hazard_type,
                    'description': self._generate_description(hazard_type, area['name']),
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'status': status,
                    'rectify_date': rectify_date.strftime('%Y-%m-%d') if rectify_date else None,
                    'rectify_days': (rectify_date - current_date).days if rectify_date else None,
                    'responsible': fake.name(),
                    'inspector': fake.name(),
                    'data_type': 'recent'
                })
                
                hazard_id += 1
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(data)
        print(f"  [OK] 生成 {len(df)} 条近期隐患记录")
        
        return df
    
    def _generate_description(self, hazard_type: str, area_name: str) -> str:
        """生成隐患描述"""
        descriptions = {
            # 电气安全
            '临时用电': [
                f'{area_name}发现临时用电未办理审批手续',
                f'{area_name}临时电缆未架空，存在损坏风险',
                f'{area_name}临时配电箱未接地',
            ],
            '配电箱隐患': [
                f'{area_name}配电箱门未关闭上锁',
                f'{area_name}配电箱内堆放杂物',
                f'{area_name}配电箱警示标识缺失',
            ],
            '接地不良': [
                f'{area_name}设备接地线松动',
                f'{area_name}接地电阻超标',
            ],
            '线路老化': [
                f'{area_name}电缆绝缘层破损',
                f'{area_name}线路超负荷运行',
            ],
            '漏电保护失效': [
                f'{area_name}漏电保护器未定期检测',
                f'{area_name}漏电保护器跳闸后强行合闸',
            ],
            # 消防安全
            '灭火器过期': [
                f'{area_name}灭火器超过有效期',
                f'{area_name}灭火器压力不足',
            ],
            '消防通道堵塞': [
                f'{area_name}消防通道被物料占用',
                f'{area_name}安全出口被锁闭',
            ],
            '烟感故障': [
                f'{area_name}烟感探测器被遮挡',
                f'{area_name}烟感探测器故障未修复',
            ],
            '消防栓问题': [
                f'{area_name}消防栓箱内设备不全',
                f'{area_name}消防栓被遮挡',
            ],
            '应急照明故障': [
                f'{area_name}应急照明灯不亮',
                f'{area_name}疏散指示标志损坏',
            ],
            # 机械安全
            '防护罩缺失': [
                f'{area_name}传动部件防护罩缺失',
                f'{area_name}设备防护装置被拆除',
            ],
            '设备故障': [
                f'{area_name}设备异常振动未处理',
                f'{area_name}设备带病运行',
            ],
            '传动部件裸露': [
                f'{area_name}皮带轮无防护',
                f'{area_name}联轴器裸露',
            ],
            '紧急停止失效': [
                f'{area_name}急停按钮失效',
                f'{area_name}安全联锁被旁路',
            ],
            # 化学品安全
            '泄漏风险': [
                f'{area_name}管道法兰渗漏',
                f'{area_name}储罐液位超限',
            ],
            '标识缺失': [
                f'{area_name}化学品无安全标签',
                f'{area_name}管道标识不清',
            ],
            '存储不当': [
                f'{area_name}化学品未分类存放',
                f'{area_name}危化品超量存储',
            ],
            'MSDS缺失': [
                f'{area_name}未配备化学品安全技术说明书',
            ],
            '混存问题': [
                f'{area_name}酸碱类化学品混存',
                f'{area_name}氧化剂与还原剂混存',
            ],
            # 行走安全
            '地面湿滑': [
                f'{area_name}地面积水未及时清理',
                f'{area_name}油污导致地面湿滑',
            ],
            '通道障碍': [
                f'{area_name}通道被物料堆占',
                f'{area_name}安全通道宽度不足',
            ],
            '照明不足': [
                f'{area_name}照明灯损坏未更换',
                f'{area_name}照度不达标',
            ],
            '护栏缺失': [
                f'{area_name}平台护栏缺失',
                f'{area_name}踢脚板缺失',
            ],
            '台阶损坏': [
                f'{area_name}楼梯台阶破损',
                f'{area_name}台阶防滑条脱落',
            ],
            # 特种设备
            '压力容器超期': [
                f'{area_name}压力容器未按期检验',
                f'{area_name}安全阀未校验',
            ],
            '起重机械问题': [
                f'{area_name}行车限位器失效',
                f'{area_name}吊钩无防脱装置',
            ],
            '叉车违规': [
                f'{area_name}叉车超速行驶',
                f'{area_name}叉车载人违规',
            ],
            '锅炉隐患': [
                f'{area_name}锅炉水位计故障',
                f'{area_name}锅炉安全阀起跳压力偏差',
            ],
            # 个人防护
            'PPE佩戴不规范': [
                f'{area_name}作业人员未佩戴安全帽',
                f'{area_name}作业人员未佩戴护目镜',
                f'{area_name}作业人员未穿防护服',
            ],
            '防护用品缺失': [
                f'{area_name}防护用品配备不足',
                f'{area_name}专用防护用品未配备',
            ],
            '防护用品损坏': [
                f'{area_name}安全帽破损',
                f'{area_name}防护手套破损',
            ],
            # 作业安全
            '高处作业违规': [
                f'{area_name}高处作业未系安全带',
                f'{area_name}高处作业未设置警戒',
            ],
            '受限空间问题': [
                f'{area_name}受限空间作业未检测',
                f'{area_name}受限空间作业无监护人',
            ],
            '动火作业隐患': [
                f'{area_name}动火作业无审批',
                f'{area_name}动火点周围有易燃物',
            ],
            '吊装作业问题': [
                f'{area_name}吊装作业无指挥',
                f'{area_name}吊装区域无警戒',
            ],
        }
        
        if hazard_type in descriptions:
            return random.choice(descriptions[hazard_type])
        else:
            return f'{area_name}发现{hazard_type}隐患'
    
    def generate_all_data(self) -> pd.DataFrame:
        """
        生成所有数据（历史 + 近期）
        
        Returns:
            DataFrame: 合并后的隐患数据
        """
        # 生成2024年历史数据
        df_historical = self.generate_historical_data(year=2024)
        
        # 生成2025.01至今的近期数据
        df_recent = self.generate_recent_data(start_date='2025-01-01')
        
        # 合并数据
        df_all = pd.concat([df_historical, df_recent], ignore_index=True)
        
        # 按日期排序
        df_all['date'] = pd.to_datetime(df_all['date'])
        df_all = df_all.sort_values('date').reset_index(drop=True)
        
        print(f"\n[总计] 共生成 {len(df_all)} 条隐患记录")
        print(f"  历史数据: {len(df_historical)} 条 (2024年)")
        print(f"  近期数据: {len(df_recent)} 条 (2025年至今)")
        
        return df_all
    
    def save_data(self, df: pd.DataFrame, output_dir: str = None):
        """保存数据到CSV和Excel"""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'data'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存CSV
        csv_path = output_dir / 'hazards.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  [OK] 数据已保存: {csv_path}")
        
        # 保存Excel
        xlsx_path = output_dir / 'hazards.xlsx'
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        print(f"  [OK] 数据已保存: {xlsx_path}")
        
        return csv_path, xlsx_path


def print_data_summary(df: pd.DataFrame):
    """打印数据摘要"""
    print("\n" + "="*60)
    print("数据摘要")
    print("="*60)
    
    print(f"\n[时间范围]")
    print(f"  起始: {df['date'].min()}")
    print(f"  结束: {df['date'].max()}")
    
    print(f"\n[按区域统计]")
    area_stats = df.groupby('area_name').agg({
        'hazard_id': 'count',
        'risk_score': 'mean'
    }).round(2)
    area_stats.columns = ['隐患数量', '平均风险分']
    print(area_stats.to_string())
    
    print(f"\n[按隐患大类统计]")
    category_stats = df['hazard_category'].value_counts()
    for cat, count in category_stats.items():
        pct = count / len(df) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")
    
    print(f"\n[风险等级分布]")
    level_stats = df['risk_level'].value_counts()
    for level, count in level_stats.items():
        pct = count / len(df) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\n[整改状态]")
    status_stats = df['status'].value_counts()
    for status, count in status_stats.items():
        pct = count / len(df) * 100
        print(f"  {status}: {count} ({pct:.1f}%)")
    
    rectified = len(df[df['status'] == '已整改'])
    total = len(df)
    print(f"\n  整改率: {rectified/total*100:.1f}%")


if __name__ == '__main__':
    generator = HazardDataGenerator()
    df = generator.generate_all_data()
    generator.save_data(df)
    print_data_summary(df)

