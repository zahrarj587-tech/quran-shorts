import re

with open("run.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. إصلاح السطر المقطوع بتاع التفسير
code = re.sub(r'tafsir_section = f"\\n\s*', 'tafsir_section = f"\\n\\n📝 {tafsir_source}:\\n{tafsir_text}\\n"\n', code)

# 2. مسح كود البوستات من مكانه الغلط
pattern = re.compile(r'import sys\nfrom islamic_content import get_facebook_post.*?sys\.exit\(0\)\n', re.DOTALL)
match = pattern.search(code)

if match:
    injected_block = match.group(0)
    # مسحه من النص الأصلي
    code = code.replace(injected_block, '')
    
    # إضافته في أول الملف (بعد أول سطرين)
    lines = code.split('\n')
    # ندور على أول سطر فيه import عشان نحط الكود بعده
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
            
    lines.insert(insert_idx, injected_block)
    code = '\n'.join(lines)
    print("✅ تم إصلاح الكود ونقل جزء البوستات للمكان الصح!")
else:
    print("⚠️ لم يتم العثور على كود البوستات، لكن تم إصلاح السطر المقطوع.")

with open("run.py", "w", encoding="utf-8") as f:
    f.write(code)
