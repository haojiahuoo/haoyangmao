import time, cv2, re
import numpy as np
from cnocr import CnOcr
from typing import List, Dict, Tuple, Optional

class SmartController:
    def __init__(self):
        # 初始化OCR
        self.ocr = CnOcr(
            det_model_name='db_shufflenet_v2',
            rec_model_name='densenet_lite_136-gru',
            box_score_thresh=0.3
        )
        
    def _analyze_elements(self, ocr_results: List[Dict], img_shape: Tuple[int], button_keywords: Optional[List[str]] = None) -> Dict:
        """分析OCR结果，识别按钮和关键文本"""
        h, w = img_shape[:2]
        buttons = []
        key_texts = []
        
        # 按钮特征：包含动作词且通常位于底部或右侧
        
        default_keywords = ["看视频"]
        # 如果传了自定义关键词，使用它；否则用默认值
        button_keywords = button_keywords or default_keywords
        for res in ocr_results:
            text = res['text'].strip()
            if not text:
                continue
                
            # 获取边界框坐标 (x1,y1,x2,y2)
            bbox = self._get_normalized_bbox(res['position'], w, h)
            # 识别按钮
            if any(keyword in text for keyword in button_keywords):
                buttons.append({
                    "text": text,
                    "bbox": bbox,
                    "center": self._get_center(bbox)
                })
            # 识别关键数值
            elif re.search(r'\d+\.?\d*(金币|现金|天|万)', text):
                key_texts.append({
                    "text": text,
                    "bbox": bbox,
                    "center": self._get_center(bbox)
                })
        
        return {
            "buttons": buttons,
            "key_texts": key_texts
        }
    
    def _get_normalized_bbox(self, positions: List[List[int]], img_w: int, img_h: int) -> List[int]:
        """将OCR返回的多边形框转为标准矩形框(x1,y1,x2,y2)并归一化"""
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        return [
            max(0, min(xs)/img_w),    # x1 (0~1)
            max(0, min(ys)/img_h),    # y1 (0~1)
            min(1, max(xs)/img_w),    # x2 (0~1)
            min(1, max(ys)/img_h)     # y2 (0~1)
        ]
    
    def _get_center(self, bbox: List[float]) -> Tuple[float, float]:
        """计算bbox中心点坐标(归一化)"""
        return ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)

    def visualize_results(self, image_path: str, output_path: str = None):
        """可视化检测结果"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("无法读取图片")
            
        elements = self.detect_clickable_elements(image_path)
        
        # 绘制按钮
        for btn in elements['buttons']:
            x1, y1, x2, y2 = [int(coord*img.shape[1 if i%2==0 else 0]) 
                            for i, coord in enumerate(btn['bbox'])]
            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(img, btn['text'], (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        
        # 绘制关键文本
        for text in elements['key_texts']:
            x1, y1, x2, y2 = [int(coord*img.shape[1 if i%2==0 else 0]) 
                            for i, coord in enumerate(text['bbox'])]
            cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), 1)
        
        if output_path:
            cv2.imwrite(output_path, img)
        else:
            cv2.imshow('Detection Results', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def detect_clickable_elements(self, screenshot_path: str, button_keywords: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """检测图片中所有可点击元素及其位置
        
        Returns:
            {
                "buttons": [{"text": "去提现", "bbox": [x1,y1,x2,y2]}...],
                "key_texts": [{"text": "815金币", "bbox": [...]}...]
            }
        """
        img = cv2.imread(screenshot_path)
        if img is None:
            raise ValueError("无法读取图片")
            
        # 获取OCR结果带位置信息
        ocr_results = self.ocr.ocr(img)
        
        # 分析布局
        elements = self._analyze_elements(ocr_results, img.shape, button_keywords=button_keywords)
        
        return elements
