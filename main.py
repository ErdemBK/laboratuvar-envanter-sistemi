import customtkinter as ctk
import os, logging
from datetime import datetime
from veritabani import DatabaseManager
from modeller import IslemTipi, stok_metni_olustur
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelOnayKutusu, OzelBilgiKutusu # IMPORTLAR TAM

from sayfa_envanter import EnvanterSayfasi
from sayfa_ekle import EkleSayfasi
from sayfa_gecmis import GecmisSayfasi
from sayfa_yedekleme import YedeklemeSayfasi

class EnvanterUygulamasi(ctk.CTk):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.aktif_dil = "TR"
        self.aktif_tema = "dark"
        self.kullanici_adi = ""
        self.islem_gecmisi = [] 
        self.ileri_gecmisi = [] 
        self.sayfalar = {} 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        ctk.set_appearance_mode(self.aktif_tema)
        self.login_ekrani_goster()

    def on_closing(self):
        try:
            os.makedirs("Yedekler", exist_ok=True)
            self.db.yedek_al(f"Yedekler/oto_yedek_{datetime.now().strftime('%Y_%m_%d')}.db")
        except: pass
        finally: self.db.kapat(); self.destroy()

    def login_ekrani_goster(self):
        for widget in self.winfo_children(): widget.destroy()
        self.title(metinler[self.aktif_dil]["title"])
        self.geometry("400x450"); self.resizable(False, False)
        ctk.CTkLabel(self, text=metinler[self.aktif_dil]["kim_giris"], font=FontManager.get_font(24, "bold")).pack(pady=(20, 10))
        self.k_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=200); self.k_frame.pack(fill="x", padx=20, pady=10)
        self.kullanici_listesini_ciz()
        ctk.CTkLabel(self, text=metinler[self.aktif_dil]["yeni_kullanici"], font=FontManager.get_font(14)).pack(pady=(10, 0))
        y_f = ctk.CTkFrame(self, fg_color="transparent"); y_f.pack(pady=5)
        self.e_yeni = ctk.CTkEntry(y_f, placeholder_text=metinler[self.aktif_dil]["isim_girin"], width=150); self.e_yeni.pack(side="left", padx=5)
        ctk.CTkButton(y_f, text=metinler[self.aktif_dil]["ekle_btn"], width=60, command=self.kullanici_ekle).pack(side="left")

    def kullanici_ekle(self):
        n = self.e_yeni.get().strip()
        if n: self.db.kullanici_ekle(n); self.e_yeni.delete(0, 'end'); self.kullanici_listesini_ciz()

    def kullanici_listesini_ciz(self):
        for w in self.k_frame.winfo_children(): w.destroy()
        ks = self.db.kullanicilari_getir()
        if not ks: ctk.CTkLabel(self.k_frame, text=metinler[self.aktif_dil]["kayitli_yok"]).pack(pady=20)
        else:
            for k in ks:
                r = ctk.CTkFrame(self.k_frame, fg_color=renkler["kart"]); r.pack(fill="x", pady=4)
                ctk.CTkButton(r, text=k, fg_color="transparent", anchor="w", command=lambda x=k: self.kullanici_secildi(x)).pack(side="left", expand=True, fill="x", padx=10, pady=5)
                ctk.CTkButton(r, text="X", width=30, fg_color=renkler["tehlike"], command=lambda x=k: self.kullanici_sil_onay(x)).pack(side="right", padx=5, pady=5)

    def kullanici_sil_onay(self, n):
        OzelOnayKutusu(self, metinler[self.aktif_dil]["sil"], metinler[self.aktif_dil]["emin_misin_kullanici"].format(n), lambda: (self.db.kullanici_sil(n), self.kullanici_listesini_ciz()))

    def kullanici_secildi(self, n):
        self.kullanici_adi = n; [w.destroy() for w in self.winfo_children()]; self.resizable(True, True); self.ana_arayuzu_kur() 

    def ana_arayuzu_kur(self):
        self.title(f"{metinler[self.aktif_dil]['title']} - {self.kullanici_adi}"); self.geometry("1200x700")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
        self.sol_menu = ctk.CTkFrame(self, width=220, fg_color=renkler["menu"]); self.sol_menu.grid(row=0, column=0, sticky="nsew")
        self.sol_menu.grid_rowconfigure(6, weight=1) 
        ctk.CTkLabel(self.sol_menu, text=metinler[self.aktif_dil]["logo"], font=FontManager.get_font(24, "bold"), text_color=renkler["buton_mavi"]).grid(row=0, column=0, padx=20, pady=(30, 40))
        
        def m_btn(r, key, s_adi):
            ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil][key], font=FontManager.get_font(16, "bold"), fg_color="transparent", anchor="w", command=lambda: self.sayfa_goster(s_adi)).grid(row=r, column=0, padx=15, pady=5, sticky="ew")
        
        self.sag_icerik = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent"); self.sag_icerik.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.sag_icerik.grid_rowconfigure(0, weight=1); self.sag_icerik.grid_columnconfigure(0, weight=1)
        
        self.sayfalar = {"EnvanterSayfasi": EnvanterSayfasi(self.sag_icerik, self), "EkleSayfasi": EkleSayfasi(self.sag_icerik, self), "GecmisSayfasi": GecmisSayfasi(self.sag_icerik, self), "YedeklemeSayfasi": YedeklemeSayfasi(self.sag_icerik, self)}
        for s in self.sayfalar.values(): s.grid(row=0, column=0, sticky="nsew")
        
        m_btn(1, "envanter", "EnvanterSayfasi"); m_btn(2, "yeni_ekle", "EkleSayfasi"); m_btn(3, "gecmis", "GecmisSayfasi"); m_btn(4, "yedekleme", "YedeklemeSayfasi")
        nv = ctk.CTkFrame(self.sol_menu, fg_color="transparent"); nv.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.btn_geri = ctk.CTkButton(nv, text="⟲", font=FontManager.get_font(24, "bold"), width=45, height=45, corner_radius=22, command=self.islemi_geri_al, fg_color="transparent", state="disabled"); self.btn_geri.pack(side="left", padx=5)
        self.btn_ileri = ctk.CTkButton(nv, text="⟳", font=FontManager.get_font(24, "bold"), width=45, height=45, corner_radius=22, command=self.islemi_ileri_al, fg_color="transparent", state="disabled"); self.btn_ileri.pack(side="left", padx=5)
        ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil]["tema_degistir"], command=self.tema_degistir, fg_color="transparent").grid(row=8, column=0, padx=20, pady=(10, 5))
        ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil]["dil_sec"], command=self.dil_degistir, fg_color="transparent").grid(row=9, column=0, padx=20, pady=(5, 20))
        self.sayfa_goster("EnvanterSayfasi")

    def gui_guncelle(self):
        self.btn_geri.configure(state="normal" if self.islem_gecmisi else "disabled", fg_color=renkler["buton_mavi"] if self.islem_gecmisi else "transparent")
        self.btn_ileri.configure(state="normal" if self.ileri_gecmisi else "disabled", fg_color="#8B5CF6" if self.ileri_gecmisi else "transparent")
        self.sayfa_goster("EnvanterSayfasi")

    def sayfa_goster(self, s_adi):
        s = self.sayfalar[s_adi]
        if s_adi == "EnvanterSayfasi": s.envanter_kartlarini_ciz()
        elif s_adi == "GecmisSayfasi": s.gecmisi_yenile()
        s.tkraise()

    def islemi_geri_al(self):
        if not self.islem_gecmisi: return
        i = self.islem_gecmisi.pop(); self.db.gecmis_sil(i.log_id)
        if i.tip == "ekleme": self.db.malzeme_sil(i.malzeme_id)
        elif i.tip == "silme": self.db.malzeme_geri_yukle(i.eski_malzeme)
        elif i.tip == "guncelleme": self.db.stok_guncelle(i.eski_malzeme)
        self.ileri_gecmisi.append(i); self.gui_guncelle()

    def islemi_ileri_al(self):
        if not self.ileri_gecmisi: return
        i = self.ileri_gecmisi.pop()
        if i.tip == "ekleme": self.db.malzeme_geri_yukle(i.yeni_malzeme)
        elif i.tip == "silme": self.db.malzeme_sil(i.malzeme_id)
        elif i.tip == "guncelleme": self.db.stok_guncelle(i.yeni_malzeme)
        self.islem_gecmisi.append(i); self.gui_guncelle()

    def tema_degistir(self):
        self.aktif_tema = "light" if self.aktif_tema == "dark" else "dark"; ctk.set_appearance_mode(self.aktif_tema)

    def dil_degistir(self):
        self.aktif_dil = "EN" if self.aktif_dil == "TR" else "TR"
        if hasattr(self, "sol_menu"): self.sol_menu.destroy()
        if hasattr(self, "sag_icerik"): self.sag_icerik.destroy()
        self.sayfalar.clear(); self.ana_arayuzu_kur()

if __name__ == "__main__":
    app_db = DatabaseManager(); uygulama = EnvanterUygulamasi(app_db); uygulama.mainloop()