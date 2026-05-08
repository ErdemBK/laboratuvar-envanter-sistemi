import customtkinter as ctk
import os, logging
from datetime import datetime

from veritabani import DatabaseManager
from modeller import IslemTipi, stok_metni_olustur
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelOnayKutusu

from sayfa_envanter import EnvanterSayfasi
from sayfa_ekle import EkleSayfasi
from sayfa_gecmis import GecmisSayfasi
from sayfa_yedekleme import YedeklemeSayfasi

class EnvanterUygulamasi(ctk.CTk):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.withdraw()
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
        except Exception as e: logging.error(f"Yedek hatası: {e}")
        finally: 
            self.db.kapat()
            self.destroy()

    def login_ekrani_goster(self):
        self.login = ctk.CTkToplevel(self)
        self.login.title(metinler[self.aktif_dil]["title"])
        self.login.geometry("400x450")
        self.login.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.login.transient(self)
        self.login.grab_set()
        self.login.attributes("-topmost", True)
        self.login.configure(fg_color=renkler["arkaplan"])

        ctk.CTkLabel(self.login, text=metinler[self.aktif_dil]["kim_giris"], font=FontManager.get_font(24, "bold"), text_color=renkler["yazi_ana"]).pack(pady=(20, 10))
        self.kullanici_frame = ctk.CTkScrollableFrame(self.login, fg_color="transparent", height=200)
        self.kullanici_frame.pack(fill="x", padx=20, pady=10)
        self.kullanici_listesini_ciz()

        ctk.CTkLabel(self.login, text=metinler[self.aktif_dil]["yeni_kullanici"], font=FontManager.get_font(14), text_color=renkler["yazi_ikincil"]).pack(pady=(10, 0))
        yeni_frame = ctk.CTkFrame(self.login, fg_color="transparent")
        yeni_frame.pack(pady=5)
        self.yeni_isim_entry = ctk.CTkEntry(yeni_frame, placeholder_text=metinler[self.aktif_dil]["isim_girin"], font=FontManager.get_font(14), width=150)
        self.yeni_isim_entry.pack(side="left", padx=5)
        ctk.CTkButton(yeni_frame, text=metinler[self.aktif_dil]["ekle_btn"], width=60, font=FontManager.get_font(14, "bold"), fg_color=renkler["buton_mavi"], command=self.kullanici_ekle).pack(side="left")

    def kullanici_ekle(self):
        isim = self.yeni_isim_entry.get().strip()
        if isim:
            self.db.kullanici_ekle(isim)
            self.yeni_isim_entry.delete(0, 'end')
            self.kullanici_listesini_ciz()

    def kullanici_listesini_ciz(self):
        for widget in self.kullanici_frame.winfo_children(): widget.destroy()
        kullanicilar = self.db.kullanicilari_getir()
        if not kullanicilar: ctk.CTkLabel(self.kullanici_frame, text=metinler[self.aktif_dil]["kayitli_yok"], text_color=renkler["yazi_ikincil"]).pack(pady=20)
        else:
            for k in kullanicilar:
                row = ctk.CTkFrame(self.kullanici_frame, fg_color=renkler["kart"])
                row.pack(fill="x", pady=4)
                ctk.CTkButton(row, text=k, fg_color="transparent", text_color=renkler["yazi_ana"], anchor="w", command=lambda isim=k: self.kullanici_secildi(isim)).pack(side="left", expand=True, fill="x", padx=10, pady=5)
                # DÜZELTME: Doğrudan silme yerine onay fonksiyonuna bağlandı
                ctk.CTkButton(row, text="X", width=30, fg_color=renkler["tehlike"], command=lambda isim=k: self.kullanici_sil_onay(isim)).pack(side="right", padx=5, pady=5)

    def kullanici_sil_onay(self, isim):
        mesaj = metinler[self.aktif_dil]["emin_misin_kullanici"].format(isim)
        OzelOnayKutusu(self.login, baslik=metinler[self.aktif_dil]["sil"], mesaj=mesaj, evet_komut=lambda: self.kullanici_sil_islemi(isim), evet_metni=metinler[self.aktif_dil]["evet"], hayir_metni=metinler[self.aktif_dil]["hayir"])

    def kullanici_sil_islemi(self, isim):
        self.db.kullanici_sil(isim)
        self.kullanici_listesini_ciz()

    def kullanici_secildi(self, isim):
        self.kullanici_adi = isim
        self.login.grab_release()
        self.login.destroy()
        self.deiconify() 
        self.ana_arayuzu_kur() 

    def ana_arayuzu_kur(self):
        self.title(f"{metinler[self.aktif_dil]['title']} - {self.kullanici_adi}")
        self.geometry("1200x700")
        self.configure(fg_color=renkler["arkaplan"])
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
        
        self.sol_menu = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=renkler["menu"])
        self.sol_menu.grid(row=0, column=0, sticky="nsew")
        self.sol_menu.grid_rowconfigure(6, weight=1) 

        ctk.CTkLabel(self.sol_menu, text=metinler[self.aktif_dil]["logo"], font=FontManager.get_font(24, "bold"), text_color=renkler["buton_mavi"]).grid(row=0, column=0, padx=20, pady=(30, 40))
        
        def menu_btn(r, key, sayfa_adi):
            ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil][key], font=FontManager.get_font(16, "bold"), fg_color="transparent", text_color=renkler["yazi_ana"], hover_color=renkler["arkaplan"], height=40, anchor="w", command=lambda: self.sayfa_goster(sayfa_adi)).grid(row=r, column=0, padx=15, pady=5, sticky="ew")
        
        self.sag_icerik = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.sag_icerik.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.sag_icerik.grid_rowconfigure(0, weight=1); self.sag_icerik.grid_columnconfigure(0, weight=1)
        
        self.sayfalar["EnvanterSayfasi"] = EnvanterSayfasi(self.sag_icerik, self)
        self.sayfalar["EkleSayfasi"] = EkleSayfasi(self.sag_icerik, self)
        self.sayfalar["GecmisSayfasi"] = GecmisSayfasi(self.sag_icerik, self)
        self.sayfalar["YedeklemeSayfasi"] = YedeklemeSayfasi(self.sag_icerik, self)

        for s in self.sayfalar.values(): s.grid(row=0, column=0, sticky="nsew")

        menu_btn(1, "envanter", "EnvanterSayfasi")
        menu_btn(2, "yeni_ekle", "EkleSayfasi")
        menu_btn(3, "gecmis", "GecmisSayfasi")
        menu_btn(4, "yedekleme", "YedeklemeSayfasi")
        
        nav_frame = ctk.CTkFrame(self.sol_menu, fg_color="transparent")
        nav_frame.grid(row=7, column=0, padx=20, pady=(10, 10))
        
        self.btn_geri = ctk.CTkButton(nav_frame, text="⟲", font=FontManager.get_font(24, "bold"), width=45, height=45, corner_radius=22, command=self.islemi_geri_al, fg_color="transparent", text_color=renkler["yazi_ikincil"], state="disabled")
        self.btn_geri.pack(side="left", padx=5)
        self.btn_ileri = ctk.CTkButton(nav_frame, text="⟳", font=FontManager.get_font(24, "bold"), width=45, height=45, corner_radius=22, command=self.islemi_ileri_al, fg_color="transparent", text_color=renkler["yazi_ikincil"], state="disabled")
        self.btn_ileri.pack(side="left", padx=5)

        self.btn_tema = ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil]["tema_degistir"], font=FontManager.get_font(13), command=self.tema_degistir, fg_color="transparent", text_color=renkler["yazi_ana"])
        self.btn_tema.grid(row=8, column=0, padx=20, pady=(10, 5))
        self.btn_dil = ctk.CTkButton(self.sol_menu, text=metinler[self.aktif_dil]["dil_sec"], font=FontManager.get_font(13), command=self.dil_degistir, fg_color="transparent", text_color=renkler["yazi_ana"])
        self.btn_dil.grid(row=9, column=0, padx=20, pady=(5, 20))

        self.sayfa_goster("EnvanterSayfasi")

    def gui_guncelle(self):
        self.navigasyon_butonlarini_guncelle()
        self.sayfa_goster("EnvanterSayfasi")

    def sayfa_goster(self, sayfa_adi):
        sayfa = self.sayfalar[sayfa_adi]
        if sayfa_adi == "EnvanterSayfasi": sayfa.envanter_kartlarini_ciz()
        elif sayfa_adi == "GecmisSayfasi": sayfa.gecmisi_yenile()
        sayfa.tkraise()

    def navigasyon_butonlarini_guncelle(self):
        self.btn_geri.configure(state="normal" if self.islem_gecmisi else "disabled", fg_color=renkler["buton_mavi"] if self.islem_gecmisi else "transparent", text_color="#FFFFFF" if self.islem_gecmisi else renkler["yazi_ikincil"])
        self.btn_ileri.configure(state="normal" if self.ileri_gecmisi else "disabled", fg_color="#8B5CF6" if self.ileri_gecmisi else "transparent", text_color="#FFFFFF" if self.ileri_gecmisi else renkler["yazi_ikincil"])

    def islemi_geri_al(self):
        if not self.islem_gecmisi: return
        islem = self.islem_gecmisi.pop() 
        self.db.gecmis_sil(islem.log_id)
        if islem.tip == "ekleme": self.db.malzeme_sil(islem.malzeme_id)
        elif islem.tip == "silme": self.db.malzeme_geri_yukle(islem.eski_malzeme)
        elif islem.tip == "guncelleme": self.db.stok_guncelle(islem.eski_malzeme)
        self.ileri_gecmisi.append(islem) 
        self.gui_guncelle()

    def islemi_ileri_al(self):
        if not self.ileri_gecmisi: return
        islem = self.ileri_gecmisi.pop()
        if islem.tip == "ekleme":
            self.db.malzeme_geri_yukle(islem.yeni_malzeme)
            sm = stok_metni_olustur(islem.yeni_malzeme.miktar, islem.yeni_malzeme.birim, islem.yeni_malzeme.ikinci_miktar, islem.yeni_malzeme.ikinci_birim, islem.yeni_malzeme.ucuncu_miktar, islem.yeni_malzeme.ucuncu_birim)
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, f"{IslemTipi.EKLEME.value} (Miktar: {sm})", self.kullanici_adi)
        elif islem.tip == "silme":
            self.db.malzeme_sil(islem.malzeme_id)
            sm = stok_metni_olustur(islem.eski_malzeme.miktar, islem.eski_malzeme.birim, islem.eski_malzeme.ikinci_miktar, islem.eski_malzeme.ikinci_birim, islem.eski_malzeme.ucuncu_miktar, islem.eski_malzeme.ucuncu_birim)
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, f"{IslemTipi.SILME.value} (Son Stok: {sm})", self.kullanici_adi)
        elif islem.tip == "guncelleme":
            self.db.stok_guncelle(islem.yeni_malzeme)
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, IslemTipi.GUNCELLEME.value, self.kullanici_adi)
        self.islem_gecmisi.append(islem)
        self.gui_guncelle()

    def tema_degistir(self):
        self.aktif_tema = "light" if self.aktif_tema == "dark" else "dark"
        ctk.set_appearance_mode(self.aktif_tema)

    def dil_degistir(self):
        self.aktif_dil = "EN" if self.aktif_dil == "TR" else "TR"
        if hasattr(self, "sol_menu"): self.sol_menu.destroy()
        if hasattr(self, "sag_icerik"): self.sag_icerik.destroy()
        self.sayfalar.clear()
        self.ana_arayuzu_kur()

if __name__ == "__main__":
    app_db = DatabaseManager()
    uygulama = EnvanterUygulamasi(app_db)
    uygulama.mainloop()