import customtkinter as ctk
from modeller import Malzeme, IslemTipi, stok_metni_olustur, miktar_dogrula, UndoIslemi
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelBilgiKutusu

class EkleSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ctk.CTkLabel(self, text=metinler[self.app.aktif_dil]["yeni_ekle"], font=FontManager.get_font(26, "bold")).pack(pady=(10, 20), anchor="w", padx=20)
        f = ctk.CTkScrollableFrame(self, fg_color="transparent"); f.pack(fill="both", expand=True, padx=20)
        f.grid_columnconfigure(0, weight=0, minsize=160); f.grid_columnconfigure(1, weight=1)
        
        birimler = metinler[self.app.aktif_dil]["birimler"]
        L_font = FontManager.get_font(15)

        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["malzeme_adi"], font=L_font).grid(row=0, column=0, padx=10, pady=12, sticky="w")
        self.e_isim = ctk.CTkEntry(f, width=250, placeholder_text=metinler[self.app.aktif_dil]["orn_isim"]); self.e_isim.grid(row=0, column=1, padx=10, pady=12, sticky="w")
        
        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["lokasyon"], font=L_font).grid(row=1, column=0, padx=10, pady=12, sticky="w")
        self.e_lok = ctk.CTkEntry(f, width=250, placeholder_text=metinler[self.app.aktif_dil]["orn_lok"]); self.e_lok.grid(row=1, column=1, padx=10, pady=12, sticky="w")

        def m_satir(r, key, ph):
            ctk.CTkLabel(f, text=metinler[self.app.aktif_dil][key], font=L_font).grid(row=r, column=0, padx=10, pady=12, sticky="w")
            fr = ctk.CTkFrame(f, fg_color="transparent"); fr.grid(row=r, column=1, sticky="w", padx=10)
            e = ctk.CTkEntry(fr, width=120, placeholder_text=metinler[self.app.aktif_dil][ph]); e.pack(side="left")
            c = ctk.CTkComboBox(fr, values=birimler, width=120); c.pack(side="left", padx=10)
            return e, c

        self.e_m1, self.c_b1 = m_satir(2, "ana_miktar", "miktar_zorunlu")
        self.e_m2, self.c_b2 = m_satir(3, "ek_miktar_2", "opsiyonel")
        self.e_m3, self.c_b3 = m_satir(4, "ek_miktar_3", "opsiyonel")

        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["notlar"], font=L_font).grid(row=5, column=0, padx=10, pady=12, sticky="nw")
        self.t_not = ctk.CTkTextbox(f, width=250, height=80); self.t_not.grid(row=5, column=1, padx=10, pady=12, sticky="w")

        ctk.CTkButton(f, text=metinler[self.app.aktif_dil]["kaydet"], font=FontManager.get_font(16, "bold"), fg_color=renkler["buton_mavi"], height=45, command=self.malzeme_kaydet).grid(row=6, column=0, columnspan=2, pady=30, sticky="w", padx=10)

    def malzeme_kaydet(self):
        try:
            isim = self.e_isim.get().strip()
            if not isim: OzelBilgiKutusu(self.winfo_toplevel(), "Eksik", "İsim girin!", renk=renkler["uyari"]); return
            
            m1, m2, m3 = miktar_dogrula(self.e_m1.get().strip()), miktar_dogrula(self.e_m2.get().strip()), miktar_dogrula(self.e_m3.get().strip())
            y_m = Malzeme(isim=isim, ambalaj_tipi="", miktar=m1, birim=self.c_b1.get(), ikinci_miktar=m2, ikinci_birim=self.c_b2.get(), ucuncu_miktar=m3, ucuncu_birim=self.c_b3.get(), donusum_orani=0.0, lokasyon=self.e_lok.get().strip(), notlar=self.t_not.get("1.0", "end-1c"))
            
            y_id = self.db.malzeme_ekle(y_m); y_m.id = y_id
            
            # DINAMIK LOG
            dil = self.app.aktif_dil
            # DÜZELTME: aktif_dil eklendi
            stok_log = stok_metni_olustur(m1, y_m.birim, m2, y_m.ikinci_birim, m3, y_m.ucuncu_birim, aktif_dil=dil)
            islem_metni = f"{metinler[dil]['log_eklendi']} ({metinler[dil]['log_miktar']}: {stok_log})"
            
            log_id = self.db.gecmis_ekle(y_id, isim, islem_metni, self.app.kullanici_adi)
            
            self.app.islem_gecmisi.append(UndoIslemi(tip="ekleme", malzeme_id=y_id, malzeme_isim=isim, log_id=log_id, yeni_malzeme=y_m))
            for e in [self.e_isim, self.e_m1, self.e_m2, self.e_m3, self.e_lok]: e.delete(0, 'end')
            self.t_not.delete("1.0", "end"); OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"'{isim}' eklendi!", renk=renkler["basari"]); self.app.gui_guncelle()
        except ValueError as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])