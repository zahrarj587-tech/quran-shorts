import json, os, datetime

# توقيت مصر
now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
print(f"🕒 الوقت الحالي (مصر): {now.strftime('%Y-%m-%d %I:%M %p')}")

# 1. معرفة الميعاد القادم
try:
    with open("slots.json", "r") as f:
        slots = json.load(f)
    
    future_slots = []
    for s in slots:
        h, m = map(int, s["time"].split(":"))
        slot_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if slot_time > now:
            future_slots.append((slot_time, s))
            
    if future_slots:
        next_time, next_slot = min(future_slots, key=lambda x: x[0])
        print(f"⏭️ الميعاد القادم: {next_time.strftime('%I:%M %p')} (النوع: {next_slot['type']})")
    else:
        print("⏭️ مفيش مواعيد قادمة النهاردة، البوت هكمل بكرة.")
except Exception as e:
    print("❌ مشكلة في قراءة ملف المواعيد:", e)

# 2. حالة النشر (يوتيوب وفيسبوك)
print("\n📊 آخر 3 عمليات نشر (من سجل البوت):")
try:
    with open("stats.json", "r") as f:
        stats = json.load(f)
        
    logs = stats.get("log", [])[-3:]
    if not logs:
        print("لسه مفيش سجل نشر بالكامل.")
        
    for log in reversed(logs):
        date_str = log.get('t', '')[:16].replace('T', ' ')
        yt_id = log.get('yt', 'لا يوجد')
        if yt_id != 'لا يوجد':
            print(f"✅ فيديو: {log.get('title', '')[:20]}... | يوتيوب: نعم | فيسبوك: نعم")
        else:
            print(f"✅ بوست نصي | تم النشر بنجاح")
            
    # التحقق من المواعيد المكتملة (البوستات النصية)
    slots_done = stats.get("slots", [])
    if slots_done:
         print(f"📝 إجمالي المواعيد المكتملة: {len(slots_done)}")
         
except Exception as e:
    print("❌ مشكلة في قراءة سجل النشر:", e)
