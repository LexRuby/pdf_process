import os
import time
import concurrent.futures
from typing import List, Dict, Optional
import json
from image_ocr import ImageOCR
import gc

def get_output_path(image_path: str, output_dir: str) -> str:
    """
    根据图片路径生成对应的输出文件路径
    
    参数:
    image_path: 图片路径
    output_dir: 输出目录
    
    返回:
    str: 输出文件路径
    """
    # 获取图片文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # 构建输出路径
    return os.path.join(output_dir, f"{base_name}.txt")

def get_image_files(input_dir: str) -> List[str]:
    """
    获取目录下所有图片文件的路径
    
    参数:
    input_dir: 输入目录路径
    
    返回:
    List[str]: 图片文件路径列表
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    image_files = []
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if os.path.splitext(file.lower())[1] in image_extensions:
                image_files.append(os.path.join(root, file))
    
    return image_files

def save_result_to_txt(texts: List[str], output_path: str):
    """
    将识别结果保存到txt文件
    
    参数:
    texts: 识别出的文字列表
    output_path: 输出文件路径
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n')
    except Exception as e:
        print(f"保存文件时出错 {output_path}: {str(e)}")

def process_image_with_retry(image_path: str, output_dir: str, use_gpu: bool = False, 
                           max_retries: int = 3, delay: int = 5) -> Optional[Dict]:
    """
    带重试机制的图片处理函数
    
    参数:
    image_path: 图片路径
    output_dir: 输出目录
    use_gpu: 是否使用GPU
    max_retries: 最大重试次数
    delay: 重试间隔（秒）
    
    返回:
    Dict: 包含图片路径和识别结果的字典
    """
    output_path = get_output_path(image_path, output_dir)
    
    for attempt in range(max_retries):
        try:
            ocr = ImageOCR(use_gpu=use_gpu)
            texts = ocr.get_text_only(image_path)
            
            if texts:
                # 保存识别结果到txt文件
                save_result_to_txt(texts, output_path)
                result = {
                    'image_path': image_path,
                    'output_path': output_path,
                    'texts': texts,
                    'status': 'success'
                }
            else:
                result = {
                    'image_path': image_path,
                    'output_path': output_path,
                    'texts': [],
                    'status': 'no_text_found'
                }
                
            print(f"\n成功处理图片: {image_path}")
            print(f"结果已保存到: {output_path}")
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"\n处理图片 {image_path} 时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                print(f"等待 {delay} 秒后重试...")
                gc.collect()  # 强制垃圾回收
                time.sleep(delay)
            else:
                print(f"\n处理图片 {image_path} 失败，已达到最大重试次数: {str(e)}")
                return {
                    'image_path': image_path,
                    'output_path': output_path,
                    'error': str(e),
                    'status': 'error'
                }

def process_images_parallel(input_dir: str, output_dir: str,
                          max_workers: int = 2, use_gpu: bool = False):
    """
    并行处理目录下的所有图片
    
    参数:
    input_dir: 输入目录路径
    output_dir: 输出目录路径
    max_workers: 最大并行工作进程数
    use_gpu: 是否使用GPU
    """
    # 获取所有图片文件
    image_files = get_image_files(input_dir)
    if not image_files:
        print(f"错误：在目录 {input_dir} 中未找到图片文件")
        return
    
    print(f"\n找到 {len(image_files)} 个图片文件")
    print(f"输出目录: {output_dir}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    # 使用进程池并行处理
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_image_with_retry, img_path, output_dir, use_gpu) 
                  for img_path in image_files]
        
        # 处理完成的任务
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"\n处理任务时发生异常: {str(e)}")
    
    # 保存处理报告
    report_path = os.path.join(output_dir, 'processing_report.json')
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n处理报告已保存到: {report_path}")
    except Exception as e:
        print(f"\n保存处理报告时出错: {str(e)}")

if __name__ == "__main__":
    # 设置输入输出路径
    input_dir = '/mnt/shiyue/zhaohongyu/offline_project/ocr/minerU/data/241203_╠┌╤╢╧ю─┐_╗с╥щ_226╕Ў'
    output_dir = os.path.join('output', 'ocr_results', os.path.basename(input_dir))
    
    print(f"开始处理目录: {input_dir}")
    
    # 开始并行处理
    process_images_parallel(
        input_dir=input_dir,
        output_dir=output_dir,
        max_workers=2,  # 可以根据需要调整并行数
        use_gpu=True    # 使用GPU加速
    )
