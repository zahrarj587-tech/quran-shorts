import requests
RECITERS = {
 "Alafasy_128kbps": "مشاري العفاسي",
 "Abdul_Basit_Murattal_192kbps": "عبد الباسط عبد الصمد",
 "Husary_128kbps": "محمود خليل الحصري",
 "Minshawy_Murattal_128kbps": "محمد صديق المنشاوي",
 "Hudhaify_128kbps": "علي الحذيفي",
 "Ghamadi_40kbps": "سعد الغامدي",
 "Abdurrahmaan_As-Sudais_192kbps": "عبد الرحمن السديس",
 "Saood_ash-Shuraym_128kbps": "سعود الشريم",
 "MaherAlMuaiqly128kbps": "ماهر المعيقلي",
 "Hani_Rifai_192kbps": "هاني الرفاعي",
 "Abdullah_Basfar_192kbps": "عبد الله بصفر",
 "Abu_Bakr_Ash-Shaatree_128kbps": "أبو بكر الشاطري",
 "Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net": "أحمد العجمي",
 "Nasser_Alqatami_128kbps": "ناصر القطامي",
 "Yasser_Ad-Dussary_128kbps": "ياسر الدوسري",
 "Muhammad_Ayyoub_128kbps": "محمد أيوب",
 "Muhammad_Jibreel_128kbps": "محمد جبريل",
 "Salah_Al_Budair_128kbps": "صلاح البدير",
 "Ali_Jaber_64kbps": "علي جابر",
 "Salaah_AbdulRahman_Bukhatir_128kbps": "صلاح بو خاطر",
 "Fares_Abbad_64kbps": "فارس عباد",
 "Khalefa_Al_Tunaiji_64kbps": "خليفة الطنيجي",
 "Abdullaah_3awwaad_Al-Juhaynee_128kbps": "عبد الله الجهني",
 "Muhsin_Al_Qasim_192kbps": "محسن القاسم",
 "Mustafa_Ismail_48kbps": "مصطفى إسماعيل",
 "Mahmoud_Ali_Al_Banna_32kbps": "محمود علي البنا",
 "Ayman_Sowaid_64kbps": "أيمن سويد",
 "Ibrahim_Akhdar_32kbps": "إبراهيم الأخضر",
}
RECITERS.update({
 "Abdul_Basit_Mujawwad_128kbps": "عبد الباسط عبد الصمد (مجوّد)",
 "Minshawy_Mujawwad_192kbps": "محمد صديق المنشاوي (مجوّد)",
 "Husary_128kbps_Mujawwad": "محمود خليل الحصري (مجوّد)",
 "Idrees_Abkar_128kbps": "إدريس أبكر",
 "Abdullah_Matroud_128kbps": "عبد الله مطرود",
 "Ahmed_Neana_128kbps": "أحمد نعينع",
 "Khaalid_Abdullaah_al-Qahtaanee_192kbps": "خالد القحطاني",
 "Mohammad_al_Tablaway_128kbps": "محمد الطبلاوي",
 "Ali_Hajjaj_AlSuesy_128kbps": "علي الحجاج السويسي",
 "Sahl_Yassin_128kbps": "سهل ياسين",
 "Muhammad_Abdulkareem_128kbps": "محمد عبد الكريم",
 "Yaser_Salamah_128kbps": "ياسر سلامة",
 "Akram_AlAlaqimy_128kbps": "أكرم العلاقمي",
 "Karim_Mansoori_40kbps": "كريم منصوري",
 "Nabil_Rifa3i_48kbps": "نبيل الرفاعي",
})
_ok = None
def available():
    global _ok
    if _ok is None:
        _ok = []
        for k in RECITERS:
            try:
                r = requests.get(f"https://everyayah.com/data/{k}/001001.mp3", stream=True, timeout=20)
                if r.status_code == 200:
                    _ok.append(k)
                r.close()
            except Exception:
                pass
        if not _ok:
            _ok = ["Alafasy_128kbps"]
    return _ok
def pick(n):
    a = available()
    return a[n % len(a)]
if __name__ == "__main__":
    for k in RECITERS:
        print("OK" if k in available() else "NO", k)
