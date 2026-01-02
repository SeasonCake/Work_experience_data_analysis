"""
准入控制核心模块 (Access Control)
功能：实现承包商人员准入的核心验证逻辑
包括：黑名单比对、证书过期检查、资质验证、综合准入判断
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class AccessController:
    """准入控制器"""
    
    def __init__(self, blacklist_file=None, config=None):
        """
        初始化准入控制器
        
        参数:
            blacklist_file: 黑名单文件路径
            config: 配置字典
        """
        self.blacklist = self._load_blacklist(blacklist_file) if blacklist_file else set()
        self.config = config or self._default_config()
        self.check_history = []
        
    def _default_config(self):
        """默认配置"""
        return {
            'expiry_warning_days': [30, 7, 1],  # 到期预警天数
            'min_training_score': 80,  # 最低培训合格分数
            'required_certificates': [],  # 所有人必需的证书（普通工种不需要特种证书）
            'special_work_certificates': {  # 特种作业需要的证书（与data_generator保持一致）
                '电工': ['电工作业证', '特种作业操作证'],
                '焊工': ['焊工作业证', '特种作业操作证'],
                '架子工': ['架子工证', '高处作业证'],
                '起重工': ['起重机械作业证', '特种作业操作证'],
                '司炉工': ['锅炉作业证', '特种作业操作证'],
                '高处作业工': ['高处作业证', '特种作业操作证'],
                '制冷工': ['制冷作业证', '特种作业操作证'],
                '叉车司机': ['叉车驾驶证', '特种作业操作证'],
                '塔吊司机': ['塔吊操作证', '建筑施工特种作业证'],
                '信号工': ['起重指挥证', '建筑施工特种作业证'],
            },
            # 普通工种列表（不需要特种作业证书）
            'general_work_types': [
                '普工', '杂工', '辅助工', '清洁工', '搬运工',
                '钳工', '管道工', '油漆工', '泥瓦工', '抹灰工',
                '混凝土工', '钢筋工', '木工', '瓦工', '防水工',
                '保温工', '测量工', '资料员', '安全员', '质检员'
            ]
        }
    
    def _load_blacklist(self, blacklist_file):
        """加载黑名单数据"""
        try:
            if os.path.exists(blacklist_file):
                df = pd.read_excel(blacklist_file)
                # 使用身份证号作为黑名单标识（哈希表，O(1)查询）
                blacklist_set = set(df['身份证号'].values)
                print(f"[OK] 已加载黑名单: {len(blacklist_set)} 人")
                return blacklist_set
            else:
                print("[WARN] 黑名单文件不存在，使用空黑名单")
                return set()
        except Exception as e:
            print(f"[FAIL] 加载黑名单失败: {e}")
            return set()
    
    def check_blacklist(self, id_card):
        """
        黑名单比对
        
        参数:
            id_card: 身份证号
        
        返回:
            dict: 检查结果
        """
        is_blacklisted = id_card in self.blacklist
        
        return {
            'check_type': '黑名单检查',
            'passed': not is_blacklisted,
            'id_card': id_card,
            'is_blacklisted': is_blacklisted,
            'message': '该人员在黑名单中，禁止入场' if is_blacklisted else '未在黑名单中',
            'severity': 'critical' if is_blacklisted else 'ok'
        }
    
    def check_expiry(self, cert_date, cert_name='证书', is_special_worker=False):
        """
        证书过期检查
        
        参数:
            cert_date: 证书有效期日期（datetime.date或str或None）
            cert_name: 证书名称
            is_special_worker: 是否为特种作业人员
        
        返回:
            dict: 检查结果
        """
        # 处理无证书的情况（普通工种）
        if cert_date is None or pd.isna(cert_date) or cert_name in ['无', '', None]:
            if is_special_worker:
                # 特种作业人员必须有证书
                return {
                    'check_type': '证书有效期检查',
                    'passed': False,
                    'cert_name': cert_name if cert_name else '无',
                    'expiry_date': None,
                    'days_until_expiry': None,
                    'message': '特种作业人员缺少有效证书',
                    'severity': 'critical'
                }
            else:
                # 普通工种不需要特种作业证书，直接通过
                return {
                    'check_type': '证书有效期检查',
                    'passed': True,
                    'cert_name': cert_name if cert_name else '普通工种',
                    'expiry_date': None,
                    'days_until_expiry': None,
                    'message': '普通工种，无需特种作业证书',
                    'severity': 'ok'
                }
        
        # 转换日期格式
        if isinstance(cert_date, str):
            try:
                cert_date = datetime.strptime(cert_date, '%Y-%m-%d').date()
            except:
                return {
                    'check_type': '证书有效期检查',
                    'passed': False,
                    'cert_name': cert_name,
                    'expiry_date': cert_date,
                    'message': '日期格式错误',
                    'severity': 'error'
                }
        
        today = datetime.now().date()
        # 确保cert_date是date类型
        if hasattr(cert_date, 'date'):
            cert_date = cert_date.date()
        days_until_expiry = (cert_date - today).days
        
        # 判断状态
        if days_until_expiry < 0:
            passed = False
            message = f'{cert_name}已过期 {abs(days_until_expiry)} 天'
            severity = 'critical'
        elif days_until_expiry <= 7:
            passed = False
            message = f'{cert_name}将在 {days_until_expiry} 天后过期（紧急）'
            severity = 'critical'
        elif days_until_expiry <= 30:
            passed = True  # 可以入场，但需要预警
            message = f'{cert_name}将在 {days_until_expiry} 天后过期（预警）'
            severity = 'warning'
        else:
            passed = True
            message = f'{cert_name}有效，还有 {days_until_expiry} 天到期'
            severity = 'ok'
        
        return {
            'check_type': '证书有效期检查',
            'passed': passed,
            'cert_name': cert_name,
            'expiry_date': cert_date,
            'days_until_expiry': days_until_expiry,
            'message': message,
            'severity': severity
        }
    
    def verify_certificate(self, cert_info):
        """
        证书真伪验证（简化版）
        实际项目中需要对接官方API进行验证
        
        参数:
            cert_info: 证书信息字典
        
        返回:
            dict: 验证结果
        """
        cert_number = cert_info.get('证书编号', '')
        cert_type = cert_info.get('证书类型', '')
        
        # 处理无证书或普通工种的情况
        if cert_type in ['无', '', None] or cert_number in ['待办理', '', None]:
            return {
                'check_type': '证书真伪验证',
                'passed': True,  # 普通工种无需验证
                'cert_number': cert_number,
                'cert_type': cert_type,
                'message': '普通工种，无需特种作业证书验证',
                'severity': 'ok'
            }
        
        # 简单的格式验证
        is_valid_format = len(str(cert_number)) >= 8 and str(cert_number)[:2].isalpha()
        
        # 模拟证书验证（实际需要调用官方API）
        # 这里简化为格式验证
        passed = is_valid_format
        
        return {
            'check_type': '证书真伪验证',
            'passed': passed,
            'cert_number': cert_number,
            'cert_type': cert_type,
            'message': '证书格式有效' if passed else '证书编号格式无效',
            'severity': 'ok' if passed else 'critical'
        }
    
    def check_training_status(self, person_info, training_df=None):
        """
        培训状态检查
        
        参数:
            person_info: 人员信息字典
            training_df: 培训记录DataFrame
        
        返回:
            dict: 检查结果
        """
        # 支持新旧字段格式
        training_score = person_info.get('培训成绩', 0)
        training_date = person_info.get('培训日期')
        
        # 检查是否有培训记录（有培训日期就算完成了入场培训）
        has_training = training_date is not None and pd.notna(training_date)
        
        issues = []
        
        if not has_training:
            issues.append('缺少入场培训记录')
        
        if training_score < self.config['min_training_score']:
            issues.append(f'培训成绩不合格（{training_score}分）')
        
        passed = len(issues) == 0
        message = '培训记录完整' if passed else f"培训问题: {', '.join(issues)}"
        
        return {
            'check_type': '培训状态检查',
            'passed': passed,
            'has_training': has_training,
            'training_score': training_score,
            'issues': issues,
            'message': message,
            'severity': 'ok' if passed else 'warning'
        }
    
    def check_work_qualification(self, person_info):
        """
        工种资质匹配检查
        
        参数:
            person_info: 人员信息字典
        
        返回:
            dict: 检查结果
        """
        work_type = person_info.get('工种', '')
        cert_type = person_info.get('证书类型', '')
        is_special_worker = person_info.get('是否特种作业', False)
        
        # 如果有证书且不是普通培训证书，视为匹配
        general_certs = ['安全培训合格证', '三级安全教育证', '健康证明']
        
        # 检查特种作业人员是否有相应证书
        if is_special_worker:
            # 如果证书类型不是普通证书，认为是匹配的特种作业证书
            if cert_type and cert_type not in general_certs:
                return {
                    'check_type': '工种资质检查',
                    'passed': True,
                    'work_type': work_type,
                    'cert_type': cert_type,
                    'message': '特种作业证书匹配',
                    'severity': 'ok'
                }
            else:
                return {
                    'check_type': '工种资质检查',
                    'passed': False,
                    'work_type': work_type,
                    'cert_type': cert_type,
                    'message': f'{work_type}需要持有特种作业操作证',
                    'severity': 'critical'
                }
        
        return {
            'check_type': '工种资质检查',
            'passed': True,
            'work_type': work_type,
            'cert_type': cert_type,
            'message': '工种资质匹配',
            'severity': 'ok'
        }
    
    def comprehensive_check(self, person_info):
        """
        综合准入检查
        
        参数:
            person_info: 人员信息字典（Series或dict）
        
        返回:
            dict: 综合检查结果
        """
        # 转换Series为dict
        if isinstance(person_info, pd.Series):
            person_info = person_info.to_dict()
        
        check_results = []
        
        # 获取是否为特种作业人员
        is_special_worker = person_info.get('是否特种作业', False)
        
        # 1. 黑名单检查（所有人都要检查）
        blacklist_result = self.check_blacklist(person_info.get('身份证号', ''))
        check_results.append(blacklist_result)
        
        # 2. 证书有效期检查（特种作业人员必须检查，普通工种跳过）
        expiry_result = self.check_expiry(
            person_info.get('有效期至'),
            person_info.get('证书类型', '证书'),
            is_special_worker=is_special_worker
        )
        check_results.append(expiry_result)
        
        # 3. 证书真伪验证（只对有证书的人员验证）
        cert_verify_result = self.verify_certificate({
            '证书编号': person_info.get('证书编号', ''),
            '证书类型': person_info.get('证书类型', '')
        })
        check_results.append(cert_verify_result)
        
        # 4. 培训状态检查
        training_result = self.check_training_status(person_info)
        check_results.append(training_result)
        
        # 5. 工种资质检查
        qualification_result = self.check_work_qualification(person_info)
        check_results.append(qualification_result)
        
        # 汇总结果
        all_passed = all(r['passed'] for r in check_results)
        critical_issues = [r for r in check_results if r['severity'] == 'critical' and not r['passed']]
        warnings = [r for r in check_results if r['severity'] == 'warning']
        
        # 记录检查历史
        check_record = {
            'person_id': person_info.get('人员ID', ''),
            'name': person_info.get('姓名', ''),
            'check_time': datetime.now(),
            'result': 'PASS' if all_passed else 'FAIL',
            'check_results': check_results
        }
        self.check_history.append(check_record)
        
        return {
            'person_id': person_info.get('人员ID', ''),
            'name': person_info.get('姓名', ''),
            'overall_result': 'PASS' if all_passed else 'FAIL',
            'all_passed': all_passed,
            'check_results': check_results,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'check_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def batch_check(self, df_contractors, show_progress=True):
        """
        批量准入检查
        
        参数:
            df_contractors: 承包商人员DataFrame
            show_progress: 是否显示进度
        
        返回:
            pd.DataFrame: 包含检查结果的DataFrame
        """
        print("\n" + "="*80)
        print("开始批量准入检查")
        print("="*80)
        
        results = []
        total = len(df_contractors)
        
        for idx, (_, person) in enumerate(df_contractors.iterrows()):
            result = self.comprehensive_check(person)
            results.append(result)
            
            if show_progress and (idx + 1) % 500 == 0:
                print(f"  已检查: {idx+1}/{total} ({(idx+1)/total*100:.1f}%)")
        
        # 统计结果
        pass_count = sum(1 for r in results if r['overall_result'] == 'PASS')
        fail_count = total - pass_count
        
        # 统计各类问题
        blacklist_count = sum(1 for r in results 
                             if any(c['check_type'] == '黑名单检查' and not c['passed'] 
                                   for c in r['check_results']))
        
        expired_count = sum(1 for r in results 
                           if any(c['check_type'] == '证书有效期检查' and not c['passed']
                                 for c in r['check_results']))
        
        training_incomplete = sum(1 for r in results 
                                 if any(c['check_type'] == '培训状态检查' and not c['passed']
                                       for c in r['check_results']))
        
        qualification_mismatch = sum(1 for r in results 
                                    if any(c['check_type'] == '工种资质检查' and not c['passed']
                                          for c in r['check_results']))
        
        warning_count = sum(len(r['warnings']) for r in results)
        
        # 打印结果
        print("\n" + "="*80)
        print("检查完成！")
        print("="*80)
        print(f"[PASS] 通过人数: {pass_count} 人 ({pass_count/total*100:.1f}%)")
        print(f"[FAIL] 未通过人数: {fail_count} 人 ({fail_count/total*100:.1f}%)")
        print(f"\n问题分类:")
        print(f"  [X] 证书过期: {expired_count} 人")
        print(f"  [X] 黑名单人员: {blacklist_count} 人")
        print(f"  [!] 培训未完成: {training_incomplete} 人")
        print(f"  [!] 资质不符: {qualification_mismatch} 人")
        print(f"  [!] 其他预警: {warning_count} 项")
        print("="*80)
        
        return pd.DataFrame(results)
    
    def generate_report(self, check_results_df, output_file=None):
        """
        生成检查报告
        
        参数:
            check_results_df: 检查结果DataFrame
            output_file: 输出文件路径
        """
        if output_file is None:
            output_file = f'../outputs/access_check_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 准备报告数据
        report_data = []
        
        for _, row in check_results_df.iterrows():
            person_data = {
                '人员ID': row['person_id'],
                '姓名': row['name'],
                '检查结果': row['overall_result'],
                '检查时间': row['check_time']
            }
            
            # 添加各项检查的详细结果
            for check in row['check_results']:
                person_data[check['check_type']] = check['message']
            
            report_data.append(person_data)
        
        report_df = pd.DataFrame(report_data)
        report_df.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"\n[OK] 检查报告已生成: {output_file}")
        
        return output_file


if __name__ == "__main__":
    # 演示用法
    print("准入控制模块演示")
    print("请先运行 data_generator.py 生成测试数据")

