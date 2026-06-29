# sayfa_kullanici.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri

def kullanici_gorunumu(page: ft.Page):
    L = ayarlar.LOCALIZED[ayarlar.DIL]
    yeni_isim_input = ft.TextField(label=L["kaydet"], border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], width=280)
    liste_alani = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

    def listeyi_yenile():
        liste_alani.controls.clear()
        for kullanici in veri.KULLANICILAR:
            def giris_yap(e):
                veri.aktif_kullanici = e.control.data
                ui_bilesenleri.goster_toast(page, f"Hoş geldin, {veri.aktif_kullanici}!" if ayarlar.DIL == "TR" else f"Welcome, {veri.aktif_kullanici}!", basari=True)
                page.sayfa_degistir("envanter")

            def sil(e):
                sil_kisi = e.control.data
                def onayla(e2):
                    veri.KULLANICILAR.remove(sil_kisi); veri.verileri_kaydet()
                    ui_bilesenleri.dialog_kapat(page, dlg); listeyi_yenile()
                    ui_bilesenleri.goster_toast(page, "Silindi!" if ayarlar.DIL == "TR" else "Deleted!", False)
                
                dlg = ft.AlertDialog(title=ft.Text("Emin Misiniz?" if ayarlar.DIL == "TR" else "Are you sure?"), content=ft.Text(f"'{sil_kisi}' silinecek."), bgcolor=ayarlar.TEMA_RENKLER["kart"],
                    actions=[ft.TextButton("İptal" if ayarlar.DIL == "TR" else "Cancel", on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton("Evet, Sil" if ayarlar.DIL == "TR" else "Yes, Delete", icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=onayla)])
                ui_bilesenleri.dialog_ac(page, dlg)

            liste_alani.controls.append(ft.Row([
                ft.ElevatedButton(content=ft.Text(f"👤 {kullanici}", color="#FFFFFF", size=16, weight="bold"), bgcolor=ayarlar.TEMA_RENKLER["vurgu_mavi"], height=50, width=230, data=kullanici, on_click=giris_yap),
                ft.TextButton("🗑️", data=kullanici, on_click=sil)
            ], alignment=ft.MainAxisAlignment.CENTER))
        page.update()

    def kullanici_ekle(e):
        if not yeni_isim_input.value: return
        veri.KULLANICILAR.append(yeni_isim_input.value); veri.verileri_kaydet()
        ui_bilesenleri.goster_toast(page, "Eklendi!" if ayarlar.DIL == "TR" else "Added!", True); yeni_isim_input.value = ""; listeyi_yenile()
        
    def baglantiyi_kes_uyari(e):
        def onayla(e2):
            ui_bilesenleri.dialog_kapat(page, dlg); veri.baglantiyi_kes(); page.sayfa_degistir("baglanti")
            ui_bilesenleri.goster_toast(page, "Bulut bağlantısı kesildi." if ayarlar.DIL == "TR" else "Cloud connection disconnected.", False)

        # DİKKAT: "Laboratuvar" kelimesi tamamen silindi, yerine Bulut ve Link uyarıları eklendi
        dlg = ft.AlertDialog(
            title=ft.Text("Bulut Bağlantısını Kes" if ayarlar.DIL == "TR" else "Disconnect Cloud", color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"]), 
            content=ft.Text("Bulut sisteminden çıkış yapmak üzeresiniz.\n\n⚠️ LÜTFEN DİKKAT: Linkinizi kaybetmeniz durumunda verilerinize tekrar ulaşamazsınız. Çıkış yapmadan önce linkinizi güvenli bir yere kopyaladığınızdan emin olun!\n\nOnaylıyor musunuz?" if ayarlar.DIL == "TR" else "You are about to disconnect from the cloud system.\n\n⚠️ WARNING: If you lose your link, you cannot access your data again. Make sure you copy your link to a safe place before logging out!"), 
            bgcolor=ayarlar.TEMA_RENKLER["kart"],
            actions=[
                ft.TextButton("İptal" if ayarlar.DIL == "TR" else "Cancel", on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), 
                ft.TextButton("Evet, Çıkış Yap" if ayarlar.DIL == "TR" else "Yes, Logout", icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=onayla)
            ]
        )
        ui_bilesenleri.dialog_ac(page, dlg)

    listeyi_yenile()
    return ft.Container(
        bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=40, border_radius=15, width=450,
        content=ft.Column([
            ft.Row([ft.Container(expand=True), ft.TextButton("🌐 TR/EN", on_click=lambda _: setattr(ayarlar, 'DIL', "EN" if ayarlar.DIL == "TR" else "TR") or page.sayfa_degistir("kullanici"))]),
            ft.Text("Kim Giriş Yapıyor?" if ayarlar.DIL == "TR" else "Who is Logging In?", size=25, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Container(height=10),
            ft.Row([yeni_isim_input, ft.ElevatedButton(content=ft.Text("➕ Ekle" if ayarlar.DIL == "TR" else "➕ Add", color="#FFFFFF"), bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], height=50, on_click=kullanici_ekle)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=ayarlar.TEMA_RENKLER["arkaplan"], height=30), ft.Container(content=liste_alani, height=250), ft.Divider(color=ayarlar.TEMA_RENKLER["arkaplan"], height=10),
            ft.TextButton(content=ft.Row([ft.Text("🔌", size=18), ft.Text("Bulut Bağlantısını Kes" if ayarlar.DIL == "TR" else "Disconnect Cloud", size=15, color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"])]), on_click=baglantiyi_kes_uyari)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )