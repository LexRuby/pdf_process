import os
import re
from typing import List, Tuple
from image_ocr import ImageOCR
import concurrent.futures
import time
import gc
import shutil

def get_new_output_path(markdown_path: str, input_base_dir: str, output_base_dir: str) -> str:
    """
    根据原始markdown路径生成新的输出路径
    
    参数:
    markdown_path: 原始markdown文件路径
    input_base_dir: 输入基础目录
    output_base_dir: 输出基础目录
    """
    # 获取相对路径
    rel_path = os.path.relpath(markdown_path, input_base_dir)
    # 构建新的输出路径
    return os.path.join(output_base_dir, rel_path)

def find_markdown_files(input_dir: str) -> List[str]:
    """
    在输入目录中查找所有markdown文件
    """
    markdown_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def extract_images_from_markdown(markdown_path: str) -> List[Tuple[str, str, int]]:
    """
    从markdown文件中提取图片路径和对应的行号
    
    返回: List[Tuple[图片完整路径, 原始图片链接文本, 行号]]
    """
    images = []
    markdown_dir = os.path.dirname(markdown_path)
    
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 匹配markdown中的图片链接
    image_pattern = r'!\[.*?\]\((.*?)\)'
    
    for line_num, line in enumerate(lines):
        matches = re.finditer(image_pattern, line)
        for match in matches:
            image_path = match.group(1)
            # 将相对路径转换为绝对路径
            abs_image_path = os.path.join(markdown_dir, image_path)
            if os.path.exists(abs_image_path):
                images.append((abs_image_path, match.group(0), line_num))
    
    return images

def process_image_with_retry(image_path: str, ocr: ImageOCR, 
                           max_retries: int = 3, delay: int = 5) -> List[str]:
    """
    带重试机制的图片OCR处理
    """
    for attempt in range(max_retries):
        try:
            texts = ocr.get_text_only(image_path)
            if texts:
                return texts
            return []
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"\n处理图片 {image_path} 时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                print(f"等待 {delay} 秒后重试...")
                gc.collect()
                time.sleep(delay)
    return []

def update_markdown_with_ocr(markdown_path: str, output_base_dir: str, input_base_dir: str, use_gpu: bool = False):
    """
    处理单个markdown文件中的图片，并输出到新位置
    """
    print(f"\n处理markdown文件: {markdown_path}")
    
    # 获取新的输出路径
    new_markdown_path = get_new_output_path(markdown_path, input_base_dir, output_base_dir)
    new_markdown_dir = os.path.dirname(new_markdown_path)
    
    # 创建输出目录
    os.makedirs(new_markdown_dir, exist_ok=True)
    
    # 提取图片信息
    images = extract_images_from_markdown(markdown_path)
    if not images:
        print(f"未在 {markdown_path} 中找到图片")
        # 如果没有图片，直接复制原文件
        shutil.copy2(markdown_path, new_markdown_path)
        return
    
    print(f"找到 {len(images)} 张图片")
    
    # 初始化OCR
    ocr = ImageOCR(use_gpu=use_gpu)
    
    # 读取原始文件内容
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 复制images目录到新位置
    old_images_dir = os.path.join(os.path.dirname(markdown_path), 'images')
    new_images_dir = os.path.join(new_markdown_dir, 'images')
    if os.path.exists(old_images_dir):
        shutil.copytree(old_images_dir, new_images_dir, dirs_exist_ok=True)
    
    # 处理每个图片并更新内容
    for image_path, original_text, line_num in images:
        texts = process_image_with_retry(image_path, ocr)
        
        if texts:
            # 构建新的文本内容
            ocr_text = '\n'.join(texts)
            replacement = f'''"""图片
{ocr_text}
图片"""
{original_text}'''
            
            # 更新行内容
            lines[line_num] = lines[line_num].replace(original_text, replacement)
            print(f"已处理图片: {image_path}")
        else:
            print(f"图片未识别出文字: {image_path}")
    
    # 保存到新位置
    with open(new_markdown_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"已保存处理结果到: {new_markdown_path}")

def process_markdown_parallel(input_dir: str, output_dir: str, max_workers: int = 2, use_gpu: bool = False):
    """
    并行处理输入目录中的所有markdown文件，并输出到新目录
    """
    # 查找所有markdown文件
    markdown_files = find_markdown_files(input_dir)
    if not markdown_files:
        print(f"在目录 {input_dir} 中未找到markdown文件")
        return
    
    print(f"\n找到 {len(markdown_files)} 个markdown文件")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 使用进程池并行处理
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(update_markdown_with_ocr, md_path, output_dir, input_dir, use_gpu) 
                  for md_path in markdown_files]
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"\n处理任务时发生异常: {str(e)}")

if __name__ == "__main__":
    # 设置输入和输出目录
    input_dir = "output"  # 原始PDF处理结果的目录
    output_dir = "output_with_ocr"  # 新的输出目录
    
    print(f"开始处理...")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 开始并行处理
    process_markdown_parallel(
        input_dir=input_dir,
        output_dir=output_dir,
        max_workers=2,  # 可以根据需要调整并行数
        use_gpu=True    # 使用GPU加速
    )
