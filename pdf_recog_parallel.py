import os
import time
import concurrent.futures
from typing import List
from pdf_recog import process_directory
import gc

def get_output_dir(input_dir: str) -> str:
    """
    根据输入目录生成对应的输出目录名
    """
    return f'output/{os.path.basename(os.path.normpath(input_dir))}'

def process_with_retry(input_dir: str, max_retries: int = 3, delay: int = 5):
    """
    带重试机制的处理函数
    
    参数:
    input_dir: 输入目录
    max_retries: 最大重试次数
    delay: 重试间隔（秒）
    """
    for attempt in range(max_retries):
        try:
            process_directory(input_dir)
            print(f"\n成功处理目录: {input_dir}")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"\n处理 {input_dir} 时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                print(f"等待 {delay} 秒后重试...")
                gc.collect()  # 强制垃圾回收
                time.sleep(delay)
            else:
                print(f"\n处理 {input_dir} 失败，已达到最大重试次数: {str(e)}")
                return False

def count_pdf_files(input_dir_list: List[str]) -> int:
    """
    计算所有输入目录中PDF文件的总数
    
    参数:
    input_dir_list: 输入目录列表
    
    返回:
    int: PDF文件总数
    """
    pdf_count = 0
    for input_dir in input_dir_list:
        for root, _, files in os.walk(input_dir):
            pdf_count += sum(1 for file in files if file.lower().endswith('.pdf'))
    return pdf_count

def process_parallel(input_dir_list: List[str], max_workers: int = 2):
    """
    并行处理多个输入目录
    
    参数:
    input_dir_list: 输入目录列表
    max_workers: 最大并行工作进程数，默认为2
    """
    # 首先检查所有输入目录是否存在
    for input_dir in input_dir_list:
        if not os.path.exists(input_dir):
            print(f"错误：输入目录不存在: {input_dir}")
            return

    # 打印处理信息
    print("开始并行处理以下目录：")
    for input_dir in input_dir_list:
        output_dir = get_output_dir(input_dir)
        print(f"输入：{input_dir} -> 输出：{output_dir}")

    # 计算并打印PDF文件总数
    total_pdf_files = count_pdf_files(input_dir_list)
    print(f"\n从 input_dir_list 中一共读取了 {total_pdf_files} 个PDF文件")

    # 使用进程池并行处理
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_with_retry, input_dir) for input_dir in input_dir_list]
        
        # 处理完成的任务
        for future, input_dir in zip(concurrent.futures.as_completed(futures), input_dir_list):
            try:
                success = future.result()
                if not success:
                    print(f"\n目录处理失败: {input_dir}")
            except Exception as e:
                print(f"\n处理目录时发生异常 {input_dir}: {str(e)}")

if __name__ == "__main__":
    input_dirs = ['./data/gartner_官网/','/mnt/shiyue/zhaohongyu/offline_project/ocr/minerU/data/241129_╠┌╤╢╧ю─┐_╣┘═°_72╕ЎPDF']
    works = 2  # 设置为2个进程并行处理
    process_parallel(input_dir_list=input_dirs, max_workers=works)