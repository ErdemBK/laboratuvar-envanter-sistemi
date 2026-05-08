from dataclasses import dataclass
from typing import Optional
from enum import Enum

class IslemTipi(Enum):
    EKLEME = "Ekleme"
    SILME = "Silme"
    GUNCELLEME = "Güncelleme"

@dataclass
class Malzeme:
    id: Optional[int] = None
    isim: str = ""
    ambalaj_tipi: str = ""
    miktar: float = 0.0
    birim: str = ""
    ikinci_miktar: float = 0.0
    ikinci_birim: str = ""
    ucuncu_miktar: float = 0.0
    ucuncu_birim: str = ""
    donusum_orani: float = 0.0
    lokasyon: str = ""
    notlar: str = ""

@dataclass
class UndoIslemi:
    tip: str 
    malzeme_id: int
    malzeme_isim: str
    log_id: int
    eski_malzeme: Optional[Malzeme] = None
    yeni_malzeme: Optional[Malzeme] = None

def miktar_dogrula(deger):
    try:
        return float(deger) if deger and str(deger).strip() else 0.0
    except ValueError:
        return 0.0

# DİL DESTEKLİ STOK METNİ
def stok_metni_olustur(m1, b1, m2, b2, m3, b3, aktif_dil="TR"):
    # Birim sözlüğü
    birim_map = {
        "TR": ["Koli", "Paket", "Kutu", "Şişe", "Adet"],
        "EN": ["Case", "Package", "Box", "Bottle", "Piece"]
    }
    
    # Eğer dil EN ise ve gelen birim TR listesindeyse çevir
    def cevir(birim):
        if aktif_dil == "EN":
            for i, tr_b in enumerate(birim_map["TR"]):
                if birim == tr_b: return birim_map["EN"][i]
        return birim

    parcalar = []
    if m1 > 0: parcalar.append(f"{m1} {cevir(b1)}")
    if m2 > 0: parcalar.append(f"{m2} {cevir(b2)}")
    if m3 > 0: parcalar.append(f"{m3} {cevir(b3)}")
    return " + ".join(parcalar) if parcalar else "0"