# sayfa_envanter.py
import flet as ft
import ayarlar
import ui_bilesenleri
import veri
import datetime

def envanter_gorunumu(page: ft.Page):
    L = ayarlar.LOCALIZED[ayarlar.DIL]
    
    def arama_yapildi(e): listeyi_yenile(arama_metni=e.control.value)

    arama_kutusu = ft.TextField(label=L["arama_label"], border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"], on_change=arama_yapildi)
    sonuc_yok_alani = ft.Container(content=ft.Text(L["sonuc_yok"], size=25, color=ayarlar.TEMA_RENKLER["metin_ikincil"]), visible=False)
    liste_alani = ft.ListView(expand=True, spacing=10, padding=10)

    def excel_indir_fiziksel(e):
        bugun = datetime.datetime.now().strftime("%Y_%m_%d")
        yol = ui_bilesenleri.dosya_kaydet_dialog(
            "Excel (CSV) Nereye Kaydedilsin?" if ayarlar.DIL == "TR" else "Save CSV As", 
            f"lab_envanter_{bugun}.csv", ".csv"
        )
        if yol:
            with open(yol, "w", encoding="utf-8-sig") as f:
                f.write("ID;Konum;Malzeme Adi;Miktarlar;Notlar\n")
                sirali_malzemeler = sorted(veri.MALZEMELER, key=lambda x: str(x.get('konum', '')).lower())
                for m in sirali_malzemeler:
                    miks = ", ".join([f"{k['deger']} {k['birim']}" for k in m.get('miktarlar', [])])
                    notlar = m.get('notlar', '').replace('\n', ' ')
                    f.write(f"{m['id']};{m['konum']};{m['isim']};{miks};{notlar}\n")
            ui_bilesenleri.goster_toast(page, "Excel Başarıyla Kaydedildi!" if ayarlar.DIL == "TR" else "Excel Saved!", True)

    def notu_goster(e):
        malzeme = e.control.data
        dlg = ft.AlertDialog(title=ft.Text(f"📝 {malzeme['isim']}"), content=ft.Text(malzeme['notlar']), bgcolor=ayarlar.TEMA_RENKLER["kart"])
        ui_bilesenleri.dialog_ac(page, dlg)

    def gelismis_guncelle(e):
        m = e.control.data
        isim_edt = ft.TextField(label="Malzeme Adı" if ayarlar.DIL == "TR" else "Material Name", value=m["isim"], border_color=ayarlar.TEMA_RENKLER["vurgu_mavi"])
        konum_edt = ft.Dropdown(label="Konum" if ayarlar.DIL == "TR" else "Location", value=m["konum"], options=[ft.dropdown.Option(k) for k in veri.KONUMLAR] + [ft.dropdown.Option("Yer Belirtilmiyor")])
        not_edt = ft.TextField(label="Notlar" if ayarlar.DIL == "TR" else "Notes", value=m["notlar"], multiline=True)
        
        satirlar_box = ft.Column(spacing=5)
        BIRIMLER = ["Adet", "Litre", "ml", "Kg", "Gram", "mg", "Kutu", "Koli", "Paket", "Rulo", "Şişe"]

        def miktar_satiri_ekle(deger="", birim="Adet"):
            s = ft.Row([
                ft.TextField(label="Miktar" if ayarlar.DIL == "TR" else "Qty", value=deger, width=120),
                ft.Dropdown(value=birim, options=[ft.dropdown.Option(b) for b in BIRIMLER], width=120)
            ])
            satirlar_box.controls.append(s)

        for miktar in m["miktarlar"]: miktar_satiri_ekle(miktar["deger"], miktar["birim"])

        def yeni_satir_tetik(_):
            if len(satirlar_box.controls) < 5: miktar_satiri_ekle(); page.update()
            else: ui_bilesenleri.goster_toast(page, "Maksimum 5 miktar sınırı!" if ayarlar.DIL == "TR" else "Max 5 quantity limits!", False)

        def kaydet_aksiyon(_):
            veri.anim_kaydet()
            
            # Değişiklik analizi için eski değerleri koru
            eski_isim = m["isim"]
            eski_konum = m["konum"]
            eski_notlar = m["notlar"]
            eski_miktarlar_str = ", ".join([f"{k['deger']} {k['birim']}" for k in m.get('miktarlar', [])])
            
            # Yeni değerleri formdan topla
            yeni_isim = isim_edt.value
            yeni_konum = konum_edt.value if konum_edt.value else "Yer Belirtilmiyor"
            yeni_notlar = not_edt.value
            
            yeni_mik = []
            for c in satirlar_box.controls:
                if c.controls[0].value: 
                    yeni_mik.append({"deger": c.controls[0].value, "birim": c.controls[1].value})
            yeni_miktarlar_str = ", ".join([f"{k['deger']} {k['birim']}" for k in yeni_mik])
            
            # Değişen alanları tespit et ve detaylı mesaj oluştur
            degisimler = []
            if eski_isim != yeni_isim:
                degisimler.append(f"İsim: '{eski_isim}' -> '{yeni_isim}'" if ayarlar.DIL == "TR" else f"Name: '{eski_isim}' -> '{yeni_isim}'")
            if eski_konum != yeni_konum:
                degisimler.append(f"Konum: '{eski_konum}' -> '{yeni_konum}'" if ayarlar.DIL == "TR" else f"Location: '{eski_konum}' -> '{yeni_konum}'")
            if eski_notlar != yeni_notlar:
                degisimler.append("Notlar güncellendi" if ayarlar.DIL == "TR" else "Notes updated")
            if eski_miktarlar_str != yeni_miktarlar_str:
                eski_yaz = eski_miktarlar_str if eski_miktarlar_str else "0"
                yeni_yaz = yeni_miktarlar_str if yeni_miktarlar_str else "0"
                degisimler.append(f"Miktar: [{eski_yaz}] -> [{yeni_yaz}]" if ayarlar.DIL == "TR" else f"Qty: [{eski_yaz}] -> [{yeni_yaz}]")
            
            # Eğer hiçbir şey değişmediyse loglama yapma
            if degisimler:
                detay_metni = f"'{eski_isim}' - " + " | ".join(degisimler)
                zaman = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
                islem_adi = "Güncellendi" if ayarlar.DIL == "TR" else "Updated"
                veri.GECMIS.insert(0, {"islem": islem_adi, "tarih": zaman, "kullanici": veri.aktif_kullanici, "detay": detay_metni})
            
            # Gerçek verileri güncelle
            m["isim"] = yeni_isim
            m["konum"] = yeni_konum
            m["notlar"] = yeni_notlar
            m["miktarlar"] = yeni_mik
            
            veri.verileri_kaydet()
            ui_bilesenleri.dialog_kapat(page, dlg_edt); listeyi_yenile()
            ui_bilesenleri.goster_toast(page, "Güncellendi!" if ayarlar.DIL == "TR" else "Updated!", True)

        dlg_edt = ft.AlertDialog(
            title=ft.Text(f"✏️ {m['isim']}"),
            content=ft.Column([
                isim_edt, konum_edt, not_edt,
                ft.Row([ft.Text("Miktarlar" if ayarlar.DIL == "TR" else "Quantities"), ft.TextButton("➕ Satır Ekle" if ayarlar.DIL == "TR" else "➕ Add Row", on_click=yeni_satir_tetik)]),
                satirlar_box
            ], tight=True, scroll=ft.ScrollMode.AUTO, height=450),
            bgcolor=ayarlar.TEMA_RENKLER["kart"],
            actions=[
                ft.TextButton("İptal" if ayarlar.DIL == "TR" else "Cancel", on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg_edt)),
                ft.ElevatedButton("Kaydet" if ayarlar.DIL == "TR" else "Save", color="#FFFFFF", bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], on_click=kaydet_aksiyon)
            ]
        )
        ui_bilesenleri.dialog_ac(page, dlg_edt)

    def sil(e):
        malzeme = e.control.data
        def onayla(e2):
            veri.anim_kaydet()
            veri.MALZEMELER.remove(malzeme)
            zaman = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
            veri.GECMIS.insert(0, {"islem": "Silindi" if ayarlar.DIL == "TR" else "Deleted", "tarih": zaman, "kullanici": veri.aktif_kullanici, "detay": f"'{malzeme['isim']}' silindi." if ayarlar.DIL == "TR" else f"'{malzeme['isim']}' deleted."})
            veri.verileri_kaydet()
            ui_bilesenleri.dialog_kapat(page, dlg); listeyi_yenile(arama_kutusu.value)
            ui_bilesenleri.goster_toast(page, "Silindi!" if ayarlar.DIL == "TR" else "Deleted!", False)
            
        dlg = ft.AlertDialog(title=ft.Text("Emin Misiniz?" if ayarlar.DIL == "TR" else "Are you sure?"), content=ft.Text(f"'{malzeme['isim']}' silinecek." if ayarlar.DIL == "TR" else f"'{malzeme['isim']}' will be deleted."), bgcolor=ayarlar.TEMA_RENKLER["kart"],
            actions=[ft.TextButton("İptal" if ayarlar.DIL == "TR" else "Cancel", on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton("Evet, Sil" if ayarlar.DIL == "TR" else "Yes, Delete", on_click=onayla, icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"])])
        ui_bilesenleri.dialog_ac(page, dlg)

    def listeyi_yenile(arama_metni=""):
        liste_alani.controls.clear()
        arama_metni = arama_metni.lower() if arama_metni else ""
        eslesenler = [m for m in veri.MALZEMELER if arama_metni in m["isim"].lower() or arama_metni in m["konum"].lower()]
        
        eslesenler = sorted(eslesenler, key=lambda x: str(x['isim']).lower())
        
        if not eslesenler: sonuc_yok_alani.visible = True
        else:
            sonuc_yok_alani.visible = False
            for m in eslesenler:
                rozetler = ft.Row(spacing=5)
                for miktar in m["miktarlar"]: rozetler.controls.append(ft.Container(bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], padding=8, border_radius=15, content=ft.Text(f"{miktar['deger']} {miktar['birim']}", color="#FFFFFF", weight="bold", size=13)))

                kart = ft.Container(
                    bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=15, border_radius=10,
                    content=ft.Row([
                        ft.Column([ft.Text(m["isim"], color=ayarlar.TEMA_RENKLER["metin_ana"], size=16, weight="bold", no_wrap=True, overflow="ellipsis"), ft.Text(m["konum"], color=ayarlar.TEMA_RENKLER["uyari_sari"] if m["konum"] != "Yer Belirtilmiyor" else ayarlar.TEMA_RENKLER["metin_ikincil"], size=12, no_wrap=True, overflow="ellipsis")], expand=True),
                        rozetler,
                        ft.ElevatedButton("📝 Notlar" if ayarlar.DIL == "TR" else "📝 Notes", bgcolor=ayarlar.TEMA_RENKLER["uyari_sari"], color="black", data=m, on_click=notu_goster, visible=bool(m["notlar"])),
                        ft.TextButton("✏️", tooltip="Güncelle" if ayarlar.DIL == "TR" else "Update", data=m, on_click=gelismis_guncelle),
                        ft.TextButton("🗑️", data=m, on_click=sil)
                    ], alignment="spaceBetween", vertical_alignment="center")
                )
                liste_alani.controls.append(kart)
        page.update()

    listeyi_yenile()
    return ft.Column([
        ft.Row([ft.Text(f"📦 {L['envanter']}", size=30, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Container(expand=True), ft.ElevatedButton(L["excel_aktar"], bgcolor=ayarlar.TEMA_RENKLER["basari_yesil"], color="#FFFFFF", on_click=excel_indir_fiziksel)]),
        ft.Container(height=10), arama_kutusu, ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=20), ft.Row([ft.Container(expand=True), sonuc_yok_alani, ft.Container(expand=True)]), liste_alani
    ], expand=True)