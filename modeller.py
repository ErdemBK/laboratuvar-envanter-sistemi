from dataclasses import dataclass
from typing import Optional
from enum import Enum

class IslemTipi(Enum):
    EKLEME = "Sisteme Eklendi"
    SILME = "Kalıcı Olarak Silindi"
    GUNCELLEME = "Stok Düzenlendi"

@dataclass
class Malzeme:
    isim: str
    ambalaj_tipi: str
    miktar: float
    birim: str
    ikinci_miktar: float = 0.0
    ikinci_birim: str = ""
    ucuncu_miktar: float = 0.0
    ucuncu_birim: str = ""
    donusum_orani: float = 0.0
    lokasyon: str = ""
    notlar: str = ""
    id: Optional[int] = None

# YENİ EKLENEN PROFESYONEL UNDO SINIFI
@dataclass
class UndoIslemi:
    tip: str  # "ekleme", "silme", "guncelleme"
    malzeme_id: int
    malzeme_isim: str
    log_id: int
    eski_malzeme: Optional[Malzeme] = None
    yeni_malzeme: Optional[Malzeme] = None

def stok_metni_olustur(m1: float, b1: str, m2: float = 0.0, b2: str = "", m3: float = 0.0, b3: str = "") -> str:
    m1, m2, m3 = m1 or 0.0, m2 or 0.0, m3 or 0.0
    m1_str = str(int(m1)) if m1 % 1 == 0 else str(m1)
    m2_str = str(int(m2)) if m2 % 1 == 0 else str(m2)
    m3_str = str(int(m3)) if m3 % 1 == 0 else str(m3)
    metin = f"{m1_str} {b1}"
    if m2 > 0: metin += f" + {m2_str} {b2}"
    if m3 > 0: metin += f" + {m3_str} {b3}"
    return metin

def miktar_dogrula(deger: str) -> float:
    if not deger: return 0.0
    try:
        val = float(deger)
        if val < 0: raise ValueError("Miktar eksi bir değer olamaz.")
        return val
    except ValueError:
        raise ValueError("Miktar alanına geçerli bir sayı girmelisiniz.")