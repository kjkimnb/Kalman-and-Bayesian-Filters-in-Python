#!/usr/bin/env bash
# 构建中文版全书 PDF：封面、可跳转目录、代码运行结果（含图片）
set -euo pipefail

cd "$(dirname "$0")"
PDF_DIR="$PWD"
OUT_PDF="$(dirname "$PDF_DIR")/Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf"

EXECUTE=1
for arg in "$@"; do
  if [[ "$arg" == "--no-execute" ]]; then
    EXECUTE=0
  fi
done

echo "==> 1/4 准备 tmp 目录"
if [[ "$EXECUTE" -eq 1 ]]; then
  python3 prepare_tmp.py
else
  python3 prepare_tmp.py --no-execute
fi

echo "==> 2/4 合并章节"
python3 merge_book.py

echo "==> 3/4 导出 HTML 并渲染 PDF（封面 + 目录 + 输出）"
python3 export_book_pdf.py

echo "==> 完成: $OUT_PDF"
ls -lh "$OUT_PDF"
