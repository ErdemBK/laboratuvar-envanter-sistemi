# sayfa_baglanti.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri
import webbrowser

def baglanti_gorunumu(page: ft.Page):
    link_input = ft.TextField(label="Bulut Bağlantı Linki (DB URL)" if ayarlar.DIL == "TR" else "Cloud Connection Link (DB URL)", border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], password=True, can_reveal_password=True, expand=True)

    def baglan_tiklandi(e):
        if not link_input.value: ui_bilesenleri.goster_toast(page, "Lütfen linkinizi giriniz!" if ayarlar.DIL == "TR" else "Please enter your link!", False); return
        ui_bilesenleri.goster_toast(page, "Buluta bağlanılıyor, bekleyin..." if ayarlar.DIL == "TR" else "Connecting to cloud...", True)
        basarili_mi, mesaj = veri.baglanti_kur(link_input.value)
        if basarili_mi:
            ui_bilesenleri.goster_toast(page, "Bağlanıldı!" if ayarlar.DIL == "TR" else "Connected!", True); page.sayfa_degistir("kullanici")
        else:
            ui_bilesenleri.goster_toast(page, mesaj, False)

    neon_link_butonu = ft.ElevatedButton(
        content=ft.Row([ft.Text("🌐 Neon.tech Giriş Sayfası için Tıklayın" if ayarlar.DIL == "TR" else "🌐 Click for Neon.tech Login", color="#FFFFFF", weight="bold")], alignment="center"),
        bgcolor=ayarlar.TEMA_RENKLER["vurgu_mavi"], height=40, on_click=lambda _: webbrowser.open("https://neon.tech/")
    )

    talimatlar = ft.Container(
        bgcolor=ayarlar.TEMA_RENKLER["arkaplan"], padding=20, border_radius=10,
        content=ft.Column([
            neon_link_butonu, ft.Container(height=5),
            ft.Text(
                "1. Yukarıdaki linke tıklayıp giriş yapın.\n2. 'Create Project' ile proje oluşturun.\n3. Region: Frankfurt seçin.\n4. Connection string kısmını bulun.\n5. postgresql:// linkini kopyalayıp yapıştırın." if ayarlar.DIL == "TR" else
                "1. Click the link above and log in.\n2. Create a project via 'Create Project'.\n3. Select Region: Frankfurt.\n4. Find the 'Connection string' section.\n5. Copy and paste the postgresql:// link.", 
                size=13, color=ayarlar.TEMA_RENKLER["metin_ikincil"]
            )
        ])
    )

    def dil_degis(e):
        ayarlar.DIL = "EN" if ayarlar.DIL == "TR" else "TR"
        page.sayfa_degistir("baglanti")

    return ft.Container(
        bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=40, border_radius=15, width=550,
        content=ft.Column([
            ft.Row([ft.Text("☁️", size=40), ft.Container(expand=True), ft.TextButton("🌐 TR/EN", on_click=dil_degis)]),
            ft.Text("Sisteme Bağlan" if ayarlar.DIL == "TR" else "Connect to System", size=25, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]),
            talimatlar, ft.Container(height=10), ft.Row([link_input]), 
            ft.Text("💡 DİKKAT: Linkinizi güvenli bir yere kaydedin." if ayarlar.DIL == "TR" else "💡 ATTENTION: Save your link in a safe place.", color=ayarlar.TEMA_RENKLER["uyari_sari"], size=12, italic=True),
            ft.Container(height=10),
            # HATA BURADAYDI: "ayarlar.B TEMA_RENKLER" düzeltildi
            ft.ElevatedButton(content=ft.Text("Sisteme Giriş Yap" if ayarlar.DIL == "TR" else "Login to System", color="#FFFFFF", weight="bold"), bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], expand=True, height=50, on_click=baglan_tiklandi)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )