from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_docx(content: str, title: str, output_path: Path) -> Path:
    """Generate a .docx file from script content."""
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Microsoft YaHei'
    font.size = Pt(11)
    
    # Title
    heading = doc.add_heading(title, level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Content lines
    for line in content.split("\n"):
        line = line.rstrip()
        if not line:
            doc.add_paragraph("")
            continue
            
        p = doc.add_paragraph()
        
        # Scene headers (e.g., "1-1 日 内 客厅")
        if len(line) > 2 and line[0].isdigit() and "-" in line[:5]:
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(12)
        # Action/camera cues starting with triangle
        elif line.startswith("▲"):
            run = p.add_run(line)
            run.italic = True
        # Character dialogue
        elif "：" in line and not line.startswith("▲") and not line.startswith("【"):
            parts = line.split("：", 1)
            run_name = p.add_run(parts[0] + "：")
            run_name.bold = True
            run_text = p.add_run(parts[1])
        else:
            p.add_run(line)
    
    doc.save(str(output_path))
    return output_path

def generate_txt(content: str, output_path: Path) -> Path:
    """Save content as plain text file."""
    output_path.write_text(content, encoding='utf-8')
    return output_path
