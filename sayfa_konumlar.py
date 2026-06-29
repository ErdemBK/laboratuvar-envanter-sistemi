# sayfa_konumlar.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri

def konumlar_gorunumu(page: ft.Page):
    d = ayarlar.dil
    isim_input = ft.TextField(label=d("Yeni Konum Adı", "New Location Name"), border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], expand=True)
    liste_alani = ft.ListView(expand=True, spacing=10, padding=10)

    def listeyi_yenile():
        liste_alani.controls.clear()
        for k in veri.KONUMLAR:
            
            def duzenle(e):
                eski_ad = e.control.data
                yeni_ad_input = ft.TextField(value=eski_ad, border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"])
                def onayla(_):
                    if yeni_ad_input.value and yeni_ad_input.value != eski_ad:
                        veri.anim_kaydet()
                        veri.KONUMLAR[veri.KONUMLAR.index(eski_ad)] = yeni_ad_input.value
                        for m in veri.MALZEMELER:
                            if m["konum"] == eski_ad: m["konum"] = yeni_ad_input.value
                        veri.verileri_kaydet()
                        listeyi_yenile(); ui_bilesenleri.dialog_kapat(page, dlg)
                        ui_bilesenleri.goster_toast(page, d("Konum ve içerikler güncellendi!", "Location & contents updated!"), True)
                
                dlg = ft.AlertDialog(title=ft.Text(d("Konumu Düzenle", "Edit Location")), content=yeni_ad_input, bgcolor=ayarlar.TEMA_RENKLER["kart"],
                    actions=[ft.TextButton(d("İptal", "Cancel"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton(d("Kaydet", "Save"), on_click=onayla)])
                ui_bilesenleri.dialog_ac(page, dlg)

            def sil(e):
                konum_adi = e.control.data
                def onayla(e2):
                    veri.anim_kaydet()
                    veri.KONUMLAR.remove(konum_adi)
                    for m in veri.MALZEMELER:
                        if m["konum"] == konum_adi: m["konum"] = "Yer Belirtilmiyor"
                    veri.verileri_kaydet(); ui_bilesenleri.dialog_kapat(page, dlg); listeyi_yenile()
                    ui_bilesenleri.goster_toast(page, d("Konum silindi!", "Location deleted!"), False)
                
                # DÜZELTME: Konum ismini belirten daha açık ve net uyarı mesajı
                dlg = ft.AlertDialog(title=ft.Text(d("Kritik Uyarı!", "Critical Warning!"), color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"]),
                    content=ft.Text(d(f"'{konum_adi}' konumuna ait tüm malzemeler 'Yer Belirtilmiyor' olarak güncellenecektir.\n\nOnaylıyor musunuz?", f"All materials in '{konum_adi}' will be updated to 'Not Specified'.\n\nConfirm?")), bgcolor=ayarlar.TEMA_RENKLER["kart"],
                    actions=[ft.TextButton(d("İptal", "Cancel"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton(d("Evet, Sil", "Yes, Delete"), icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=onayla)])
                ui_bilesenleri.dialog_ac(page, dlg)

            liste_alani.controls.append(ft.Container(bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=15, border_radius=10, content=ft.Row([
                ft.Text(k, color=ayarlar.TEMA_RENKLER["metin_ana"], size=16, weight="bold", expand=True), 
                ft.TextButton("✏️", data=k, on_click=duzenle), ft.TextButton("🗑️", data=k, on_click=sil)
            ])))
        page.update()

    def konum_ekle(e):
        if not isim_input.value: return
        veri.anim_kaydet(); veri.KONUMLAR.append(isim_input.value); veri.verileri_kaydet()
        ui_bilesenleri.goster_toast(page, d("Eklendi!", "Added!"), True); isim_input.value = ""; listeyi_yenile()

    listeyi_yenile()
    return ft.Column([ft.Text(d("📍 Konum Yönetimi", "📍 Location Mgmt"), size=30, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=30), ft.Row([isim_input, ft.ElevatedButton(d("➕ Ekle", "➕ Add"), bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], color="#FFFFFF", height=50, on_click=konum_ekle)]), ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=20), liste_alani], expand=True)