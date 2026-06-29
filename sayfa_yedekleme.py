# sayfa_yedekleme.py
import flet as ft
import ayarlar
import ui_bilesenleri
import datetime
import json
import veri

def yedekleme_gorunumu(page: ft.Page):
    d = ayarlar.dil
    def yedek_indir(e, tip):
        bugun = datetime.datetime.now().strftime("%Y_%m_%d")
        if tip == "csv":
            yol = ui_bilesenleri.dosya_kaydet_dialog(d("Excel (CSV) Kaydet", "Save CSV"), f"lab_yedek_{bugun}.csv", ".csv")
            if yol:
                with open(yol, "w", encoding="utf-8-sig") as f:
                    f.write("ID;Konum;Malzeme Adi;Miktarlar;Notlar\n")
                    sirali = sorted(veri.MALZEMELER, key=lambda x: str(x.get('konum', '')).lower())
                    for m in sirali: 
                        miks = ", ".join([f"{k['deger']} {k['birim']}" for k in m.get('miktarlar', [])])
                        notlar = m.get('notlar', '').replace('\n', ' ')
                        f.write(f"{m['id']};{m['konum']};{m['isim']};{miks};{notlar}\n")
                ui_bilesenleri.goster_toast(page, d("Excel İndirildi!", "Excel Saved!"), True)
        else:
            yol = ui_bilesenleri.dosya_kaydet_dialog(d("Veritabanı Kaydet", "Save DB"), f"lab_db_{bugun}.json", ".json")
            if yol:
                data = {"kullanicilar": veri.KULLANICILAR, "konumlar": veri.KONUMLAR, "malzemeler": veri.MALZEMELER, "gecmis": veri.GECMIS}
                with open(yol, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
                ui_bilesenleri.goster_toast(page, d("Veritabanı İndirildi!", "DB Saved!"), True)

    def yedek_yukle(e, tip):
        yol = ui_bilesenleri.dosya_sec_dialog(d("Dosya Seç", "Select File"), f".{tip}")
        if not yol: return
        
        def onayla(e2):
            try:
                veri.anim_kaydet()
                if tip == "json":
                    with open(yol, "r", encoding="utf-8") as f: data = json.load(f)
                    veri.KULLANICILAR[:] = data.get("kullanicilar", [])
                    veri.KONUMLAR[:] = data.get("konumlar", [])
                    veri.MALZEMELER[:] = data.get("malzemeler", [])
                    veri.GECMIS[:] = data.get("gecmis", [])
                elif tip == "csv":
                    # Excel CSV Okuma Motoru (İndirilen formatı tanır)
                    with open(yol, "r", encoding="utf-8-sig") as f: lines = f.readlines()[1:]
                    yeni_malzemeler = []
                    import random
                    for l in lines:
                        parts = l.strip().split(";")
                        if len(parts) >= 4:
                            _id = int(parts[0]) if parts[0].isdigit() else random.randint(100,99999)
                            konum = parts[1]
                            isim = parts[2]
                            mik_str = parts[3]
                            notlar = parts[4] if len(parts) > 4 else ""
                            miks = []
                            for par in mik_str.split(", "):
                                m_parts = par.strip().split(" ")
                                if len(m_parts) >= 2: miks.append({"deger": m_parts[0], "birim": " ".join(m_parts[1:])})
                                elif len(m_parts) == 1 and m_parts[0]: miks.append({"deger": m_parts[0], "birim": "Adet"})
                            yeni_malzemeler.append({"id": _id, "isim": isim, "konum": konum, "miktarlar": miks, "notlar": notlar})
                    veri.MALZEMELER[:] = yeni_malzemeler

                veri.verileri_kaydet()
                ui_bilesenleri.dialog_kapat(page, dlg)
                ui_bilesenleri.goster_toast(page, d("Yüklendi!", "Restored!"), True)
            except Exception as err:
                ui_bilesenleri.dialog_kapat(page, dlg)
                ui_bilesenleri.goster_toast(page, d("Dosya okunamadı!", "File corrupt!"), False)

        dlg = ft.AlertDialog(title=ft.Text(d("DİKKAT: Veriler Silinecek!", "WARNING: Data overwrite!"), color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"]),
            content=ft.Text(d("Mevcut veriler yedeğin üzerine yazılacaktır. Emin misiniz?", "Current data will be replaced. Sure?")), bgcolor=ayarlar.TEMA_RENKLER["kart"],
            actions=[ft.TextButton(d("İptal", "Cancel"), on_click=lambda _: ui_bilesenleri.dialog_kapat(page, dlg)), ft.TextButton(d("Evet, Yükle", "Yes, Restore"), icon_color=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], on_click=onayla)])
        ui_bilesenleri.dialog_ac(page, dlg)

    kart_disa_aktar = ft.Container(bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=20, border_radius=10, expand=True, content=ft.Column([
        ft.Text("☁️", size=40), ft.Text(d("Dışa Aktar (Export)", "Export Database"), size=20, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]),
        ft.Container(height=10),
        ft.ElevatedButton(d("⬇️ Excel (CSV) İndir", "⬇️ Download Excel (CSV)"), on_click=lambda e: yedek_indir(e, "csv")),
        ft.ElevatedButton(d("⬇️ Veritabanı (JSON) İndir", "⬇️ Download DB (JSON)"), on_click=lambda e: yedek_indir(e, "json"))
    ]))

    # Yükleme için Excel (CSV) opsiyonu geri getirildi!
    kart_ice_aktar = ft.Container(bgcolor=ayarlar.TEMA_RENKLER["kart"], padding=20, border_radius=10, expand=True, content=ft.Column([
        ft.Text("🖥️", size=40), ft.Text(d("Geri Yükle (Restore)", "Restore Database"), size=20, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]),
        ft.Container(height=10),
        ft.ElevatedButton(d("⬆️ Excel (CSV) Yükle", "⬆️ Restore Excel (CSV)"), bgcolor=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], color="#FFFFFF", on_click=lambda e: yedek_yukle(e, "csv")),
        ft.ElevatedButton(d("⬆️ Veritabanı (JSON) Yükle", "⬆️ Restore DB (JSON)"), bgcolor=ayarlar.TEMA_RENKLER["tehlike_kirmizi"], color="#FFFFFF", on_click=lambda e: yedek_yukle(e, "json"))
    ]))

    return ft.Column([ft.Text(d("💾 Yedekleme", "💾 Backup"), size=30, weight="bold", color=ayarlar.TEMA_RENKLER["metin_ana"]), ft.Divider(color=ayarlar.TEMA_RENKLER["kart"], height=30), ft.Row([kart_disa_aktar, kart_ice_aktar], spacing=20, alignment="start")], expand=True)