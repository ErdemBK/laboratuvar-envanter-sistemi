# dosya: sayfa_ekle.py
# ---------------------------------------------------------
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
        ctk.CTkLabel(self, text=metinler[self.app.aktif_dil]["yeni_ekle"], font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]).pack(pady=(10, 20), anchor="w", padx=20)
        
        form_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        form_frame.grid_columnconfigure(0, weight=0, minsize=160); form_frame.grid_columnconfigure(1, weight=1)
        
        birimler = ["Koli", "Paket", "Kutu", "Şişe", "Adet", "ml", "L", "g", "mg", ""]
        lbl_font = FontManager.get_font(15)

        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["malzeme_adi"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=0, column=0, padx=10, pady=12, sticky="w")
        self.entry_isim = ctk.CTkEntry(form_frame, width=250, placeholder_text=metinler[self.app.aktif_dil]["orn_isim"], font=FontManager.get_font(14))
        self.entry_isim.grid(row=0, column=1, padx=10, pady=12, sticky="w")
        
        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["lokasyon"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=1, column=0, padx=10, pady=12, sticky="w")
        self.entry_lokasyon = ctk.CTkEntry(form_frame, width=250, placeholder_text=metinler[self.app.aktif_dil]["orn_lok"], font=FontManager.get_font(14))
        self.entry_lokasyon.grid(row=1, column=1, padx=10, pady=12, sticky="w")

        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["ana_miktar"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=2, column=0, padx=10, pady=12, sticky="w")
        m_frame1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        m_frame1.grid(row=2, column=1, sticky="w", padx=10)
        self.entry_m1 = ctk.CTkEntry(m_frame1, width=120, placeholder_text=metinler[self.app.aktif_dil]["miktar_zorunlu"], font=FontManager.get_font(14))
        self.entry_m1.pack(side="left")
        self.combo_b1 = ctk.CTkComboBox(m_frame1, values=birimler, width=120, font=FontManager.get_font(14))
        self.combo_b1.pack(side="left", padx=10)

        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["ek_miktar_2"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=3, column=0, padx=10, pady=12, sticky="w")
        m_frame2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        m_frame2.grid(row=3, column=1, sticky="w", padx=10)
        self.entry_m2 = ctk.CTkEntry(m_frame2, width=120, placeholder_text=metinler[self.app.aktif_dil]["opsiyonel"], font=FontManager.get_font(14))
        self.entry_m2.pack(side="left")
        self.combo_b2 = ctk.CTkComboBox(m_frame2, values=birimler, width=120, font=FontManager.get_font(14))
        self.combo_b2.pack(side="left", padx=10)

        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["ek_miktar_3"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=4, column=0, padx=10, pady=12, sticky="w")
        m_frame3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        m_frame3.grid(row=4, column=1, sticky="w", padx=10)
        self.entry_m3 = ctk.CTkEntry(m_frame3, width=120, placeholder_text=metinler[self.app.aktif_dil]["opsiyonel"], font=FontManager.get_font(14))
        self.entry_m3.pack(side="left")
        self.combo_b3 = ctk.CTkComboBox(m_frame3, values=birimler, width=120, font=FontManager.get_font(14))
        self.combo_b3.pack(side="left", padx=10)

        ctk.CTkLabel(form_frame, text=metinler[self.app.aktif_dil]["notlar"], font=lbl_font, text_color=renkler["yazi_ana"]).grid(row=5, column=0, padx=10, pady=12, sticky="nw")
        self.textbox_notlar = ctk.CTkTextbox(form_frame, width=250, height=80, font=FontManager.get_font(14))
        self.textbox_notlar.grid(row=5, column=1, padx=10, pady=12, sticky="w")

        ctk.CTkButton(form_frame, text=metinler[self.app.aktif_dil]["kaydet"], font=FontManager.get_font(16, "bold"), fg_color=renkler["buton_mavi"], hover_color=renkler["buton_mavi_hover"], height=45, command=self.malzeme_kaydet).grid(row=6, column=0, columnspan=2, pady=30, sticky="w", padx=10)

    def malzeme_kaydet(self):
        try:
            isim = self.entry_isim.get().strip()
            if not isim:
                OzelBilgiKutusu(self.winfo_toplevel(), "Eksik", "Lütfen Malzeme Adı giriniz!", renk=renkler["uyari"])
                return

            m1_val, m2_val, m3_val = miktar_dogrula(self.entry_m1.get().strip()), miktar_dogrula(self.entry_m2.get().strip()), miktar_dogrula(self.entry_m3.get().strip())
            y_malz = Malzeme(
                isim=isim, ambalaj_tipi="", miktar=m1_val, birim=self.combo_b1.get(),
                ikinci_miktar=m2_val, ikinci_birim=self.combo_b2.get(), ucuncu_miktar=m3_val, ucuncu_birim=self.combo_b3.get(),
                donusum_orani=0.0, lokasyon=self.entry_lokasyon.get().strip(), notlar=self.textbox_notlar.get("1.0", "end-1c")
            )
            
            yeni_id = self.db.malzeme_ekle(y_malz)
            y_malz.id = yeni_id
            stok_log = stok_metni_olustur(m1_val, y_malz.birim, m2_val, y_malz.ikinci_birim, m3_val, y_malz.ucuncu_birim)
            log_id = self.db.gecmis_ekle(yeni_id, isim, f"{IslemTipi.EKLEME.value} (Miktar: {stok_log})", self.app.kullanici_adi)
            
            self.app.islem_gecmisi.append(UndoIslemi(tip="ekleme", malzeme_id=yeni_id, malzeme_isim=isim, log_id=log_id, yeni_malzeme=y_malz))
            self.app.ileri_gecmisi.clear()
            self.entry_isim.delete(0, 'end'); self.entry_m1.delete(0, 'end'); self.entry_m2.delete(0, 'end'); self.entry_m3.delete(0, 'end'); self.entry_lokasyon.delete(0, 'end'); self.textbox_notlar.delete("1.0", "end")
            
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"'{isim}' eklendi!", renk=renkler["basari"])
            self.app.gui_guncelle()
        except ValueError as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])