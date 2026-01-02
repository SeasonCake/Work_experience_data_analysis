"""
承包商人员准入自动化系统 - 主程序
整合所有模块，实现完整的准入管理流程
"""

import sys
import os
import pandas as pd
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_generator import ContractorDataGenerator
from src.ocr_simulator import OCRSimulator
from src.access_control import AccessController
from src.dashboard import Dashboard


class ContractorAccessSystem:
    """承包商准入管理系统"""
    
    def __init__(self, data_dir='data', output_dir='outputs'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        self.df_contractors = None
        self.df_blacklist = None
        self.df_training = None
        self.df_entry_exit = None  # 进退场记录
        self.check_results = None
        
    def initialize_data(self, num_contractors=3000, force_regenerate=False):
        """
        初始化数据
        
        参数:
            num_contractors: 承包商人员数量
            force_regenerate: 是否强制重新生成数据
        """
        contractor_file = os.path.join(self.data_dir, 'simulated_contractors.xlsx')
        blacklist_file = os.path.join(self.data_dir, 'blacklist.xlsx')
        training_file = os.path.join(self.data_dir, 'training_records.xlsx')
        entry_exit_file = os.path.join(self.data_dir, 'entry_exit_records.xlsx')
        
        # 检查数据文件是否存在
        if not force_regenerate and os.path.exists(contractor_file):
            print("检测到已有数据文件，正在加载...")
            self.df_contractors = pd.read_excel(contractor_file)
            self.df_blacklist = pd.read_excel(blacklist_file)
            self.df_training = pd.read_excel(training_file)
            if os.path.exists(entry_exit_file):
                self.df_entry_exit = pd.read_excel(entry_exit_file)
            print(f"[OK] 已加载 {len(self.df_contractors)} 条承包商数据")
        else:
            print("正在生成新的模拟数据...")
            generator = ContractorDataGenerator(num_records=num_contractors)
            self.df_contractors, self.df_blacklist, self.df_training, self.df_entry_exit = generator.save_data(self.data_dir)
        
        return self
    
    def run_access_check(self):
        """运行准入检查"""
        if self.df_contractors is None:
            print("错误: 请先初始化数据")
            return None
        
        print("\n" + "="*80)
        print("承包商人员准入自动化检查系统")
        print("="*80)
        print(f"开始处理: {len(self.df_contractors)} 人")
        
        # 创建准入控制器
        blacklist_file = os.path.join(self.data_dir, 'blacklist.xlsx')
        controller = AccessController(blacklist_file=blacklist_file)
        
        # 执行批量检查
        self.check_results = controller.batch_check(self.df_contractors)
        
        return self.check_results
    
    def generate_qualified_list(self):
        """生成合格人员名单（用于制卡）"""
        if self.check_results is None:
            print("错误: 请先运行准入检查")
            return None
        
        print("\n正在生成合格人员名单...")
        
        # 筛选通过检查的人员
        qualified_indices = self.check_results[
            self.check_results['overall_result'] == 'PASS'
        ].index
        
        qualified_personnel = self.df_contractors.iloc[qualified_indices].copy()
        
        # 添加厂牌信息
        qualified_personnel['厂牌编号'] = qualified_personnel.apply(
            lambda row: f"BP-{datetime.now().strftime('%Y')}-{row.name+1:04d}",
            axis=1
        )
        qualified_personnel['厂牌发放日期'] = datetime.now().strftime('%Y-%m-%d')
        qualified_personnel['厂牌有效期'] = (datetime.now() + pd.Timedelta(days=365)).strftime('%Y-%m-%d')
        qualified_personnel['准入状态'] = '合格'
        
        # 选择输出字段（适配新数据结构）
        output_columns = [
            '厂牌编号', '人员ID', '姓名', '身份证号', '联系电话',
            '所属单位', '工种', '工种大类', '用工阶段', '证书类型', '证书编号',
            '有效期至', '入场日期', '厂牌发放日期', '厂牌有效期', '准入状态'
        ]
        
        qualified_list = qualified_personnel[output_columns]
        
        # 保存（使用时间戳避免文件冲突）
        output_file = os.path.join(
            self.output_dir,
            f'qualified_personnel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        qualified_list.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"[OK] 合格人员名单已生成: {output_file}")
        print(f"  合格人数: {len(qualified_list)}")
        
        return qualified_list
    
    def generate_alert_log(self):
        """生成预警日志"""
        if self.check_results is None:
            print("错误: 请先运行准入检查")
            return None
        
        print("\n正在生成预警日志...")
        
        alert_data = []
        
        for idx, row in self.check_results.iterrows():
            person = self.df_contractors.iloc[idx]
            
            # 收集所有警告和错误
            for check in row['check_results']:
                if check['severity'] in ['warning', 'critical'] and not check['passed']:
                    alert_data.append({
                        '人员ID': row['person_id'],
                        '姓名': row['name'],
                        '身份证号': person['身份证号'],
                        '所属单位': person['所属单位'],
                        '问题类型': check['check_type'],
                        '严重程度': check['severity'],
                        '问题描述': check['message'],
                        '检查时间': row['check_time'],
                        '处理状态': '待处理'
                    })
                elif check['severity'] == 'warning' and check['passed']:
                    # 即将过期的预警
                    alert_data.append({
                        '人员ID': row['person_id'],
                        '姓名': row['name'],
                        '身份证号': person['身份证号'],
                        '所属单位': person['所属单位'],
                        '问题类型': check['check_type'],
                        '严重程度': 'warning',
                        '问题描述': check['message'],
                        '检查时间': row['check_time'],
                        '处理状态': '已放行（需关注）'
                    })
        
        if alert_data:
            alert_df = pd.DataFrame(alert_data)
            
            output_file = os.path.join(
                self.output_dir,
                f'alert_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            alert_df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"[OK] 预警日志已生成: {output_file}")
            print(f"  预警条目: {len(alert_df)}")
            
            # 按严重程度统计
            critical_count = len(alert_df[alert_df['严重程度'] == 'critical'])
            warning_count = len(alert_df[alert_df['严重程度'] == 'warning'])
            print(f"    严重问题: {critical_count} 条")
            print(f"    一般预警: {warning_count} 条")
            
            return alert_df
        else:
            print("[OK] 无预警信息")
            return None
    
    def generate_expiry_monitor(self):
        """生成证书到期监控表"""
        if self.df_contractors is None:
            print("错误: 请先初始化数据")
            return None
        
        print("\n正在生成证书到期监控表...")
        
        today = datetime.now().date()
        
        # 确保有效期至是date类型
        if '有效期至' in self.df_contractors.columns:
            self.df_contractors['有效期至'] = pd.to_datetime(self.df_contractors['有效期至'], errors='coerce').dt.date
        
        # 计算距离到期的天数
        self.df_contractors['距离到期天数'] = self.df_contractors['有效期至'].apply(
            lambda x: (x - today).days if pd.notna(x) and x is not None else None
        )
        
        # 筛选需要监控的证书（90天内到期）
        monitor_df = self.df_contractors[
            (self.df_contractors['距离到期天数'] <= 90) &
            (self.df_contractors['距离到期天数'] >= 0)
        ].copy()
        
        # 添加预警等级
        def get_alert_level(days):
            if days <= 7:
                return '紧急'
            elif days <= 30:
                return '重要'
            elif days <= 90:
                return '提醒'
            else:
                return '正常'
        
        monitor_df['预警等级'] = monitor_df['距离到期天数'].apply(get_alert_level)
        
        # 排序
        monitor_df = monitor_df.sort_values('距离到期天数')
        
        # 选择输出字段
        output_columns = [
            '人员ID', '姓名', '身份证号', '联系电话', '所属单位', '工种',
            '证书类型', '证书编号', '有效期至', '距离到期天数', '预警等级', '备注'
        ]
        
        monitor_output = monitor_df[output_columns]
        
        # 保存（使用时间戳避免文件冲突）
        output_file = os.path.join(
            self.output_dir,
            f'expiry_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        monitor_output.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"[OK] 证书到期监控表已生成: {output_file}")
        print(f"  监控人数: {len(monitor_output)}")
        print(f"    7天内到期: {len(monitor_df[monitor_df['预警等级']=='紧急'])} 人")
        print(f"    30天内到期: {len(monitor_df[monitor_df['预警等级']=='重要'])} 人")
        print(f"    90天内到期: {len(monitor_df[monitor_df['预警等级']=='提醒'])} 人")
        
        return monitor_output
    
    def generate_dashboard(self, auto_open=True):
        """
        生成可视化仪表板
        
        参数:
            auto_open: 是否自动在浏览器中打开
        """
        if self.df_contractors is None:
            print("错误: 请先初始化数据")
            return None
        
        print("\n正在生成可视化仪表板...")
        
        # 创建仪表板
        dashboard = Dashboard(
            df_contractors=self.df_contractors,
            df_training=self.df_training,
            df_blacklist=self.df_blacklist,
            df_entry_exit=self.df_entry_exit,
            check_results=self.check_results
        )
        
        # 打印每日摘要到控制台
        dashboard.print_daily_summary()
        
        # 生成HTML报告
        output_file = os.path.join(
            self.output_dir,
            f'dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        )
        dashboard.generate_html_report(output_path=output_file)
        
        # 自动打开浏览器
        if auto_open:
            import webbrowser
            abs_path = os.path.abspath(output_file)
            print(f"\n正在打开仪表板: {abs_path}")
            webbrowser.open(f'file://{abs_path}')
        
        return output_file
    
    def run_complete_workflow(self, generate_visualization=True, auto_open_dashboard=True):
        """
        运行完整工作流程
        
        参数:
            generate_visualization: 是否生成可视化仪表板
            auto_open_dashboard: 是否自动在浏览器中打开仪表板
        """
        total_steps = 6 if generate_visualization else 5
        
        print("\n" + "="*80)
        print("承包商人员准入自动化系统")
        print("完整工作流程")
        print("="*80)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. 初始化数据
        print(f"\n步骤 1/{total_steps}: 初始化数据")
        self.initialize_data()
        
        # 2. 运行准入检查
        print(f"\n步骤 2/{total_steps}: 执行准入检查")
        self.run_access_check()
        
        # 3. 生成合格人员名单
        print(f"\n步骤 3/{total_steps}: 生成合格人员名单")
        self.generate_qualified_list()
        
        # 4. 生成预警日志
        print(f"\n步骤 4/{total_steps}: 生成预警日志")
        self.generate_alert_log()
        
        # 5. 生成到期监控表
        print(f"\n步骤 5/{total_steps}: 生成证书到期监控表")
        self.generate_expiry_monitor()
        
        # 6. 生成可视化仪表板
        dashboard_file = None
        if generate_visualization:
            print(f"\n步骤 6/{total_steps}: 生成可视化仪表板")
            dashboard_file = self.generate_dashboard(auto_open=auto_open_dashboard)
        
        print("\n" + "="*80)
        print("所有流程执行完成！")
        print("="*80)
        print(f"\n输出文件位置: {os.path.abspath(self.output_dir)}")
        print("\n生成的文件:")
        for file in os.listdir(self.output_dir):
            if file.endswith(('.xlsx', '.html')):
                file_path = os.path.join(self.output_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                file_icon = "[Excel]" if file.endswith('.xlsx') else "[HTML]"
                print(f"  {file_icon} {file} ({file_size:.1f} KB)")
        
        if dashboard_file:
            print(f"\n[TIP] 可视化仪表板已生成，可在浏览器中查看实时监控数据")
            print(f"      路径: {os.path.abspath(dashboard_file)}")
        
        print("\n" + "="*80)


def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     承包商人员准入自动化系统                                   ║
    ║     Contractor Access Automation System                        ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # 创建系统实例
    system = ContractorAccessSystem()
    
    # 运行完整工作流程
    system.run_complete_workflow()


if __name__ == "__main__":
    main()

