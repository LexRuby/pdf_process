# 并发处理 pdf

nohup python3 -u pdf_recog_parallel.py > pdf_recog_parallel.log 2>&1 &
echo "Log file: $(pwd)/pdf_recog_parallel.log"



