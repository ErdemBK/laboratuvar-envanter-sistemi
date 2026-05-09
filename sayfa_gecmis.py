import customtkinter as ctk
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager

class GecmisSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ust_frame = ctk.CTkFrame(self, fg_color="transparent")
        ust_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(
            ust_frame, text=metinler[self.app.aktif_dil]["gecmis"], 
            font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            ust_frame, text=metinler[self.app.aktif_dil]["gecmisi_disa_aktar"], 
            font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], 
            height=35, command=self.gecmis_export
        ).pack(side="right", padx=10)

        self.liste_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=5)
        
        self.gecmisi_yenile()

    def gecmisi_yenile(self):
        for w in self.liste_frame.winfo_children():
            w.destroy()
            
        kayitlar = self.db.gecmisi_getir()
        dil = self.app.aktif_dil
        
        if not kayitlar:
            ctk.CTkLabel(
                self.liste_frame, text=metinler[dil]["islem_yok"], 
                font=FontManager.get_font(16), text_color=renkler["yazi_ikincil"]
            ).pack(pady=40)
            return
            
        for k in kayitlar:
            f = ctk.CTkFrame(self.liste_frame, fg_color=renkler["kart"], corner_radius=8)
            f.pack(fill="x", pady=4, padx=5)
            
            tarih = k['tarih'][:16]
            metin = f"[{tarih}] 👤 {k['kullanici']} : '{k['malzeme_isim']}' -> {k['detay']}"
            
            ctk.CTkLabel(
                f, text=metin, font=FontManager.get_font(14), 
                text_color=renkler["yazi_ana"], anchor="w", justify="left"
            ).pack(fill="x", padx=15, pady=12)

    def gecmis_export(self):
        import csv
        from tkinter import filedialog
        from ui_bilesenleri import OzelBilgiKutusu
        
        y = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
        if not y: 
            return
            
        try:
            with open(y, 'w', newline='', encoding='utf-8-sig') as f:
                wr = csv.writer(f, delimiter=';')
                wr.writerow(["ID", "Tarih", "Kullanıcı", "Malzeme", "İşlem Detayı"])
                for k in self.db.gecmisi_getir():
                    wr.writerow([k['id'], k['tarih'], k['kullanici'], k['malzeme_isim'], k['detay']])
                    
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Geçmiş dışa aktarıldı.", renk=renkler["basari"])
        except Exception as e:
            OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])