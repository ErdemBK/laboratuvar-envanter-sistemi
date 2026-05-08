# dosya: sayfa_gecmis.py
# ---------------------------------------------------------
import customtkinter as ctk
from tkinter import filedialog
import csv
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelBilgiKutusu

class GecmisSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ust_frame = ctk.CTkFrame(self, fg_color="transparent")
        ust_frame.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkLabel(ust_frame, text=metinler[self.app.aktif_dil]["gecmis"], font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]).pack(side="left")
        btn_export = ctk.CTkButton(ust_frame, text=metinler[self.app.aktif_dil]["gecmisi_disa_aktar"], font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], hover_color="#059669", height=35, command=self.excel_gecmisi_disa_aktar)
        btn_export.pack(side="right")

        self.liste_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.gecmisi_yenile()

    def gecmisi_yenile(self):
        for widget in self.liste_frame.winfo_children(): widget.destroy()
        kayitlar = self.db.gecmis_getir()
        if not kayitlar: ctk.CTkLabel(self.liste_frame, text=metinler[self.app.aktif_dil]["islem_yok"], text_color=renkler["yazi_ikincil"], font=FontManager.get_font(15)).pack(pady=40)
        else:
            for k in kayitlar: 
                f = ctk.CTkFrame(self.liste_frame, fg_color=renkler["kart"], corner_radius=8)
                f.pack(fill="x", pady=4)
                m_isim = k['malzeme_ismi'] if k['malzeme_ismi'] else "(Silinmiş Eski Malzeme)"
                metin = f"[{k['islem_tarihi'][:16]}] 👤 {k['kullanici']} : '{m_isim}' -> {k['islem_tipi']}"
                ctk.CTkLabel(f, text=metin, font=FontManager.get_font(14), text_color=renkler["yazi_ana"], wraplength=900).pack(anchor="w", pady=10, padx=15)

    def excel_gecmisi_disa_aktar(self):
        dosya_yolu = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")], title="Kaydet")
        if not dosya_yolu: return
        try:
            with open(dosya_yolu, 'w', newline='', encoding='utf-8-sig') as dosya:
                yazici = csv.writer(dosya, delimiter=';')
                yazici.writerow(["Tarih", "Kullanıcı", "Malzeme Adı", "İşlem Detayı"])
                for k in self.db.gecmis_getir(): 
                    m_isim = k['malzeme_ismi'] if k['malzeme_ismi'] else "(Silinmiş Eski Malzeme)"
                    yazici.writerow([k['islem_tarihi'], k['kullanici'], m_isim, k['islem_tipi']])
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"Dışa aktarıldı:\n{dosya_yolu}", renk=renkler["basari"])
        except Exception as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])