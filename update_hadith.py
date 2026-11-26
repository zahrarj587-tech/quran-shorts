with open("islamic_content.py", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "# 2. دالة الحديث (عربي)"
end_marker = "# 3. دالة السيرة النبوية"

if start_marker in content and end_marker in content:
    part1 = content.split(start_marker)[0]
    part2 = content.split(end_marker)[1]
    
    new_hadith_func = '''# 2. دالة الحديث (مختار ومشروح)
def get_random_hadith():
    try:
        with open("hadiths.json", "r", encoding="utf-8") as f:
            hadiths = json.load(f)
        item = random.choice(hadiths)
        return f"🕌 حديث نبوي:\n\nعن النبي ﷺ قال:\n\\"{item['hadith']}\\"\n\n📝 الشرح:\n{item['sharh']}\n\n📚 المصدر: {item['source']}"
    except Exception:
        return "🕌 الحديث غير متاح حالياً."

'''
    new_content = part1 + new_hadith_func + end_marker + part2
    with open("islamic_content.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ تم تحديث دالة الحديث بنجاح!")
else:
    print("❌ لم أجد مكان دالة الحديث.")
