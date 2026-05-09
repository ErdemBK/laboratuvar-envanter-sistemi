import sqlite3
import os
import shutil
from modeller import Malzeme

class DatabaseManager:
    def __init__(self, db_ismi="lab_envanter.db"):
        self.db_ismi = db_ismi
        self.baglan()
        self.tablolari_olustur()

    def baglan(self):
        self.baglanti = sqlite3.connect(self.db_ismi)
        self.baglanti.row_factory = sqlite3.Row
        self.imlec = self.baglanti.cursor()

    def kapat(self):
        if self.baglanti:
            self.baglanti.close()

    def tablolari_olustur(self):
        self.imlec.execute('''CREATE TABLE IF NOT EXISTS malzemeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            ambalaj_tipi TEXT,
            miktar REAL,
            birim TEXT,
            ikinci_miktar REAL,
            ikinci_birim TEXT,
            ucuncu_miktar REAL,
            ucuncu_birim TEXT,
            donusum_orani REAL,
            lokasyon TEXT,
            notlar TEXT
        )''')
        
        try:
            self.imlec.execute("ALTER TABLE malzemeler ADD COLUMN dorduncu_miktar REAL DEFAULT 0.0")
        except sqlite3.OperationalError: pass
        try:
            self.imlec.execute("ALTER TABLE malzemeler ADD COLUMN dorduncu_birim TEXT DEFAULT ''")
        except sqlite3.OperationalError: pass
        try:
            self.imlec.execute("ALTER TABLE malzemeler ADD COLUMN besinci_miktar REAL DEFAULT 0.0")
        except sqlite3.OperationalError: pass
        try:
            self.imlec.execute("ALTER TABLE malzemeler ADD COLUMN besinci_birim TEXT DEFAULT ''")
        except sqlite3.OperationalError: pass
        
        self.imlec.execute('''CREATE TABLE IF NOT EXISTS islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            malzeme_id INTEGER,
            malzeme_isim TEXT,
            islem_tipi TEXT,
            detay TEXT,
            kullanici TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        self.imlec.execute('''CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT UNIQUE NOT NULL
        )''')
        self.baglanti.commit()

    def malzeme_ekle(self, m: Malzeme):
        self.imlec.execute('''INSERT INTO malzemeler 
            (isim, ambalaj_tipi, miktar, birim, ikinci_miktar, ikinci_birim, ucuncu_miktar, ucuncu_birim, 
            dorduncu_miktar, dorduncu_birim, besinci_miktar, besinci_birim, donusum_orani, lokasyon, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (m.isim, m.ambalaj_tipi, m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, 
            m.ucuncu_miktar, m.ucuncu_birim, m.dorduncu_miktar, m.dorduncu_birim, 
            m.besinci_miktar, m.besinci_birim, m.donusum_orani, m.lokasyon, m.notlar))
        self.baglanti.commit()
        return self.imlec.lastrowid

    def malzemeleri_getir(self, arama=""):
        if arama:
            self.imlec.execute("SELECT * FROM malzemeler WHERE isim LIKE ? ORDER BY isim ASC", ('%'+arama+'%',))
        else:
            self.imlec.execute("SELECT * FROM malzemeler ORDER BY isim ASC")
        return [dict(row) for row in self.imlec.fetchall()]

    def malzeme_getir_id(self, m_id):
        self.imlec.execute("SELECT * FROM malzemeler WHERE id=?", (m_id,))
        row = self.imlec.fetchone()
        if row:
            r = dict(row) # HATA ÖNLEYİCİ: Veriyi SQLite Row objesinden Dict'e çeviriyoruz
            return Malzeme(
                id=r.get('id'), 
                isim=r.get('isim', ''), 
                ambalaj_tipi=r.get('ambalaj_tipi') or '',
                miktar=r.get('miktar') or 0.0, 
                birim=r.get('birim') or '',
                ikinci_miktar=r.get('ikinci_miktar') or 0.0, 
                ikinci_birim=r.get('ikinci_birim') or '',
                ucuncu_miktar=r.get('ucuncu_miktar') or 0.0, 
                ucuncu_birim=r.get('ucuncu_birim') or '',
                dorduncu_miktar=r.get('dorduncu_miktar') or 0.0, 
                dorduncu_birim=r.get('dorduncu_birim') or '',
                besinci_miktar=r.get('besinci_miktar') or 0.0, 
                besinci_birim=r.get('besinci_birim') or '',
                donusum_orani=r.get('donusum_orani') or 0.0, 
                lokasyon=r.get('lokasyon') or '', 
                notlar=r.get('notlar') or ''
            )
        return None

    def stok_guncelle(self, m: Malzeme):
        self.imlec.execute('''UPDATE malzemeler SET
            miktar=?, birim=?, ikinci_miktar=?, ikinci_birim=?, ucuncu_miktar=?, ucuncu_birim=?, 
            dorduncu_miktar=?, dorduncu_birim=?, besinci_miktar=?, besinci_birim=?, lokasyon=?, notlar=?
            WHERE id=?''', 
            (m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, 
            m.dorduncu_miktar, m.dorduncu_birim, m.besinci_miktar, m.besinci_birim, m.lokasyon, m.notlar, m.id))
        self.baglanti.commit()

    def malzeme_sil(self, m_id):
        self.imlec.execute("DELETE FROM malzemeler WHERE id=?", (m_id,))
        self.baglanti.commit()

    def malzeme_geri_yukle(self, m: Malzeme):
        self.imlec.execute('''INSERT INTO malzemeler 
            (id, isim, ambalaj_tipi, miktar, birim, ikinci_miktar, ikinci_birim, ucuncu_miktar, ucuncu_birim, 
            dorduncu_miktar, dorduncu_birim, besinci_miktar, besinci_birim, donusum_orani, lokasyon, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (m.id, m.isim, m.ambalaj_tipi, m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, 
            m.ucuncu_miktar, m.ucuncu_birim, m.dorduncu_miktar, m.dorduncu_birim, 
            m.besinci_miktar, m.besinci_birim, m.donusum_orani, m.lokasyon, m.notlar))
        self.baglanti.commit()

    def gecmis_ekle(self, malzeme_id, malzeme_isim, detay, kullanici):
        self.imlec.execute('''INSERT INTO islemler 
            (malzeme_id, malzeme_isim, islem_tipi, detay, kullanici) 
            VALUES (?, ?, ?, ?, ?)''', 
            (malzeme_id, malzeme_isim, "İşlem", detay, kullanici))
        self.baglanti.commit()
        return self.imlec.lastrowid

    def gecmis_sil(self, log_id):
        self.imlec.execute("DELETE FROM islemler WHERE id=?", (log_id,))
        self.baglanti.commit()

    def gecmisi_getir(self):
        self.imlec.execute("SELECT * FROM islemler ORDER BY id DESC")
        return [dict(r) for r in self.imlec.fetchall()]

    def kullanicilari_getir(self):
        self.imlec.execute("SELECT isim FROM kullanicilar ORDER BY isim ASC")
        return [row['isim'] for row in self.imlec.fetchall()]

    def kullanici_ekle(self, isim):
        try:
            self.imlec.execute("INSERT INTO kullanicilar (isim) VALUES (?)", (isim,))
            self.baglanti.commit()
        except sqlite3.IntegrityError: pass

    def kullanici_sil(self, isim):
        self.imlec.execute("DELETE FROM kullanicilar WHERE isim=?", (isim,))
        self.baglanti.commit()

    def yedek_al(self, hedef_yol):
        self.baglanti.commit()
        self.kapat()
        shutil.copy2(self.db_ismi, hedef_yol)
        self.baglan()

    def geri_yukle(self, kaynak_yol):
        self.kapat()
        shutil.copy2(kaynak_yol, self.db_ismi)
        self.baglan()
        self.tablolari_olustur()