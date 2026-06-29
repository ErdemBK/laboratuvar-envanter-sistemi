# main.py
import flet as ft
import ayarlar
import sayfa_baglanti
import sayfa_envanter
import sayfa_ekle
import sayfa_konumlar
import sayfa_gecmis
import sayfa_yedekleme
import sayfa_kullanici
import ui_bilesenleri
import veri

def main(page: ft.Page):
    d = ayarlar.dil
    page.title = d("Bulut Envanter Sistemi v2.0", "Cloud Inventory System v2.0")
    page.theme_mode = "dark"; page.bgcolor = ayarlar.TEMA_RENKLER["arkaplan"]; page.padding = 0
    page.window.width = 1400; page.window.height = 900; page.window.min_width = 1000; page.window.min_height = 700

    ana_govde = ft.Container(expand=True)
    page.add(ana_govde)

    def sayfa_degistir(hedef):
        page.aktif_sekme = hedef; page.title = d("Bulut Envanter Sistemi v2.0", "Cloud Inventory System v2.0")
        if hedef in ["baglanti", "kullanici"]:
            icerik = sayfa_baglanti.baglanti_gorunumu(page) if hedef == "baglanti" else sayfa_kullanici.kullanici_gorunumu(page)
            ana_govde.content = ft.Row([ft.Column([icerik], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        else:
            sayfa_icerigi = ft.Container(expand=True, padding=30)
            if hedef == "envanter": sayfa_icerigi.content = sayfa_envanter.envanter_gorunumu(page)
            elif hedef == "ekle": sayfa_icerigi.content = sayfa_ekle.ekle_gorunumu(page)
            elif hedef == "konumlar": sayfa_icerigi.content = sayfa_konumlar.konumlar_gorunumu(page)
            elif hedef == "gecmis": sayfa_icerigi.content = sayfa_gecmis.gecmis_gorunumu(page)
            elif hedef == "yedekleme": sayfa_icerigi.content = sayfa_yedekleme.yedekleme_gorunumu(page)
            ana_govde.content = ft.Row([menu_olustur(), ft.VerticalDivider(width=1, color=ayarlar.TEMA_RENKLER["kart"]), sayfa_icerigi], expand=True, spacing=0)
        page.update()

    page.sayfa_degistir = sayfa_degistir

    def tetik_geri_al(e):
        if veri.geri_al_motoru(): ui_bilesenleri.goster_toast(page, d("İşlem geri alındı", "Undone"), True); sayfa_degistir(page.aktif_sekme)
        else: ui_bilesenleri.goster_toast(page, d("Geri alınacak işlem yok", "Nothing to undo"), False)

    def tetik_ileri_al(e):
        if veri.ileri_al_motoru(): ui_bilesenleri.goster_toast(page, d("İşlem ileri alındı", "Redone"), True); sayfa_degistir(page.aktif_sekme)
        else: ui_bilesenleri.goster_toast(page, d("İleri alınacak işlem yok", "Nothing to redo"), False)

    def menu_olustur():
        L = ayarlar.LOCALIZED[ayarlar.DIL]
        
        def baglanti_bilgim_ac(e):
            def kopyala_aksiyon(e2):
                if ui_bilesenleri.panoya_kopyala(veri.aktif_link): ui_bilesenleri.goster_toast(page, d("Link kopyalandı!", "Link copied!"), True)

            mb_kullanim = veri.bulut_boyutunu_getir()
            yuzde = (mb_kullanim / 500.0)
            yuzde_gorsel = yuzde if yuzde > 0.01 else 0.01

            dlg = ft.AlertDialog(title=ft.Text(d("☁️ Bağlantı Bilgilerim", "☁️ Connection Info")), content=ft.Column([
                ft.Text(d("Mevcut Linkiniz:", "Current Link:")), ft.TextField(value=veri.aktif_link, read_only=True, border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"]),
                ft.TextButton(d("📋 Kopyala", "📋 Copy"), on_click=kopyala_aksiyon), ft.Divider(), 
                ft.Text(d("💾 Depolama Alanı (Neon Free Tier)", "💾 Storage (Neon Free Tier)"), weight="bold"),
                ft.ProgressBar(value=yuzde_gorsel, color=ayarlar.TEMA_RENKLER["basari_yesil"]),
                ft.Text(d(f"Kullanılan: {mb_kullanim} MB / 500 MB (%{yuzde*100:.2f})", f"Used: {mb_kullanim} MB / 500 MB ({yuzde*100:.2f}%)"), size=13, color=ayarlar.TEMA_RENKLER["metin_ikincil"]),
                ft.Divider(),
                ft.Row([
                    ft.Text("💡", size=16),
                    ft.Text(d("Depolama Hakkında Bilgi:", "Storage Info:"), weight="bold", size=13, color=ayarlar.TEMA_RENKLER["metin_ana"])
                ], spacing=5),
                ft.Text(
                    d("PostgreSQL sistem dosyaları nedeniyle veritabanı standart olarak ~7.5 MB yer kaplar. Eklediğiniz malzemeler ise sadece birkaç bayttır; binlerce ürün ekleseniz dahi bu kota dolmayacaktır.",
                      "PostgreSQL occupies ~7.5 MB by default for system files. Your materials take only a few bytes; this quota will not fill up even with thousands of items."),
                    size=11, color=ayarlar.TEMA_RENKLER["metin_ikincil"]
                )
            ], tight=True), bgcolor=ayarlar.TEMA_RENKLER["kart"], actions=[ft.TextButton(d("Kapat", "Close"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg))])
            ui_bilesenleri.dialog_ac(page, dlg)

        def baglanti_kes_uyari(e):
            dlg = ft.AlertDialog(title=ft.Text(L["baglanti_kes"], color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"]),
                content=ft.Text(d("Bulut bağlantısını kesmek üzeresiniz.\nLinkinizi kopyalayıp güvenli bir yere kaydettiğinizden emin olun!", "About to disconnect from cloud.\nEnsure you saved your link!")), bgcolor=ayarlar.TEMA_RENKLER["kart"],
                actions=[ft.TextButton(d("İptal", "Cancel"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton(d("Evet, Kes", "Yes, Disconnect"), icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg) or veri.baglantiyi_kes() or sayfa_degistir("baglanti"))])
            ui_bilesenleri.dialog_ac(page, dlg)

        def tema_degistir(e):
            yeni_mod = "light" if page.theme_mode == "dark" else "dark"
            page.theme_mode = yeni_mod; ayarlar.aktif_tema_degistir(yeni_mod); page.bgcolor = ayarlar.TEMA_RENKLER["arkaplan"]
            sayfa_degistir(page.aktif_sekme)

        ust_menu = ft.Column(spacing=25, controls=[
            ft.Text(L["menu"], size=26, weight="bold", color=ayarlar.TEMA_RENKLER["vurgu_mavi"]), ft.Divider(color=ayarlar.TEMA_RENKLER["metin_ikincil"]),
            ft.TextButton(content=ft.Row([ft.Text("📦", size=22), ft.Text(L["envanter"], size=18, color=ayarlar.TEMA_RENKLER["metin_ana"])]), on_click=lambda e: sayfa_degistir("envanter")),
            ft.TextButton(content=ft.Row([ft.Text("➕", size=22), ft.Text(L["ekle"], size=18, color=ayarlar.TEMA_RENKLER["metin_ana"])]), on_click=lambda e: sayfa_degistir("ekle")),
            ft.TextButton(content=ft.Row([ft.Text("📍", size=22), ft.Text(L["konumlar"], size=18, color=ayarlar.TEMA_RENKLER["metin_ana"])]), on_click=lambda e: sayfa_degistir("konumlar")),
            ft.TextButton(content=ft.Row([ft.Text("🕒", size=22), ft.Text(L["gecmis"], size=18, color=ayarlar.TEMA_RENKLER["metin_ana"])]), on_click=lambda e: sayfa_degistir("gecmis")),
            ft.TextButton(content=ft.Row([ft.Text("💾", size=22), ft.Text(L["yedekleme"], size=18, color=ayarlar.TEMA_RENKLER["metin_ana"])]), on_click=lambda e: sayfa_degistir("yedekleme"))
        ])

        orta_butonlar = ft.Row([
            ft.TextButton(content=ft.Row([ft.Text("⟲", size=20), ft.Text(L['geri_al'], size=16, color=ayarlar.TEMA_RENKLER["vurgu_mavi"])]), on_click=tetik_geri_al),
            ft.TextButton(content=ft.Row([ft.Text("⟳", size=20), ft.Text(L['ileri_al'], size=16, color=ayarlar.TEMA_RENKLER["vurgu_mavi"])]), on_click=tetik_ileri_al)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        alt_menu = ft.Column(spacing=20, controls=[
            ft.Divider(color=ayarlar.TEMA_RENKLER["metin_ikincil"]),
            ft.TextButton(content=ft.Row([ft.Text("🌐", size=22), ft.Text("Dil / Language", size=17, color=ayarlar.TEMA_RENKLER["metin_ikincil"])]), on_click=lambda _: setattr(ayarlar, 'DIL', "EN" if ayarlar.DIL == "TR" else "TR") or sayfa_degistir(page.aktif_sekme)),
            ft.TextButton(content=ft.Row([ft.Text("🌗", size=22), ft.Text(L["tema_degis"], size=17, color=ayarlar.TEMA_RENKLER["metin_ikincil"])]), on_click=tema_degistir),
            ft.TextButton(content=ft.Row([ft.Text("ℹ️", size=22), ft.Text(L["baglanti_bilgi"], size=17, color=ayarlar.TEMA_RENKLER["vurgu_mavi"])]), on_click=baglanti_bilgim_ac),
            ft.TextButton(content=ft.Row([ft.Text("👤", size=22), ft.Text(L["kullanici_degis"], size=17, color=ayarlar.TEMA_RENKLER["metin_ikincil"])]), on_click=lambda e: sayfa_degistir("kullanici")),
            ft.TextButton(content=ft.Row([ft.Text("🔌", size=22), ft.Text(L["baglanti_kes"], size=17, color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"])]), on_click=baglanti_kes_uyari)
        ])

        return ft.Container(
            width=300, 
            bgcolor=ayarlar.TEMA_RENKLER["kart"], 
            padding=25, 
            content=ft.Column(controls=[
                ust_menu,
                ft.Container(expand=True),
                orta_butonlar,
                ft.Container(height=30),
                alt_menu
            ])
        )

    son_kayitli_link = veri.son_linki_getir()
    if son_kayitli_link and veri.baglanti_kur(son_kayitli_link)[0]: sayfa_degistir("kullanici")
    else: sayfa_degistir("baglanti")

if __name__ == "__main__":
    ft.run(main)