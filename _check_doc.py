# -*- coding: utf-8 -*-
"""导出 docx 为 PDF 并统计页数（独立进程调用 Word COM，确保退出）。"""
import os, sys, glob
import win32com.client as win32

src = r"c:\Users\kybll\Desktop\AIGC\keqiao-ip-studio\dist\[队伍编号]说明文档.docx"
pdf = os.path.join(os.environ['TEMP'], "kq_doc_check.pdf")

word = win32.gencache.EnsureDispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(src, ReadOnly=True)
    pages = doc.ComputeStatistics(2)
    words = doc.ComputeStatistics(0)
    chars = doc.ComputeStatistics(3)
    doc.ExportAsFixedFormat(pdf, 17)
    doc.Close(False)
    print("页数:", pages)
    print("字数:", words, "字符数:", chars)
    print("PDF:", pdf, os.path.getsize(pdf), "bytes")
finally:
    word.Quit()

import pymupdf
d = pymupdf.open(pdf)
out = os.path.join(os.environ['TEMP'], 'kq_doc_pages')
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, '*.png')):
    os.remove(f)
for i in range(d.page_count):
    pix = d.load_page(i).get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4))
    pix.save(os.path.join(out, f'p{i+1:02d}.png'))
print("渲染页数:", d.page_count, "->", out)
