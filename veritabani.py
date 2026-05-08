import sqlite3
import logging
import threading
from typing import List, Optional
from modeller import Malzeme

class DatabaseManager:
    def __init__(self, db_name: str = "lab_envanter.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False, timeout=15)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self.hazirla()

    def hazirla(self) -> None:
        with self.lock:
            try:
                self.conn.execute("PRAGMA journal_mode=WAL")
                self.conn.execute("PRAGMA foreign_keys=ON")
                self.conn.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT UNIQUE NOT NULL)")
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS malzemeler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT NOT NULL, ambalaj_tipi TEXT, miktar REAL NOT NULL, birim TEXT, 
                        ikinci_miktar REAL, ikinci_birim TEXT, ucuncu_miktar REAL, ucuncu_birim TEXT, donusum_orani REAL, lokasyon TEXT, notlar TEXT
                    )
                """)
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_malz_isim ON malzemeler(isim COLLATE NOCASE)")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_malz_lok ON malzemeler(lokasyon COLLATE NOCASE)")
                
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS stok_gecmisi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, malzeme_id INTEGER, malzeme_ismi TEXT, 
                        islem_tipi TEXT, degisim_miktari REAL, kullanici TEXT, islem_tarihi DATETIME DEFAULT (datetime('now', 'localtime'))
                    )
                """)
                sutunlar = [k[1] for k in self.conn.execute("PRAGMA table_info(stok_gecmisi)").fetchall()]
                if "malzeme_ismi" not in sutunlar: self.conn.execute("ALTER TABLE stok_gecmisi ADD COLUMN malzeme_ismi TEXT")
                self.conn.commit()
            except sqlite3.Error as e: logging.error(f"DB Hazırlama Hatası: {e}")

    def kapat(self):
        self.conn.close()

    def yedek_al(self, hedef_yol: str) -> None:
        with self.lock:
            with sqlite3.connect(hedef_yol) as dest: self.conn.backup(dest)

    def yedek_kurtar(self, kaynak_yol: str) -> None:
        with self.lock:
            with sqlite3.connect(kaynak_yol) as source: source.backup(self.conn)

    def kullanicilari_getir(self) -> List[str]:
        with self.lock: return [row['isim'] for row in self.conn.execute("SELECT isim FROM kullanicilar").fetchall()]

    def kullanici_ekle(self, isim: str) -> None:
        with self.lock:
            try:
                self.conn.execute("INSERT INTO kullanicilar (isim) VALUES (?)", (isim,))
                self.conn.commit()
            except sqlite3.IntegrityError: pass

    def kullanici_sil(self, isim: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM kullanicilar WHERE isim = ?", (isim,))
            self.conn.commit()

    def malzeme_ekle(self, m: Malzeme) -> int:
        with self.lock:
            imlec = self.conn.cursor()
            imlec.execute("""
                INSERT INTO malzemeler (isim, ambalaj_tipi, miktar, birim, ikinci_miktar, ikinci_birim, ucuncu_miktar, ucuncu_birim, donusum_orani, lokasyon, notlar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (m.isim, m.ambalaj_tipi, m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.donusum_orani, m.lokasyon, m.notlar))
            self.conn.commit()
            return imlec.lastrowid

    def malzeme_geri_yukle(self, m: Malzeme) -> None:
        with self.lock:
            # DÜZELTME: INSERT OR REPLACE kaldırıldı. Güvenli geri alma.
            self.conn.execute("""
                INSERT INTO malzemeler (id, isim, ambalaj_tipi, miktar, birim, ikinci_miktar, ikinci_birim, ucuncu_miktar, ucuncu_birim, donusum_orani, lokasyon, notlar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (m.id, m.isim, m.ambalaj_tipi, m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.donusum_orani, m.lokasyon, m.notlar))
            self.conn.commit()

    def malzemeleri_getir(self, arama: str = "") -> List[sqlite3.Row]:
        with self.lock:
            if arama:
                arama_str = f"%{arama}%"
                return self.conn.execute("SELECT * FROM malzemeler WHERE isim LIKE ? OR lokasyon LIKE ?", (arama_str, arama_str)).fetchall()
            return self.conn.execute("SELECT * FROM malzemeler").fetchall()

    def malzeme_getir_id(self, malzeme_id: int) -> Optional[Malzeme]:
        with self.lock: 
            row = self.conn.execute("SELECT * FROM malzemeler WHERE id = ?", (malzeme_id,)).fetchone()
            if row: return Malzeme(id=row['id'], isim=row['isim'], ambalaj_tipi=row['ambalaj_tipi'], miktar=row['miktar'], birim=row['birim'], ikinci_miktar=row['ikinci_miktar'], ikinci_birim=row['ikinci_birim'], ucuncu_miktar=row['ucuncu_miktar'], ucuncu_birim=row['ucuncu_birim'], donusum_orani=row['donusum_orani'], lokasyon=row['lokasyon'], notlar=row['notlar'])
            return None

    def stok_guncelle(self, m: Malzeme) -> None:
        with self.lock:
            self.conn.execute("""
                UPDATE malzemeler SET miktar=?, birim=?, ikinci_miktar=?, ikinci_birim=?, ucuncu_miktar=?, ucuncu_birim=?, lokasyon=?, notlar=? WHERE id=?
            """, (m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.lokasyon, m.notlar, m.id))
            self.conn.commit()

    def malzeme_sil(self, malzeme_id: int) -> None:
        with self.lock: 
            self.conn.execute("DELETE FROM malzemeler WHERE id = ?", (malzeme_id,))
            self.conn.commit()

    def csv_ile_veri_aktar(self, csv_verileri: List[Malzeme]) -> None:
        with self.lock:
            try:
                self.conn.execute("BEGIN TRANSACTION")
                self.conn.execute("DELETE FROM malzemeler")
                try: self.conn.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'malzemeler'")
                except: pass
                
                imlec = self.conn.cursor()
                for m in csv_verileri:
                    imlec.execute("""
                        INSERT INTO malzemeler (isim, ambalaj_tipi, miktar, birim, ikinci_miktar, ikinci_birim, ucuncu_miktar, ucuncu_birim, donusum_orani, lokasyon, notlar)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (m.isim, m.ambalaj_tipi, m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.donusum_orani, m.lokasyon, m.notlar))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback() 
                raise e

    def gecmis_ekle(self, malzeme_id: int, malzeme_ismi: str, islem_tipi: str, kullanici: str) -> int:
        with self.lock:
            imlec = self.conn.cursor()
            imlec.execute("INSERT INTO stok_gecmisi (malzeme_id, malzeme_ismi, islem_tipi, degisim_miktari, kullanici) VALUES (?, ?, ?, 0.0, ?)", 
                          (malzeme_id, malzeme_ismi, islem_tipi, kullanici))
            self.conn.commit()
            return imlec.lastrowid

    def gecmis_sil(self, log_id: int) -> None:
        with self.lock: 
            self.conn.execute("DELETE FROM stok_gecmisi WHERE id = ?", (log_id,))
            self.conn.commit()

    def gecmis_getir(self) -> List[sqlite3.Row]:
        with self.lock: return self.conn.execute("SELECT id, malzeme_ismi, islem_tipi, kullanici, islem_tarihi FROM stok_gecmisi ORDER BY islem_tarihi DESC").fetchall()