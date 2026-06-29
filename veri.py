# veri.py
import json
import os
import glob
import datetime

try:
    import psycopg2
except ImportError:
    psycopg2 = None

aktif_kullanici = "Bilinmiyor"
aktif_link = ""
conn = None 

KULLANICILAR = []
KONUMLAR = [] 
MALZEMELER = []
GECMIS = []

UNDO_STACK = []
REDO_STACK = []

DOSYA_YOLU = "yerel_hafiza.json"

def _hafizayi_oku():
    if os.path.exists(DOSYA_YOLU):
        try:
            with open(DOSYA_YOLU, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def _hafizaya_yaz(data):
    with open(DOSYA_YOLU, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def anim_kaydet():
    durum = {"kullanicilar": list(KULLANICILAR), "konumlar": list(KONUMLAR), "malzemeler": [dict(m) for m in MALZEMELER], "gecmis": list(GECMIS)}
    UNDO_STACK.append(json.dumps(durum)); REDO_STACK.clear()

def geri_al_motoru():
    global KULLANICILAR, KONUMLAR, MALZEMELER, GECMIS
    if not UNDO_STACK: return False
    REDO_STACK.append(json.dumps({"kullanicilar": list(KULLANICILAR), "konumlar": list(KONUMLAR), "malzemeler": [dict(m) for m in MALZEMELER], "gecmis": list(GECMIS)}))
    eski_durum = json.loads(UNDO_STACK.pop())
    KULLANICILAR[:] = eski_durum["kullanicilar"]; KONUMLAR[:] = eski_durum["konumlar"]; MALZEMELER[:] = eski_durum["malzemeler"]; GECMIS[:] = eski_durum["gecmis"]
    verileri_kaydet(); return True

def ileri_al_motoru():
    global KULLANICILAR, KONUMLAR, MALZEMELER, GECMIS
    if not REDO_STACK: return False
    UNDO_STACK.append(json.dumps({"kullanicilar": list(KULLANICILAR), "konumlar": list(KONUMLAR), "malzemeler": [dict(m) for m in MALZEMELER], "gecmis": list(GECMIS)}))
    sonraki_durum = json.loads(REDO_STACK.pop())
    KULLANICILAR[:] = sonraki_durum["kullanicilar"]; KONUMLAR[:] = sonraki_durum["konumlar"]; MALZEMELER[:] = sonraki_durum["malzemeler"]; GECMIS[:] = sonraki_durum["gecmis"]
    verileri_kaydet(); return True

def baglanti_kur(link):
    global aktif_link, conn, KULLANICILAR, KONUMLAR, MALZEMELER, GECMIS
    if psycopg2 is None or not link.startswith("postgres"): return False, "Geçersiz Bağlantı!"
    try:
        conn = psycopg2.connect(link)
        conn.autocommit = True
        aktif_link = link
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS lab_bulut_verisi (id INT PRIMARY KEY, veri JSON)")
            cur.execute("SELECT veri FROM lab_bulut_verisi WHERE id=1")
            satir = cur.fetchone()
            if satir:
                data = satir[0]
                KULLANICILAR = data.get("kullanicilar", [])
                KONUMLAR = data.get("konumlar", [])
                MALZEMELER = data.get("malzemeler", [])
                GECMIS = data.get("gecmis", [])
            else:
                KULLANICILAR = []; KONUMLAR = []; MALZEMELER = []; GECMIS = []
                cur.execute("INSERT INTO lab_bulut_verisi (id, veri) VALUES (1, %s)", (json.dumps({"kullanicilar":[], "konumlar":[], "malzemeler":[], "gecmis":[]}),))
        hafiza = _hafizayi_oku(); hafiza["son_link"] = link; _hafizaya_yaz(hafiza)
        return True, "Bağlantı Başarılı!"
    except: return False, "Bağlantı Başarısız!"

def verileri_kaydet():
    global conn
    if not conn: return
    data_dict = {"kullanicilar": KULLANICILAR, "konumlar": KONUMLAR, "malzemeler": MALZEMELER, "gecmis": GECMIS}
    try:
        # 1. GERÇEK BULUTA YAZ
        with conn.cursor() as cur: cur.execute("UPDATE lab_bulut_verisi SET veri = %s WHERE id=1", (json.dumps(data_dict),))
        
        # 2. OTOMATİK 5'Lİ YEDEKLEME SİSTEMİ (Bilgisayarına yedekler)
        if not os.path.exists("Yedekler"): os.makedirs("Yedekler")
        zaman = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"Yedekler/oto_yedek_{zaman}.json", "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False)
            
        dosyalar = sorted(glob.glob("Yedekler/oto_yedek_*.json"))
        while len(dosyalar) > 5: os.remove(dosyalar.pop(0)) # En eskiyi sil, 5 tane tut
            
    except Exception as e: print(e)

def baglantiyi_kes():
    global aktif_link, conn; aktif_link = ""
    if conn: conn.close(); conn = None
    hafiza = _hafizayi_oku()
    if "son_link" in hafiza: del hafiza["son_link"]; _hafizaya_yaz(hafiza)

def son_linki_getir(): return _hafizayi_oku().get("son_link", "")

# YENİ: PostgreSQL'den Gerçek Boyutu Hesaplar
def bulut_boyutunu_getir():
    global conn
    if not conn: return 0.0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_database_size(current_database())")
            boyut_bytes = cur.fetchone()[0]
            boyut_mb = boyut_bytes / (1024 * 1024)
            return round(boyut_mb, 2)
    except: return 0.0