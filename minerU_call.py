import os
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

def process_pdf(pdf_file_path,output_dir='./output'):
    """
    使用minerU处理PDF文件并输出markdown和图像。
    
    参数:
    pdf_file_path (str): 输入PDF文件的路径。
    
    返回:
    tuple: 包含输出markdown文件路径和图像目录路径的元组。
    """
    # 提取不带扩展名的文件名
    pdf_file_name = os.path.basename(pdf_file_path)
    name_without_suff = os.path.splitext(pdf_file_name)[0]
    
    # 准备输出目录
    output_dir = f"{output_dir}/{name_without_suff}"
    local_image_dir = os.path.join(output_dir, "images")
    os.makedirs(local_image_dir, exist_ok=True)
    print(f"创建输出目录: {output_dir}")

    # 初始化数据写入器
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(output_dir)
    
    # 读取PDF内容
    reader = FileBasedDataReader("")
    pdf_bytes = reader.read(pdf_file_path)
    print(f"读取PDF文件: {pdf_file_path}")

    # 创建数据集实例并处理
    ds = PymuDocDataset(pdf_bytes)
    
    # 确定处理方法并应用
    if ds.classify() == SupportedPdfParseMethod.OCR:
        print("使用OCR模式进行处理")
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    else:
        print("使用文本模式进行处理")
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)

    # 生成输出文件
    markdown_file = f"{name_without_suff}.md"
    pipe_result.dump_md(md_writer, markdown_file, "images")
    print(f"生成markdown文件: {os.path.join(output_dir, markdown_file)}")

    return os.path.join(output_dir, markdown_file), local_image_dir

# 使用示例
if __name__ == "__main__":
    input_pdf = "abc.pdf"  # 替换为实际的PDF路径
    markdown_path, images_dir = process_pdf(input_pdf)
    print(f"处理完成。Markdown: {markdown_path}, 图像: {images_dir}")