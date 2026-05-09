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
    dorduncu_miktar: float = 0.0
    dorduncu_birim: str = ""
    besinci_miktar: float = 0.0
    besinci_birim: str = ""
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
        if deger and str(deger).strip():
            return float(deger)
        return 0.0
    except ValueError:
        return 0.0

def stok_metni_olustur(m1, b1, m2, b2, m3, b3, m4, b4, m5, b5, aktif_dil="TR"):
    m1 = m1 or 0.0
    m2 = m2 or 0.0
    m3 = m3 or 0.0
    m4 = m4 or 0.0
    m5 = m5 or 0.0
    b1 = b1 or ""
    b2 = b2 or ""
    b3 = b3 or ""
    b4 = b4 or ""
    b5 = b5 or ""

    birim_map = {
        "TR": ["Koli", "Paket", "Kutu", "Şişe", "Adet"],
        "EN": ["Case", "Package", "Box", "Bottle", "Piece"]
    }
    
    def cevir(birim):
        if aktif_dil == "EN":
            for i, tr_b in enumerate(birim_map["TR"]):
                if birim == tr_b: 
                    return birim_map["EN"][i]
        return birim

    # .0 uzantılarını temizleyen akıllı fonksiyon (Örn: 12.0 -> 12)
    def fmt(val):
        try:
            v = float(val)
            return f"{int(v)}" if v.is_integer() else f"{v}"
        except:
            return str(val)

    parcalar = []
    
    if m1 > 0: parcalar.append(f"{fmt(m1)} {cevir(b1)}")
    if m2 > 0: parcalar.append(f"{fmt(m2)} {cevir(b2)}")
    if m3 > 0: parcalar.append(f"{fmt(m3)} {cevir(b3)}")
    if m4 > 0: parcalar.append(f"{fmt(m4)} {cevir(b4)}")
    if m5 > 0: parcalar.append(f"{fmt(m5)} {cevir(b5)}")
        
    if not parcalar:
        return "0"
        
    return "  •  ".join(parcalar)