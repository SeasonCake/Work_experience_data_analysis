"""
数据生成模块 (Data Generator)
功能：模拟大型工业项目（化工/制造行业）承包商人员数据
时间线：2023-2026年，从在建到全面运行的演进过程
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# 创建Faker实例（中文）
fake = Faker('zh_CN')
Faker.seed(42)
random.seed(42)
np.random.seed(42)


class ContractorDataGenerator:
    """承包商数据生成器 - 化工/电池制造行业场景"""
    
    def __init__(self, num_records=3000):
        self.num_records = num_records
        
        # ========== 项目阶段定义（2023-2026）==========
        # 模拟工厂从在建到运行的过程
        self.project_phases = {
            '2023-H1': {'在建比例': 0.60, '运行比例': 0.40, '描述': '项目建设高峰期'},
            '2023-H2': {'在建比例': 0.50, '运行比例': 0.50, '描述': '一期投产，二期在建'},
            '2024-H1': {'在建比例': 0.35, '运行比例': 0.65, '描述': '二期主体完工'},
            '2024-H2': {'在建比例': 0.20, '运行比例': 0.80, '描述': '二期投产调试'},
            '2025-H1': {'在建比例': 0.10, '运行比例': 0.90, '描述': '三期建设'},
            '2025-H2': {'在建比例': 0.05, '运行比例': 0.95, '描述': '全面运行'},
            '2026-H1': {'在建比例': 0.03, '运行比例': 0.97, '描述': '日常维护'},
        }
        
        # ========== 工种分类（大类）==========
        # 建设期工种 - 项目在建阶段为主
        self.construction_work_types = {
            '土建类': {
                'works': ['混凝土工', '钢筋工', '木工', '瓦工', '泥瓦工', '防水工', '抹灰工'],
                'special': False,
                'color': '#3498db'
            },
            '安装类': {
                'works': ['管道工', '电气安装工', '仪表安装工', '设备安装工', '通风工'],
                'special': False,
                'color': '#9b59b6'
            },
            '特种施工': {
                'works': ['焊工', '电工', '架子工', '高处作业工', '塔吊司机', '信号工'],
                'special': True,
                'color': '#e74c3c'
            },
            '辅助施工': {
                'works': ['普工', '杂工', '搬运工', '清洁工', '场地整理工'],
                'special': False,
                'color': '#95a5a6'
            }
        }
        
        # 运行期工种 - 工厂运行阶段为主
        self.operation_work_types = {
            '生产操作': {
                'works': ['操作工', '配料工', '涂布工', '卷绕工', '注液工', '化成工', '包装工'],
                'special': False,
                'color': '#2ecc71'
            },
            '设备运维': {
                'works': ['电工', '仪表工', '机修工', '设备巡检员', 'PLC技术员', '自动化工程师'],
                'special': True,
                'color': '#e67e22'
            },
            '特种设备': {
                'works': ['叉车司机', '起重工', '锅炉工', '压力容器操作员', '危化品押运员'],
                'special': True,
                'color': '#e74c3c'
            },
            '安全环保': {
                'works': ['安全员', '消防员', '环保监测员', '职业卫生员', '应急救援员'],
                'special': False,
                'color': '#1abc9c'
            },
            '质量检测': {
                'works': ['质检员', '化验员', '计量员', '理化分析员'],
                'special': False,
                'color': '#f39c12'
            }
        }
        
        # 特种作业证书映射
        self.special_certificates = {
            '焊工': '焊接与热切割作业证',
            '电工': '低压电工作业证',
            '架子工': '登高架设作业证',
            '高处作业工': '高处作业证',
            '塔吊司机': '塔式起重机司机证',
            '信号工': '起重指挥证',
            '叉车司机': '叉车司机证',
            '起重工': '起重机械作业证',
            '锅炉工': '锅炉作业证',
            '压力容器操作员': '压力容器作业证',
            '危化品押运员': '危化品押运员证',
            '仪表工': '仪表维修工证',
            '机修工': '设备维修证',
            'PLC技术员': '电气自动化证',
            '自动化工程师': '电气自动化证',
        }
        
        # 普通证书
        self.general_certificates = ['安全培训合格证', '三级安全教育证', '健康证明']
        
        # 承包商公司（按类型分）
        self.contractors = {
            '施工总包': [f'{fake.company()}建设集团' for _ in range(10)],
            '安装分包': [f'{fake.company()}安装工程公司' for _ in range(15)],
            '劳务分包': [f'{fake.company()}劳务公司' for _ in range(20)],
            '设备维保': [f'{fake.company()}设备服务公司' for _ in range(10)],
            '物流运输': [f'{fake.company()}物流公司' for _ in range(5)]
        }
        
        # 发证机关
        self.issuing_authorities = {
            'special': ['应急管理部', '市应急管理局', '省应急管理厅', '市场监督管理局'],
            'general': ['公司安全环保部', '项目安全科', '培训中心']
        }
    
    def get_phase_date_range(self, phase):
        """获取阶段对应的日期范围"""
        phase_dates = {
            '2023-H1': (datetime(2023, 1, 1), datetime(2023, 6, 30)),
            '2023-H2': (datetime(2023, 7, 1), datetime(2023, 12, 31)),
            '2024-H1': (datetime(2024, 1, 1), datetime(2024, 6, 30)),
            '2024-H2': (datetime(2024, 7, 1), datetime(2024, 12, 31)),
            '2025-H1': (datetime(2025, 1, 1), datetime(2025, 6, 30)),
            '2025-H2': (datetime(2025, 7, 1), datetime(2025, 12, 31)),
            '2026-H1': (datetime(2026, 1, 1), datetime(2026, 6, 30)),
        }
        return phase_dates.get(phase)
    
    def generate_id_card(self):
        """生成身份证号"""
        area_code = str(random.randint(100000, 999999))
        birth_year = random.randint(1970, 2000)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"
        sequence = str(random.randint(100, 999))
        check_digit = str(random.randint(0, 9))
        return area_code + birth_date + sequence + check_digit
    
    def generate_certificate_number(self, cert_type):
        """生成证书编号"""
        prefix_map = {
            '焊接与热切割作业证': 'HG', '低压电工作业证': 'DG',
            '登高架设作业证': 'GJ', '高处作业证': 'GC',
            '塔式起重机司机证': 'TD', '起重指挥证': 'QZ',
            '叉车司机证': 'CC', '起重机械作业证': 'QJ',
            '锅炉作业证': 'GL', '压力容器作业证': 'YL',
            '危化品押运员证': 'WH', '仪表维修工证': 'YB',
            '设备维修证': 'SB', '电气自动化证': 'DQ',
            '安全培训合格证': 'PX', '三级安全教育证': 'SJ',
            '健康证明': 'JK', '无': ''
        }
        prefix = prefix_map.get(cert_type, 'XX')
        if not prefix:
            return '待办理'
        year = random.randint(2022, 2025)
        number = random.randint(100000, 999999)
        return f"{prefix}{year}{number}"
    
    def generate_contractors_data(self):
        """生成承包商人员数据（动态进退场模型）"""
        print("\n" + "="*60)
        print("开始生成承包商数据集（化工/电池制造行业场景）...")
        print("="*60)
        print("模型: 动态进退场，在场人数100-400人，累计3000人")
        
        data = []
        entry_exit_records = []  # 进退场记录
        today = datetime.now().date()
        
        # 按阶段分配人员 - 动态进退场模型
        phases = list(self.project_phases.keys())
        
        # 每个阶段的“新增入场”与“截至当前日期的退场概率（by as-of）”
        # 目标：截至 today（例如 2026-01-02）在场人数约 100-400，但累计入场约 3000
        phase_config = {
            # 老阶段：绝大多数已退场；新阶段：仍有一部分在场
            '2023-H1': {'new_entry': 500, 'exit_prob': 0.97},
            '2023-H2': {'new_entry': 550, 'exit_prob': 0.97},
            '2024-H1': {'new_entry': 500, 'exit_prob': 0.93},
            '2024-H2': {'new_entry': 450, 'exit_prob': 0.93},
            '2025-H1': {'new_entry': 400, 'exit_prob': 0.88},
            '2025-H2': {'new_entry': 350, 'exit_prob': 0.88},
            '2026-H1': {'new_entry': 250, 'exit_prob': 0.60},
        }
        
        person_id_counter = 1
        
        for phase_idx, phase in enumerate(phases):
            phase_info = self.project_phases[phase]
            construction_ratio = phase_info['在建比例']
            operation_ratio = phase_info['运行比例']
            
            phase_start, phase_end = self.get_phase_date_range(phase)
            config = phase_config[phase]
            phase_records = config['new_entry']
            exit_prob = config['exit_prob']
            
            print(f"\n[{phase}] {phase_info['描述']}")
            print(f"  在建: {construction_ratio*100:.0f}% | 运行: {operation_ratio*100:.0f}%")
            print(f"  新入场: {phase_records}人 | 截止今日退场概率: {exit_prob*100:.0f}%")
            
            for i in range(phase_records):
                person_id = f"BP-{phase.replace('-', '')}-{person_id_counter:04d}"
                person_id_counter += 1
                
                name = fake.name()
                id_card = self.generate_id_card()
                phone = fake.phone_number()
                
                # 决定是建设期还是运行期工种
                is_construction = random.random() < construction_ratio
                
                if is_construction:
                    # 在建区域工种
                    period_type = '在建区域'
                    category = random.choice(list(self.construction_work_types.keys()))
                    category_info = self.construction_work_types[category]
                    work_type = random.choice(category_info['works'])
                    is_special = category_info['special'] or work_type in self.special_certificates
                    contractor_type = random.choice(['施工总包', '安装分包', '劳务分包'])
                else:
                    # 运行区域工种
                    period_type = '运行区域'
                    category = random.choice(list(self.operation_work_types.keys()))
                    category_info = self.operation_work_types[category]
                    work_type = random.choice(category_info['works'])
                    is_special = category_info['special'] or work_type in self.special_certificates
                    contractor_type = random.choice(['设备维保', '劳务分包', '物流运输'])
                
                contractor = random.choice(self.contractors[contractor_type])
                
                # 证书信息
                if work_type in self.special_certificates:
                    cert_type = self.special_certificates[work_type]
                    issuing_authority = random.choice(self.issuing_authorities['special'])
                    is_special = True
                else:
                    cert_type = random.choice(self.general_certificates)
                    issuing_authority = random.choice(self.issuing_authorities['general'])
                
                cert_number = self.generate_certificate_number(cert_type)
                
                # 入场日期（在该阶段内随机）
                entry_date = fake.date_between(
                    start_date=phase_start.date(),
                    end_date=min(phase_end.date(), today)
                )
                
                # 证书有效期
                if is_special:
                    validity_days = random.randint(1080, 2160)  # 3-6年
                else:
                    validity_days = random.randint(365, 730)  # 1-2年
                
                # 大部分证书正常，少数过期或即将到期
                cert_status = random.choices(
                    ['正常', '即将到期', '已过期'],
                    weights=[0.85, 0.10, 0.05]
                )[0]
                
                if cert_status == '正常':
                    expiry_date = today + timedelta(days=random.randint(91, validity_days))
                elif cert_status == '即将到期':
                    expiry_date = today + timedelta(days=random.randint(1, 30))
                else:
                    expiry_date = today - timedelta(days=random.randint(1, 60))
                
                issue_date = expiry_date - timedelta(days=validity_days)
                if issue_date < datetime(2022, 1, 1).date():
                    issue_date = datetime(2022, 1, 1).date() + timedelta(days=random.randint(0, 180))
                
                # 退场状态（by as-of）：用“截至 today 是否已经退场”来模拟动态
                # 建设期更短工期更易退场；运行期相对稳定但也有轮换
                actual_exit_prob = exit_prob if is_construction else min(0.98, exit_prob * 0.7)
                has_exited = random.random() < actual_exit_prob

                exit_date = None
                status = '在场'
                if has_exited:
                    # 退场日期必须 <= today，避免“名义退场但实际上还没到退场日”导致在场人数虚高
                    min_work_days = 30 if is_construction else 90
                    max_work_days = 240 if is_construction else 540
                    exit_start = entry_date + timedelta(days=min_work_days)
                    exit_end = min(entry_date + timedelta(days=max_work_days), today)

                    if exit_start <= exit_end:
                        exit_date = fake.date_between(start_date=exit_start, end_date=exit_end)
                        status = '已退场'
                
                # 培训信息
                training_score = random.randint(80, 100) if status == '在场' else random.randint(75, 95)
                training_end = min(entry_date + timedelta(days=7), today)
                if entry_date < training_end:
                    training_date = fake.date_between(start_date=entry_date, end_date=training_end)
                else:
                    training_date = entry_date
                
                data.append({
                    '人员ID': person_id,
                    '姓名': name,
                    '身份证号': id_card,
                    '联系电话': phone,
                    '所属单位': contractor,
                    '承包商类型': contractor_type,
                    '工种': work_type,
                    '工种大类': category,
                    '用工阶段': period_type,
                    '入场阶段': phase,
                    '证书类型': cert_type,
                    '证书编号': cert_number,
                    '发证日期': issue_date,
                    '有效期至': expiry_date,
                    '发证机关': issuing_authority,
                    '是否特种作业': is_special,
                    '入场日期': entry_date,
                    '退场日期': exit_date,
                    '人员状态': status,
                    '培训日期': training_date,
                    '培训成绩': training_score,
                    '备注': f'{period_type}-{category}'
                })
                
                # 记录进退场
                entry_exit_records.append({
                    '人员ID': person_id,
                    '姓名': name,
                    '工种大类': category,
                    '用工阶段': period_type,
                    '阶段': phase,
                    '类型': '入场',
                    '日期': entry_date
                })
                if exit_date:
                    entry_exit_records.append({
                        '人员ID': person_id,
                        '姓名': name,
                        '工种大类': category,
                        '用工阶段': period_type,
                        '阶段': phase,
                        '类型': '退场',
                        '日期': exit_date
                    })
        
        df = pd.DataFrame(data)
        df_entry_exit = pd.DataFrame(entry_exit_records)

        # === 后处理：强制“在场人数”落在 100-400 的现实区间（用于可视化与演示） ===
        # 说明：这是一个“快照模型”，目的是让 as-of 今日的在场规模更贴近工厂现场管理习惯
        onsite_min, onsite_max = 100, 400
        onsite_count = int((df['人员状态'] == '在场').sum())
        if onsite_count > onsite_max:
            # 优先让“更早阶段”的人员退场
            active_idx = df[df['人员状态'] == '在场'].copy()
            active_idx['phase_rank'] = active_idx['入场阶段'].map({
                '2023-H1': 1, '2023-H2': 2, '2024-H1': 3, '2024-H2': 4, '2025-H1': 5, '2025-H2': 6, '2026-H1': 7
            }).fillna(99)
            active_idx = active_idx.sort_values(['phase_rank'])
            need_exit = onsite_count - onsite_max
            choose_ids = active_idx.head(need_exit)['人员ID'].tolist()
            for pid in choose_ids:
                row_i = df.index[df['人员ID'] == pid][0]
                entry_d = df.at[row_i, '入场日期']
                # 安全退场日：入场后30-120天内，且不晚于 today
                exit_start = entry_d + timedelta(days=30)
                exit_end = min(entry_d + timedelta(days=120), today)
                if exit_start <= exit_end:
                    df.at[row_i, '退场日期'] = fake.date_between(start_date=exit_start, end_date=exit_end)
                    df.at[row_i, '人员状态'] = '已退场'
                else:
                    # 兜底：当天退场
                    df.at[row_i, '退场日期'] = today
                    df.at[row_i, '人员状态'] = '已退场'
        elif onsite_count < onsite_min:
            # 不足时，让部分“最近阶段”的退场人员回到在场（演示用）
            exited_idx = df[df['人员状态'] == '已退场'].copy()
            exited_idx['phase_rank'] = exited_idx['入场阶段'].map({
                '2023-H1': 1, '2023-H2': 2, '2024-H1': 3, '2024-H2': 4, '2025-H1': 5, '2025-H2': 6, '2026-H1': 7
            }).fillna(0)
            exited_idx = exited_idx.sort_values(['phase_rank'], ascending=False)
            need_back = onsite_min - onsite_count
            choose_ids = exited_idx.head(need_back)['人员ID'].tolist()
            for pid in choose_ids:
                row_i = df.index[df['人员ID'] == pid][0]
                df.at[row_i, '退场日期'] = None
                df.at[row_i, '人员状态'] = '在场'

        # 同步修正进退场记录（保证仪表板趋势与表格一致）
        # 重新从 df 生成进退场记录，避免前面记录与后处理不一致
        ee = []
        for _, r in df.iterrows():
            ee.append({
                '人员ID': r['人员ID'], '姓名': r['姓名'],
                '工种大类': r.get('工种大类', ''), '用工阶段': r.get('用工阶段', ''),
                '阶段': r.get('入场阶段', ''), '类型': '入场', '日期': r.get('入场日期')
            })
            if pd.notna(r.get('退场日期')) and r.get('退场日期') is not None:
                ee.append({
                    '人员ID': r['人员ID'], '姓名': r['姓名'],
                    '工种大类': r.get('工种大类', ''), '用工阶段': r.get('用工阶段', ''),
                    '阶段': r.get('入场阶段', ''), '类型': '退场', '日期': r.get('退场日期')
                })
        df_entry_exit = pd.DataFrame(ee)
        
        # 统计信息
        print(f"\n[OK] 人员数据生成完成，共 {len(df)} 条记录")
        print(f"  在建区域人员: {len(df[df['用工阶段']=='在建区域'])} 人")
        print(f"  运行区域人员: {len(df[df['用工阶段']=='运行区域'])} 人")
        print(f"  特种作业人员: {len(df[df['是否特种作业']==True])} 人")
        print(f"  当前在场: {len(df[df['人员状态']=='在场'])} 人")
        print(f"  已退场: {len(df[df['人员状态']=='已退场'])} 人")
        
        return df, df_entry_exit
    
    def generate_blacklist(self, num_records=5):
        """生成黑名单数据"""
        print(f"\n正在生成 {num_records} 条黑名单数据...")
        
        data = []
        reasons = [
            '违反安全操作规程造成事故',
            '伪造资质证书',
            '多次违章作业',
            '盗窃公司财物',
            '打架斗殴'
        ]
        
        for i in range(num_records):
            data.append({
                '黑名单ID': f'BL-{i+1:04d}',
                '姓名': fake.name(),
                '身份证号': self.generate_id_card(),
                '原所属单位': random.choice(self.contractors['劳务分包']),
                '拉黑原因': random.choice(reasons),
                '拉黑日期': fake.date_between(start_date='-2y', end_date='-30d'),
                '拉黑期限': random.choice(['永久', '3年', '5年']),
                '录入人': fake.name(),
                '备注': ''
            })
        
        df = pd.DataFrame(data)
        print(f"[OK] 黑名单数据生成完成，共 {len(df)} 条记录")
        return df
    
    def generate_training_records(self, df_contractors):
        """生成培训记录数据（按季度直接控制数量，确保有真实波动）"""
        print("\n正在生成培训记录数据...")
        
        data = []
        training_types = {
            '在建区域': ['三级安全教育', '高处作业培训', '动火作业培训', '吊装作业培训', '临时用电培训'],
            '运行区域': ['入场安全培训', '岗位技能培训', '危化品培训', '消防培训', '应急演练']
        }
        
        # 直接定义每个季度的培训人次目标（绝对数值，确保有明显波动）
        # 这是真实的业务逻辑：建设高峰期培训多，稳定期培训少
        quarterly_targets = {
            '2023Q1': {'在建区域': 650, '运行区域': 180},  # 项目启动
            '2023Q2': {'在建区域': 780, '运行区域': 220},  # 建设高峰
            '2023Q3': {'在建区域': 620, '运行区域': 250},  # 夏季略降
            '2023Q4': {'在建区域': 720, '运行区域': 280},  # 年底冲刺
            '2024Q1': {'在建区域': 580, '运行区域': 350},  # 转型开始
            '2024Q2': {'在建区域': 450, '运行区域': 420},  # 运行增加
            '2024Q3': {'在建区域': 320, '运行区域': 480},  # 建设减少
            '2024Q4': {'在建区域': 280, '运行区域': 520},  # 调试期
            '2025Q1': {'在建区域': 220, '运行区域': 480},  # 运行为主
            '2025Q2': {'在建区域': 180, '运行区域': 420},  # 稳定运行
            '2025Q3': {'在建区域': 150, '运行区域': 380},  # 夏季低谷
            '2025Q4': {'在建区域': 160, '运行区域': 450},  # 年底培训
            '2026Q1': {'在建区域': 120, '运行区域': 350},  # 日常维护
        }
        
        # 获取各区域人员列表
        construction_personnel = df_contractors[df_contractors['用工阶段'] == '在建区域']['人员ID'].tolist()
        operation_personnel = df_contractors[df_contractors['用工阶段'] == '运行区域']['人员ID'].tolist()
        
        # 如果没有人员，尝试用旧术语
        if not construction_personnel:
            construction_personnel = df_contractors[df_contractors['用工阶段'] == '建设期']['人员ID'].tolist()
        if not operation_personnel:
            operation_personnel = df_contractors[df_contractors['用工阶段'] == '运行期']['人员ID'].tolist()
        
        print(f"  在建区域人员池: {len(construction_personnel)} 人")
        print(f"  运行区域人员池: {len(operation_personnel)} 人")
        
        personnel_map = df_contractors.set_index('人员ID').to_dict('index')
        record_counter = 0
        
        # 按季度生成培训记录
        for quarter, targets in quarterly_targets.items():
            year = int(quarter[:4])
            q = int(quarter[-1])
            
            for period_key, target_count in targets.items():
                personnel_pool = construction_personnel if period_key == '在建区域' else operation_personnel
                available_types = training_types[period_key]
                
                if not personnel_pool:
                    continue
                
                # 添加随机波动（±15%）
                actual_count = int(target_count * random.uniform(0.85, 1.15))
                
                for _ in range(actual_count):
                    record_counter += 1
                    person_id = random.choice(personnel_pool)
                    person_info = personnel_map.get(person_id, {})
                    
                    # 在该季度内随机选择日期
                    month_start = (q - 1) * 3 + 1
                    month_end = q * 3
                    training_date = fake.date_between(
                        start_date=datetime(year, month_start, 1),
                        end_date=datetime(year, month_end, 28 if month_end == 2 else 30)
                    )
                    
                    # 合格率随培训类型略有不同（94-98%）
                    pass_rate = random.uniform(0.94, 0.98)
                    is_qualified = random.random() < pass_rate
                    
                    data.append({
                        '培训ID': f"TR-{record_counter:06d}",
                        '人员ID': person_id,
                        '姓名': person_info.get('姓名', fake.name()),
                        '工种大类': person_info.get('工种大类', ''),
                        '用工阶段': period_key,
                        '入场阶段': person_info.get('入场阶段', ''),
                        '培训类型': random.choice(available_types),
                        '培训日期': training_date,
                        '培训成绩': random.randint(75, 100) if is_qualified else random.randint(50, 74),
                        '是否合格': is_qualified,
                        '培训讲师': fake.name(),
                        '培训时长': random.choice([2, 4, 8, 16]),
                        '备注': ''
                    })
        
        df = pd.DataFrame(data)
        
        # 打印各季度培训统计
        print(f"\n  培训数据统计:")
        df['季度'] = pd.to_datetime(df['培训日期']).dt.to_period('Q').astype(str)
        for q in sorted(df['季度'].unique()):
            q_data = df[df['季度'] == q]
            construct = len(q_data[q_data['用工阶段'] == '在建区域'])
            operate = len(q_data[q_data['用工阶段'] == '运行区域'])
            print(f"    {q}: 在建区域={construct:>4}, 运行区域={operate:>4}")
        
        df = df.drop(columns=['季度'])  # 删除临时列
        print(f"\n[OK] 培训记录数据生成完成，共 {len(df)} 条记录")
        return df
    
    def save_data(self, output_dir='data'):
        """保存所有数据到文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成数据
        df_contractors, df_entry_exit = self.generate_contractors_data()
        df_blacklist = self.generate_blacklist()
        df_training = self.generate_training_records(df_contractors)
        
        # 保存
        print("\n正在保存数据文件...")
        
        contractor_file = os.path.join(output_dir, 'simulated_contractors.xlsx')
        df_contractors.to_excel(contractor_file, index=False, engine='openpyxl')
        print(f"[OK] 承包商数据已保存: {contractor_file}")
        
        entry_exit_file = os.path.join(output_dir, 'entry_exit_records.xlsx')
        df_entry_exit.to_excel(entry_exit_file, index=False, engine='openpyxl')
        print(f"[OK] 进退场记录已保存: {entry_exit_file}")
        
        blacklist_file = os.path.join(output_dir, 'blacklist.xlsx')
        df_blacklist.to_excel(blacklist_file, index=False, engine='openpyxl')
        print(f"[OK] 黑名单数据已保存: {blacklist_file}")
        
        training_file = os.path.join(output_dir, 'training_records.xlsx')
        df_training.to_excel(training_file, index=False, engine='openpyxl')
        print(f"[OK] 培训记录已保存: {training_file}")
        
        # 统计摘要
        print("\n" + "="*60)
        print("数据生成统计:")
        print("="*60)
        print(f"承包商人员总数: {len(df_contractors)}")
        print(f"  - 在建区域人员: {len(df_contractors[df_contractors['用工阶段']=='在建区域'])}")
        print(f"  - 运行区域人员: {len(df_contractors[df_contractors['用工阶段']=='运行区域'])}")
        print(f"  - 当前在场: {len(df_contractors[df_contractors['人员状态']=='在场'])}")
        print(f"  - 特种作业: {len(df_contractors[df_contractors['是否特种作业']==True])}")
        print(f"\n黑名单人员数: {len(df_blacklist)}")
        print(f"培训记录数: {len(df_training)}")
        print(f"进退场记录数: {len(df_entry_exit)}")
        print("="*60)
        
        return df_contractors, df_blacklist, df_training, df_entry_exit


def main():
    """测试数据生成"""
    generator = ContractorDataGenerator(num_records=3000)
    generator.save_data('data')


if __name__ == "__main__":
    main()
