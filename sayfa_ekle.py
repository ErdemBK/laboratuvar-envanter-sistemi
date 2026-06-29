# sayfa_ekle.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri
import datetime

def ekle_gorunumu(page: ft.Page):
    d = ayarlar.dil
    
    isim_input = ft.TextField(label=d("Malzeme Adı", "Material Name"), border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], border_radius=15, filled=True, expand=True)
    konum_dropdown = ft.Dropdown(label=d("Lokasyon (İsteğe Bağlı)", "Location (Optional)"), border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], border_radius=15, filled=True, options=[ft.dropdown.Option(k) for k in veri.KONUMLAR], expand=True)
    notlar_input = ft.TextField(label=d("📝 Notlar (İsteğe Bağlı)", "📝 Notes (Optional)"), border_color=ayarlar.TEMA_RENKLER["uyari_sari"], border_radius=15, filled=True, multiline=True, min_lines=3, max_lines=5)

    dinamik_satirlar = ft.Column(spacing=10)
    BIRIMLER = ["Adet", "Litre", "ml", "Kg", "Gram", "mg", "Kutu", "Koli", "Paket", "Rulo", "Şişe"]

    def satiri_sil(e, satir):
        dinamik_satirlar.controls.remove(satir); page.update()

    def satir_olustur(ilk_satir=False):
        satir = ft.Row([
            ft.TextField(label=d("Miktar", "Qty"), border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], border_radius=15, filled=True, expand=True),
            ft.Dropdown(label=d("Birim", "Unit"), border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], border_radius=15, filled=True, options=[ft.dropdown.Option(b) for b in BIRIMLER], expand=True)
        ])
        if not ilk_satir: satir.controls.append(ft.TextButton("❌", tooltip=d("Satırı Sil", "Delete Row"), on_click=lambda e: satiri_sil(e, satir)))
        return satir

    dinamik_satirlar.controls.append(satir_olustur(ilk_satir=True))

    def arti_tiklandi(e):
        if len(dinamik_satirlar.controls) < 5: dinamik_satirlar.controls.append(satir_olustur(ilk_satir=False)); page.update()
        else: ui_bilesenleri.goster_toast(page, d("Maksimum 5 birim ekleyebilirsiniz!", "Max 5 units allowed!"), basari=False)

    def formu_temizle(e=None):
        isim_input.value = ""; notlar_input.value = ""; konum_dropdown.value = None
        dinamik_satirlar.controls.clear(); dinamik_satirlar.controls.append(satir_olustur(ilk_satir=True))
        if e: ui_bilesenleri.goster_toast(page, d("Form temizlendi.", "Form cleared."), basari=True)
        page.update()

    def kaydet_tiklandi(e):
        if not isim_input.value: ui_bilesenleri.goster_toast(page, d("Lütfen malzeme adı giriniz!", "Please enter material name!"), False); return

        yeni_miktarlar = []; miktar_ozetleri = []
        for satir in dinamik_satirlar.controls:
            m_val = satir.controls[0].value; b_val = satir.controls[1].value
            if m_val and b_val: yeni_miktarlar.append({"deger": m_val, "birim": b_val}); miktar_ozetleri.append(f"{m_val} {b_val}")
        
        if not yeni_miktarlar: ui_bilesenleri.goster_toast(page, d("Lütfen en az 1 miktar giriniz!", "Enter at least 1 qty!"), False); return

        secilen_konum = konum_dropdown.value if konum_dropdown.value else "Yer Belirtilmiyor"
        
        # ID ÜRETİCİSİ: Mevcut ID'leri tarar, en yükseğinin 1 fazlasını atar. İlk malzemeyse 1 yapar.
        mevcut_idler = [m.get("id", 0) for m in veri.MALZEMELER if isinstance(m.get("id"), int)]
        yeni_id = max(mevcut_idler) + 1 if mevcut_idler else 1

        yeni_malzeme = {"id": yeni_id, "isim": isim_input.value, "konum": secilen_konum, "miktarlar": yeni_miktarlar, "notlar": notlar_input.value}
        
        veri.anim_kaydet()
        veri.MALZEMELER.insert(0, yeni_malzeme)
        zaman = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
        ozet_metni = ", ".join(miktar_ozetleri)
        veri.GECMIS.insert(0, {"islem": "Eklendi" if ayarlar.DIL == "TR" else "Added", "tarih": zaman, "kullanici": veri.aktif_kullanici, "detay": f"'{yeni_malzeme['isim']}' ({ozet_metni})"})
        
        veri.verileri_kaydet() 
        ui_bilesenleri.goster_toast(page, d(f"'{isim_input.value}' eklendi!", f"'{isim_input.value}' added!"), True)
        formu_temizle()

    form_karti = ft.Container(
        bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=40, border_radius=20, 
        content=ft.Column([
            ft.Row([isim_input, konum_dropdown], spacing=20), ft.Container(height=10),
            ft.Row([ft.Text(d("Miktar ve Birimler", "Quantities & Units"), color=ayarlar.TEMA_RENKLER["metin_ikincil"], expand=True, size=16), ft.TextButton(d("➕ Miktar Ekle", "➕ Add Qty"), on_click=arti_tiklandi)]),
            ft.Divider(color=ayarlar.TEMA_RENKLER["arkaplan"]), dinamik_satirlar, ft.Container(height=10), notlar_input, ft.Container(height=20),
            ft.Row([ft.TextButton(d("🧹 Temizle", "🧹 Clear"), on_click=formu_temizle), ft.Container(expand=True), ft.ElevatedButton(d("💾 Buluta Kaydet", "💾 Save to Cloud"), on_click=kaydet_tiklandi, bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], color="#FFFFFF", height=55, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)))])
        ])
    )
    return ft.Column([ft.Text(d("➕ Yeni Malzeme Ekle", "➕ Add New Material"), size=30, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=30), form_karti], expand=True, scroll="auto")