# MinerU OCR 工具集

这是一个基于[MinerU](https://github.com/opendatalab/MinerU)的PDF文档处理工具集，支持PDF文档解析和图片文字识别。

## 声明

本项目基于[MinerU](https://github.com/opendatalab/MinerU)开发，遵循原项目的开源协议。感谢MinerU团队提供的优秀工具。

## 环境要求

1. Python环境
   - Python 3.10+（具体版本要求请参考[MinerU](https://github.com/opendatalab/MinerU)项目）
   - 推荐使用Conda创建虚拟环境

2. 创建虚拟环境
```bash
# 创建conda环境
conda create -n mineru python=3.10
conda activate mineru

# 安装MinerU
pip install magic-pdf

# 安装其他依赖
pip install -r requirements.txt
```

## 功能特点

1. PDF文档处理
   - 支持单个PDF文件处理
   - 支持批量并行处理多个PDF文件
   - 自动提取文本和图片
   - 生成markdown格式的输出
   - 保存提取的图片
   - 支持特殊字符路径处理

2. 图片OCR识别
   - 支持中英文混合识别
   - 支持GPU加速
   - 自动检测文字方向
   - 返回文字位置和置信度

3. Markdown增强处理
   - 自动识别markdown中的图片
   - OCR识别图片中的文字
   - 在原图链接前添加识别文字
   - 保持原有目录结构输出

## 目录结构

```
minerU/
├── data/                # PDF文件存放目录
│   ├── gartner_官网/    # 示例PDF目录
│   └── pdf/            # 示例PDF目录
├── output/             # 处理结果输出目录
├── output_with_ocr/    # 增强处理后的输出目录
├── minerU_call.py      # PDF处理核心功能
├── run.py             # 单个目录处理脚本
├── run_parallel.py    # 并行处理多个目录脚本
├── image_ocr.py       # 图片文字识别脚本
├── image_ocr_parallel.py  # 并行图片处理脚本
├── pdf_recog.py       # PDF处理基础功能
├── pdf_recog_parallel.py  # 并行PDF处理脚本
└── process_markdown_images.py  # Markdown图片处理脚本
```

## 使用说明

### 1. PDF文档处理

#### 单个目录处理
```bash
python run.py data/your_pdf_folder
```
- 输入：PDF文件所在目录
- 输出：在`output/your_pdf_folder`下生成处理结果

#### 并行处理多个目录
```bash
python run_parallel.py
```
- 默认处理`data/gartner_官网/`和`data/pdf/`两个目录
- 可以在脚本中修改`input_dirs`列表添加更多目录
- 使用进程池实现并行处理
- 支持失败重试机制

### 2. 图片OCR识别

```bash
python image_ocr.py 图片路径 [--gpu]
```

也可以在代码中调用：
```python
# 方式1：直接处理单张图片
from image_ocr import process_image
texts = process_image("path/to/image.jpg", use_gpu=True)

# 方式2：批量处理多张图片
from image_ocr import ImageOCR
ocr = ImageOCR(use_gpu=True)
texts = ocr.get_text_only("path/to/image.jpg")
```

### 3. Markdown图片处理

```bash
python process_markdown_images.py
```

功能说明：
- 读取`output`目录下的所有markdown文件
- 识别文件中的图片链接
- 使用OCR识别图片内容
- 在图片链接前添加识别文字，格式如下：
  ```markdown
  """图片
  识别的文字内容
  图片"""
  ![图片描述](图片路径)
  ```
- 在`output_with_ocr`目录下保持原有目录结构输出结果
- 自动复制和处理图片文件

处理流程：
1. 扫描输入目录下所有markdown文件
2. 提取每个文件中的图片链接
3. 使用OCR识别图片内容
4. 生成新的markdown文件
5. 保持原有目录结构输出

## 输出格式

### PDF处理输出
- 每个PDF文件会在output目录下创建对应的子目录
- 生成markdown格式的文本内容
- 图片保存在`images/`子目录下

### OCR识别输出
- 返回识别出的文字列表
- 可选返回文字位置坐标和置信度

### Markdown增强处理输出
- 在`output_with_ocr`目录下保持原有目录结构输出结果
- 自动生成新的markdown文件

## 依赖要求

主要依赖：
- magic-pdf (MinerU核心包)
- paddleocr >= 2.7.0
- paddlepaddle-gpu >= 2.5.1
- 其他依赖见requirements.txt

## 注意事项

1. GPU支持
   - 需要安装CUDA和cuDNN
   - 使用`--gpu`参数开启GPU加速

2. 内存使用
   - PDF处理可能需要较大内存
   - 可以通过调整并行进程数控制内存使用

3. 错误处理
   - 包含自动重试机制
   - 单个文件失败不影响其他文件处理
   - 详细的错误日志输出

4. 路径处理
   - 支持包含特殊字符的路径
   - 自动规范化路径格式
   - 保持原有目录结构

5. 输出目录
   - PDF处理结果输出到`output`目录
   - 增强处理结果输出到`output_with_ocr`目录
   - 每个处理阶段使用独立的输出目录

## 开发说明

1. 添加新功能
   - 在`minerU_call.py`中添加新的PDF处理功能
   - 在`image_ocr.py`中扩展OCR功能
   - 在`process_markdown_images.py`中扩展Markdown图片处理功能

2. 性能优化
   - 调整`max_workers`参数控制并行度
   - 使用GPU加速OCR处理
   - 根据需要调整重试参数
