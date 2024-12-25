from paddleocr import PaddleOCR
import os
from typing import List, Tuple, Optional

class ImageOCR:
    def __init__(self, use_gpu: bool = False):
        """
        初始化OCR识别器
        
        参数:
        use_gpu: 是否使用GPU，默认False
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # 使用方向分类器
            lang="ch",  # 中英文模型
            use_gpu=use_gpu,
            show_log=False
        )
    
    def recognize_image(self, image_path: str) -> Optional[List[Tuple[List[List[int]], str, float]]]:
        """
        识别单张图片中的文字
        
        参数:
        image_path: 图片路径
        
        返回:
        List[Tuple[List[List[int]], str, float]]: 识别结果列表
            - List[List[int]]: 文字框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            - str: 识别的文字
            - float: 置信度
        """
        if not os.path.exists(image_path):
            print(f"错误：图片不存在: {image_path}")
            return None
            
        try:
            result = self.ocr.ocr(image_path, cls=True)
            if result is None or len(result) == 0:
                print(f"警告：未在图片中识别到文字: {image_path}")
                return None
                
            return result[0]
        except Exception as e:
            print(f"处理图片时出错 {image_path}: {str(e)}")
            return None
    
    def get_text_only(self, image_path: str) -> Optional[List[str]]:
        """
        只返回识别的文字内容
        
        参数:
        image_path: 图片路径
        
        返回:
        List[str]: 识别出的文字列表
        """
        result = self.recognize_image(image_path)
        if result is None:
            return None
        
        return [line[1][0] for line in result]  # 提取文字内容

def process_image(image_path: str, use_gpu: bool = False) -> Optional[List[str]]:
    """
    处理单张图片的便捷函数
    
    参数:
    image_path: 图片路径
    use_gpu: 是否使用GPU
    
    返回:
    List[str]: 识别出的文字列表
    """
    ocr = ImageOCR(use_gpu=use_gpu)
    return ocr.get_text_only(image_path)

if __name__ == "__main__":
    import argparse
    
    # parser = argparse.ArgumentParser(description='图片文字识别')
    # parser.add_argument('image_path', help='图片路径')
    # parser.add_argument('--gpu', action='store_true', help='是否使用GPU')
    
    # args = parser.parse_args()
    
    # 处理图片
    # texts = process_image(args.image_path, args.gpu)
    
    image_path = '/mnt/shiyue/zhaohongyu/offline_project/ocr/minerU/output/gartner_官网/202402 _Gartner_Business Alignment Tool/images/0c71c0fa7a97429c4b62f86ce4726a5342c4ff6cd77497e4925a204aabfe66b5.jpg'
    texts = process_image(image_path, True)
    
    if texts:
        print("\n识别结果：")
        for i, text in enumerate(texts, 1):
            print(f"{i}. {text}")
    else:
        print("未能成功识别文字")
