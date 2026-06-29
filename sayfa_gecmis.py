# sayfa_gecmis.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri
import datetime
import os

def gecmis_gorunumu(page: ft.Page):
    d = ayarlar.dil
    def islem_etiketi(islem_tipi):
        renk = ayarlar.TEMA_RENKLER["basari_yesil"] if islem_tipi == "Eklendi" or islem_tipi == "Added" else (ayarlar.TEMA_RENKLER["tehlike_kirmizi"] if islem_tipi == "Silindi" or islem_tipi == "Deleted" else ayarlar.TEMA_RENKLER["vurgu_mavi"])
        return ft.Container(bgcolor=renk, padding=6, border_radius=5, content=ft.Text(islem_tipi, color="#FFFFFF", size=11, weight="bold"))

    def gecmisi_indir(e):
        bugun = datetime.datetime.now().strftime("%Y_%m_%d")
        yol = ui_bilesenleri.dosya_kaydet_dialog(d("Geçmişi Kaydet", "Save Log"), f"lab_gecmis_{bugun}.csv", ".csv")
        if yol:
            with open(yol, "w", encoding="utf-8-sig") as f:
                f.write("Islem;Tarih;Kullanici;Detay\n")
                for log in veri.GECMIS: f.write(f"{log['islem']};{log['tarih']};{log['kullanici']};{log['detay']}\n")
            ui_bilesenleri.goster_toast(page, d("Kaydedildi!", "Saved!"), True)

    def gecmisi_temizle(e):
        def onayla(e2):
            veri.anim_kaydet(); veri.GECMIS.clear(); veri.verileri_kaydet()
            ui_bilesenleri.dialog_kapat(page, dlg); listeyi_yenile(); ui_bilesenleri.goster_toast(page, d("Temizlendi!", "Cleared!"), True)

        dlg = ft.AlertDialog(title=ft.Text(d("Emin Misiniz?", "Are you sure?"), color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"]), content=ft.Text(d("Geçmiş silinecektir.", "Logs will be deleted.")), bgcolor=ayarlar.TEMA_RENKLER["kart"],
            actions=[ft.TextButton(d("İptal", "Cancel"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton(d("Sil", "Delete"), icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=onayla)])
        ui_bilesenleri.dialog_ac(page, dlg)

    uyari_kutusu = ft.Container(bgcolor=ayarlar.TEMA_RENKLER["uyari_sari"] + "20", padding=15, border_radius=10, content=ft.Row([
        ft.Text("⚠️", size=24), 
        # TR ve EN metinleri bulut veritabanı boşaltma durumuna uyarlandı
        ft.Text(d("Bulut veritabanında yer açmak ve performansı artırmak için geçmişinizi ayda 1 kez indirip temizleyin.", "To free up space in the cloud database and improve performance, download and clear logs monthly."), expand=True),
        ft.ElevatedButton(d("⬇️ İndir", "⬇️ Download"), bgcolor=ayarlar.TEMA_RENKLER["vurgu_mavi"], color="#FFFFFF", on_click=gecmisi_indir),
        ft.ElevatedButton(d("🗑️ Temizle", "🗑️ Clear"), bgcolor=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], color="#FFFFFF", on_click=gecmisi_temizle)
    ]))
    liste_alani = ft.ListView(expand=True, spacing=10, padding=10)
    
    def listeyi_yenile():
        liste_alani.controls.clear()
        for log in veri.GECMIS:
            liste_alani.controls.append(ft.Container(bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=10, border_radius=8, content=ft.Row([
                islem_etiketi(log["islem"]), ft.Text(log["tarih"], color=ayarlar.TEMA_RENKLER["metin_ikincil"], size=12),
                ft.Text(log["kullanici"], color=ayarlar.TEMA_RENKLER["vurgu_mavi"], size=14, weight="bold"),
                ft.Text(log["detay"], color=ayarlar.TEMA_RENKLER["metin_ana"], size=14, expand=True, no_wrap=True, overflow="ellipsis")
            ])))
        page.update()

    listeyi_yenile()
    return ft.Column([ft.Text(d("🕒 İşlem Geçmişi", "🕒 Transaction Logs"), size=30, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=10), uyari_kutusu, ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=10), liste_alani], expand=True)