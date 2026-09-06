import pytest
from app.services.parser import detect_platform
from app.services.doc_generator import generate_docx, generate_txt
from pathlib import Path

def test_detect_platform_douyin():
    assert detect_platform('https://v.douyin.com/abc123/') == 'douyin'
    assert detect_platform('https://www.douyin.com/video/123') == 'douyin'
    assert detect_platform('https://tiktok.com/video/123') == 'douyin'

def test_detect_platform_hongguo():
    assert detect_platform('https://hongguo.example.com/video/123') == 'hongguo'
    assert detect_platform('https://novelquickapp.com/abc') == 'hongguo'
    assert detect_platform('https://changdunovel.com/video/1') == 'hongguo'

def test_detect_platform_unknown():
    assert detect_platform('https://example.com/video') == 'unknown'
    assert detect_platform('not a url') == 'unknown'

def test_generate_txt(tmp_path):
    content = 'Test script content\nLine 2\n1-1 日 内 客厅'
    output = tmp_path / 'test.txt'
    result = generate_txt(content, output)
    assert result.exists()
    assert result.read_text(encoding='utf-8') == content

def test_generate_docx(tmp_path):
    content = '《测试剧本》第1集\n\n1-1 日 内 客厅\n人物：角色A\n▲【字幕：开场】\n角色A：你好\n角色B：你好啊'
    output = tmp_path / 'test.docx'
    result = generate_docx(content, '测试剧本', output)
    assert result.exists()
    assert result.stat().st_size > 0
