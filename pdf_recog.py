import os
from minerU_call import process_pdf

def process_directory(input_dir):
    """
    处理指定目录下的所有PDF文件
    
    参数:
    input_dir (str): 输入目录路径（data目录下的子目录）
    """
    # 获取输入目录的名称作为输出目录名
    dir_name = os.path.basename(os.path.normpath(input_dir))
    output_base_dir = f'output/{dir_name}'
    
    # 确保输出目录存在
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 遍历目录
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                try:
                    print(f"\n开始处理PDF文件: {pdf_path}")
                    markdown_path, images_dir = process_pdf(pdf_path, output_base_dir)
                    print(f"处理完成。输出文件：\nMarkdown: {markdown_path}\n图片目录: {images_dir}")
                except Exception as e:
                    print(f"处理文件 {pdf_path} 时出错: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='批量处理PDF文件')
    parser.add_argument('input_dir', help='输入目录路径（data目录下的子目录）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"错误：输入目录 {args.input_dir} 不存在")
        exit(1)
        
    print(f"开始处理目录: {args.input_dir}")
    print(f'输出目录: output/{os.path.basename(os.path.normpath(args.input_dir))}')
    # process_directory(args.input_dir)