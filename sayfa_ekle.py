import customtkinter as ctk
from modeller import Malzeme, IslemTipi, stok_metni_olustur, miktar_dogrula, UndoIslemi
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelBilgiKutusu, OzelOnayKutusu

class EkleSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.miktar_satirlari = []
        self.kur()

    def kur(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.miktar_satirlari.clear()

        ctk.CTkLabel(
            self, text=metinler[self.app.aktif_dil]["yeni_ekle"], 
            font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]
        ).pack(pady=(10, 20), anchor="w", padx=20)
        
        self.f_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.f_scroll.pack(fill="both", expand=True, padx=20)
        
        self.e_isim = self.field_ekle("malzeme_adi", "orn_isim")
        self.e_lok = self.field_ekle("lokasyon", "orn_lok")
        
        self.miktar_frame = ctk.CTkFrame(self.f_scroll, fg_color="transparent")
        self.miktar_frame.pack(fill="x", pady=10)
        
        self.yeni_satir_ekle()
        
        self.btn_artir = ctk.CTkButton(
            self.f_scroll, text=metinler[self.app.aktif_dil]["miktar_ekle"], 
            command=self.yeni_satir_ekle, fg_color="transparent", 
            border_width=1, border_color=renkler["buton_mavi"], text_color=renkler["buton_mavi"]
        )
        self.btn_artir.pack(pady=10, anchor="w", padx=10)
        
        ctk.CTkLabel(
            self.f_scroll, text=metinler[self.app.aktif_dil]["notlar"], 
            font=FontManager.get_font(15), text_color=renkler["yazi_ana"]
        ).pack(anchor="w", padx=10)
        
        self.t_not = ctk.CTkTextbox(self.f_scroll, width=400, height=80, font=FontManager.get_font(14))
        self.t_not.pack(padx=10, pady=5, anchor="w")
        
        btn_f = ctk.CTkFrame(self.f_scroll, fg_color="transparent")
        btn_f.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_f, text=metinler[self.app.aktif_dil]["kaydet"], fg_color=renkler["basari"], 
            font=FontManager.get_font(14, "bold"), command=self.malzeme_kaydet
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_f, text=metinler[self.app.aktif_dil]["temizle"], fg_color=renkler["tehlike"], 
            font=FontManager.get_font(14, "bold"), command=self.temizle_onay
        ).pack(side="left", padx=10)

    def field_ekle(self, key, ph):
        fr = ctk.CTkFrame(self.f_scroll, fg_color="transparent")
        fr.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            fr, text=metinler[self.app.aktif_dil][key], width=150, anchor="w",
            font=FontManager.get_font(14), text_color=renkler["yazi_ana"]
        ).pack(side="left", padx=10)
        
        e = ctk.CTkEntry(
            fr, width=250, placeholder_text=metinler[self.app.aktif_dil][ph], font=FontManager.get_font(14)
        )
        e.pack(side="left")
        return e

    def yeni_satir_ekle(self):
        if len(self.miktar_satirlari) >= 5: 
            return
            
        fr = ctk.CTkFrame(self.miktar_frame, fg_color="transparent")
        fr.pack(fill="x", pady=2)
        
        lbl_metin = f"{len(self.miktar_satirlari)+1}. {metinler[self.app.aktif_dil]['log_miktar']}"
        
        ctk.CTkLabel(
            fr, text=lbl_metin, width=150, anchor="w",
            font=FontManager.get_font(14), text_color=renkler["yazi_ana"]
        ).pack(side="left", padx=10)
        
        e = ctk.CTkEntry(fr, width=120, font=FontManager.get_font(14))
        e.pack(side="left")
        
        c = ctk.CTkComboBox(
            fr, values=metinler[self.app.aktif_dil]["birimler"], 
            width=120, font=FontManager.get_font(14)
        )
        c.pack(side="left", padx=10)
        
        self.miktar_satirlari.append((e, c))
        
        if len(self.miktar_satirlari) == 5: 
            self.btn_artir.configure(state="disabled")

    def temizle_onay(self):
        OzelOnayKutusu(
            self.winfo_toplevel(), metinler[self.app.aktif_dil]["onay_baslik"], 
            metinler[self.app.aktif_dil]["emin_misin_temizle"], self.kur
        )

    def malzeme_kaydet(self):
        try:
            isim = self.e_isim.get().strip()
            dil = self.app.aktif_dil
            
            if not isim: 
                OzelBilgiKutusu(self.winfo_toplevel(), "Hata", "Lütfen malzeme adını giriniz!", renk=renkler["tehlike"])
                return
                
            m_vals = [miktar_dogrula(e.get()) for e, c in self.miktar_satirlari]
            b_vals = [c.get() for e, c in self.miktar_satirlari]
            
            while len(m_vals) < 5:
                m_vals.append(0.0)
                b_vals.append("")
                
            y_m = Malzeme(
                isim=isim, 
                miktar=m_vals[0], birim=b_vals[0], 
                ikinci_miktar=m_vals[1], ikinci_birim=b_vals[1], 
                ucuncu_miktar=m_vals[2], ucuncu_birim=b_vals[2], 
                dorduncu_miktar=m_vals[3], dorduncu_birim=b_vals[3],
                besinci_miktar=m_vals[4], besinci_birim=b_vals[4],
                lokasyon=self.e_lok.get().strip(), notlar=self.t_not.get("1.0", "end-1c")
            )
            
            y_id = self.db.malzeme_ekle(y_m)
            y_m.id = y_id
            
            stok_log = stok_metni_olustur(m_vals[0], b_vals[0], m_vals[1], b_vals[1], m_vals[2], b_vals[2], m_vals[3], b_vals[3], m_vals[4], b_vals[4], aktif_dil=dil)
            islem_metni = f"{metinler[dil]['log_eklendi']} ({metinler[dil]['log_miktar']}: {stok_log})"
            
            log_id = self.db.gecmis_ekle(y_id, isim, islem_metni, self.app.kullanici_adi)
            
            self.app.islem_gecmisi.append(UndoIslemi(tip="ekleme", malzeme_id=y_id, malzeme_isim=isim, log_id=log_id, yeni_malzeme=y_m))
            self.app.ileri_gecmisi.clear()
            
            self.kur() 
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"'{isim}' başarıyla eklendi!", renk=renkler["basari"])
            self.app.gui_guncelle()
            
        except Exception as e: 
            OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])