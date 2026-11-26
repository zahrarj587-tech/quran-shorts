import urllib.request
import urllib.parse
import json
import getpass
import os
import hmac
import hashlib

def call_get(url, params):
    try:
        encoded_params = urllib.parse.urlencode(params)
        full_url = f"{url}?{encoded_params}"
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"error": {"message": f"HTTP {e.code}: {error_body}"}}

print("--- إعداد توكن فيسبوك طويل الأمد (نسخة محسنة 2) ---")
print("1. الصق الـ App ID هنا:")
app_id = input().strip()
print("2. الصق الـ App Secret هنا (مش هيظهر على الشاشة):")
secret = getpass.getpass("").strip()
print("3. الصق الـ Page ID هنا:")
page_id = input().strip()
print("4. الصق الـ Short Token هنا (مش هيظهر على الشاشة):")
short_token = getpass.getpass("").strip()

print("\n⏳ جاري تبديل التوكن...")

# 1. تبديل التوكن القصير بتوكن طويل الأمد
token_url = "https://graph.facebook.com/v23.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": app_id,
    "client_secret": secret,
    "fb_exchange_token": short_token
}

r = call_get(token_url, params)
long_t = r.get("access_token")

if not long_t:
    error_msg = r.get("error", {}).get("message", "خطأ غير معروف")
    raise SystemExit(f"❌ فشل تبديل التوكن: {error_msg}")
    
print("✅ تم تبديل التوكن لطويل الأمد")

# 2. عمل توقيع أمان (App Secret Proof)
appsecret_proof = hmac.new(secret.encode(), long_t.encode(), hashlib.sha256).hexdigest()

# 3. جلب توكن الصفحة الدائم مع التوقيع
accounts_url = "https://graph.facebook.com/v23.0/me/accounts"
accounts_params = {
    "access_token": long_t, 
    "limit": 100, 
    "appsecret_proof": appsecret_proof
}

r = call_get(accounts_url, accounts_params)
pages = r.get("data", [])

if not pages:
    # هيطبع رسالة الخطأ الحقيقية من فيسبوك لو القائمة فاضية
    print(f"❌ فيسبوك رجع قائمة فاضية. رد فيسبوك: {r}")
    raise SystemExit("تأكد من صلاحية business_management في التوكن القصير.")

page = next((p for p in pages if p["id"] == page_id), None)

if not page:
    print(f"❌ مش لاقي صفحة بالـ ID ده: {page_id}")
    for p in pages:
        print(f" - صفحة متاحة: {p['id']} | {p['name']}")
    raise SystemExit(1)

page_token = page["access_token"]
print(f"✅ تم جلب توكن لصفحة: {page['name']}")

# 4. حفظ التوكن في ملف آمن
file_path = os.path.expanduser("~/fb_page_token.txt")
fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.write(fd, page_token.encode())
os.close(fd)
print(f"🎉 تم الحفظ في {file_path} بنجاح!")
