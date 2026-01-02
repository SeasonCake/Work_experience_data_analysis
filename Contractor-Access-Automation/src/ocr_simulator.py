"""
OCR模拟模块 (OCR Simulator)
功能：模拟证件OCR识别过程
在实际项目中，这里会调用真实的OCR API（如百度OCR、阿里云OCR等）
本模块重点展示OCR后的数据处理逻辑
"""

import random
import json
from datetime import datetime


class OCRSimulator:
    """OCR识别模拟器"""
    
    def __init__(self, accuracy=0.98):
        """
        初始化OCR模拟器
        
        参数:
            accuracy: 识别准确率 (0.0-1.0)
        """
        self.accuracy = accuracy
        
    def mock_ocr_scan(self, image_path, cert_type='身份证'):
        """
        模拟OCR扫描证件
        
        参数:
            image_path: 证件图片路径（模拟用，实际不读取）
            cert_type: 证件类型 ('身份证', '安全生产许可证', '特种作业证'等)
        
        返回:
            dict: OCR识别结果
        """
        # 模拟识别延时
        import time
        time.sleep(random.uniform(0.1, 0.3))
        
        # 根据证件类型返回不同的识别结果
        if cert_type == '身份证':
            return self._mock_id_card_ocr(image_path)
        elif cert_type in ['安全生产许可证', '特种作业操作证', '建筑施工特种作业证']:
            return self._mock_certificate_ocr(image_path, cert_type)
        else:
            return self._mock_generic_ocr(image_path)
    
    def _mock_id_card_ocr(self, image_path):
        """模拟身份证OCR识别"""
        # 模拟识别结果
        result = {
            'success': True,
            'confidence': round(random.uniform(0.90, 0.99), 3),
            'image_path': image_path,
            'cert_type': '身份证',
            'data': {
                '姓名': None,  # 实际使用时会从真实图片识别
                '性别': random.choice(['男', '女']),
                '民族': random.choice(['汉', '回', '蒙古', '维吾尔']),
                '出生日期': None,
                '身份证号': None,
                '住址': None,
                '签发机关': None,
                '有效期限': None
            },
            'ocr_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 模拟识别错误
        if random.random() > self.accuracy:
            result['success'] = False
            result['error'] = '图片模糊，无法识别'
            result['confidence'] = round(random.uniform(0.50, 0.70), 3)
        
        return result
    
    def _mock_certificate_ocr(self, image_path, cert_type):
        """模拟证书OCR识别"""
        result = {
            'success': True,
            'confidence': round(random.uniform(0.85, 0.98), 3),
            'image_path': image_path,
            'cert_type': cert_type,
            'data': {
                '证书名称': cert_type,
                '证书编号': None,
                '姓名': None,
                '性别': random.choice(['男', '女']),
                '身份证号': None,
                '工种': None,
                '发证日期': None,
                '有效期至': None,
                '发证机关': None,
                '证书状态': '有效'
            },
            'ocr_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 模拟识别错误
        if random.random() > self.accuracy:
            result['success'] = False
            result['error'] = random.choice([
                '图片质量不佳',
                '证书折痕影响识别',
                '光线不足',
                '部分文字模糊'
            ])
            result['confidence'] = round(random.uniform(0.50, 0.75), 3)
        
        return result
    
    def _mock_generic_ocr(self, image_path):
        """模拟通用证件OCR识别"""
        result = {
            'success': True,
            'confidence': round(random.uniform(0.80, 0.95), 3),
            'image_path': image_path,
            'cert_type': '其他证件',
            'data': {
                '识别文本': []
            },
            'ocr_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    def batch_ocr_scan(self, image_paths, cert_type='身份证'):
        """
        批量OCR识别
        
        参数:
            image_paths: 证件图片路径列表
            cert_type: 证件类型
        
        返回:
            list: OCR识别结果列表
        """
        results = []
        total = len(image_paths)
        
        print(f"开始批量OCR识别，共 {total} 张图片...")
        
        for i, image_path in enumerate(image_paths):
            result = self.mock_ocr_scan(image_path, cert_type)
            results.append(result)
            
            # 显示进度
            if (i + 1) % 100 == 0 or (i + 1) == total:
                progress = (i + 1) / total * 100
                print(f"  进度: {i+1}/{total} ({progress:.1f}%)")
        
        # 统计识别结果
        success_count = sum(1 for r in results if r['success'])
        fail_count = total - success_count
        avg_confidence = sum(r['confidence'] for r in results) / total
        
        print(f"\n识别完成:")
        print(f"  成功: {success_count} 张 ({success_count/total*100:.1f}%)")
        print(f"  失败: {fail_count} 张 ({fail_count/total*100:.1f}%)")
        print(f"  平均置信度: {avg_confidence:.3f}")
        
        return results
    
    def extract_key_info(self, ocr_result):
        """
        从OCR结果中提取关键信息
        
        参数:
            ocr_result: OCR识别结果字典
        
        返回:
            dict: 提取的关键信息
        """
        if not ocr_result['success']:
            return {
                'status': 'failed',
                'error': ocr_result.get('error', '识别失败'),
                'data': None
            }
        
        key_info = {
            'status': 'success',
            'cert_type': ocr_result['cert_type'],
            'confidence': ocr_result['confidence'],
            'extracted_data': ocr_result['data'],
            'ocr_time': ocr_result['ocr_time']
        }
        
        # 验证必要字段是否存在
        required_fields = {
            '身份证': ['姓名', '身份证号'],
            '安全生产许可证': ['证书编号', '姓名', '有效期至'],
            '特种作业操作证': ['证书编号', '姓名', '有效期至', '工种']
        }
        
        cert_type = ocr_result['cert_type']
        if cert_type in required_fields:
            missing_fields = []
            for field in required_fields[cert_type]:
                if not ocr_result['data'].get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                key_info['status'] = 'incomplete'
                key_info['missing_fields'] = missing_fields
                key_info['warning'] = f"缺少必要字段: {', '.join(missing_fields)}"
        
        return key_info
    
    def format_ocr_result(self, ocr_result):
        """
        格式化OCR结果为易读格式
        
        参数:
            ocr_result: OCR识别结果
        
        返回:
            str: 格式化的字符串
        """
        if not ocr_result['success']:
            return f"[识别失败] {ocr_result.get('error', '未知错误')}"
        
        lines = [
            f"证件类型: {ocr_result['cert_type']}",
            f"识别置信度: {ocr_result['confidence']:.2%}",
            "识别内容:"
        ]
        
        for key, value in ocr_result['data'].items():
            if value is not None:
                lines.append(f"  {key}: {value}")
        
        lines.append(f"识别时间: {ocr_result['ocr_time']}")
        
        return "\n".join(lines)


def demo_ocr_usage():
    """演示OCR模块的使用方法"""
    print("="*60)
    print("OCR模拟器演示")
    print("="*60)
    
    # 创建OCR模拟器实例
    ocr = OCRSimulator(accuracy=0.95)
    
    # 模拟单个证件识别
    print("\n1. 单个身份证识别:")
    print("-"*60)
    result1 = ocr.mock_ocr_scan('images/id_card_001.jpg', '身份证')
    print(ocr.format_ocr_result(result1))
    
    print("\n2. 单个安全生产许可证识别:")
    print("-"*60)
    result2 = ocr.mock_ocr_scan('images/safety_cert_001.jpg', '安全生产许可证')
    print(ocr.format_ocr_result(result2))
    
    # 提取关键信息
    print("\n3. 提取关键信息:")
    print("-"*60)
    key_info = ocr.extract_key_info(result2)
    print(json.dumps(key_info, ensure_ascii=False, indent=2))
    
    # 批量识别演示
    print("\n4. 批量识别演示:")
    print("-"*60)
    image_paths = [f'images/cert_{i:03d}.jpg' for i in range(1, 11)]
    results = ocr.batch_ocr_scan(image_paths, '特种作业操作证')
    
    print("\n" + "="*60)
    print("演示完成")
    print("="*60)


if __name__ == "__main__":
    demo_ocr_usage()

