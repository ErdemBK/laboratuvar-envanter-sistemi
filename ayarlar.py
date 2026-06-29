# ayarlar.py

TEMA_RENKLER = {
    "arkaplan": "#121212", "kart": "#1E1E1E", "vurgu_mavi": "#3B82F6",
    "basari_yesil": "#10B981", "uyari_sari": "#F59E0B", "tehlike_kirmizi": "#EF4444",
    "metin_ana": "#FFFFFF", "metin_ikincil": "#A1A1AA"
}

def aktif_tema_degistir(mod):
    if mod == "light":
        TEMA_RENKLER.update({"arkaplan": "#F3F4F6", "kart": "#FFFFFF", "metin_ana": "#111827", "metin_ikincil": "#6B7280"})
    else:
        TEMA_RENKLER.update({"arkaplan": "#121212", "kart": "#1E1E1E", "metin_ana": "#FFFFFF", "metin_ikincil": "#A1A1AA"})

DIL = "TR"

# DÜZELTME: Kelimelerin içindeki emojiler temizlendi. Çift ikon sorunu bitti!
LOCALIZED = {
    "TR": {
        "menu": "MENÜ", "envanter": "Envanter Listesi", "ekle": "Malzeme Ekle", "konumlar": "Konum Yönetimi",
        "gecmis": "İşlem Geçmişi", "yedekleme": "Yedekleme", "geri_al": "Geri Al", "ileri_al": "İleri Al",
        "kullanici_degis": "Kullanıcı Değiştir", "tema_degis": "Tema Değiştir", "baglanti_bilgi": "Bağlantı Bilgim",
        "baglanti_kes": "Bağlantıyı Kes", "arama_label": "🔍 Malzeme ve Konum Ara...", "uygulama_baslik": "Bulut Envanter Sistemi v2.0",
        "sonuc_yok": "Sonuç Bulunamadı", "excel_aktar": "⬇️ Excel'e Aktar", "temizle": "🧹 Temizle", "kaydet": "💾 Kaydet"
    },
    "EN": {
        "menu": "MENU", "envanter": "Inventory List", "ekle": "Add Material", "konumlar": "Location Mgmt",
        "gecmis": "Transaction Logs", "yedekleme": "Backup & Safety", "geri_al": "Undo", "ileri_al": "Redo",
        "kullanici_degis": "Change User", "tema_degis": "Toggle Theme", "baglanti_bilgi": "Connection Info",
        "baglanti_kes": "Disconnect", "arama_label": "🔍 Search Material or Location...", "uygulama_baslik": "Cloud Inventory System v2.0",
        "sonuc_yok": "No Results Found", "excel_aktar": "⬇️ Export to Excel", "temizle": "🧹 Clear Form", "kaydet": "💾 Save Data"
    }
}

def dil(tr_metin, en_metin):
    return tr_metin if DIL == "TR" else en_metin