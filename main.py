import customtkinter as ctk
import os
import logging
import traceback
from datetime import datetime

from veritabani import DatabaseManager
from modeller import IslemTipi, stok_metni_olustur, UndoIslemi
from ayarlar import metinler, renkler, font_tipi
from ui_bilesenleri import FontManager, OzelOnayKutusu, OzelBilgiKutusu

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
            # 1. Klasör yoksa oluştur ve bugünün yedeğini al
            os.makedirs("Yedekler", exist_ok=True)
            bugun_tarih = datetime.now().strftime('%Y_%m_%d')
            yeni_yedek_yolu = f"Yedekler/oto_yedek_{bugun_tarih}.db"
            self.db.yedek_al(yeni_yedek_yolu)
            
            # 2. ESKİ YEDEKLERİ OTOMATİK SİLME MANTIĞI (Sadece son 5 yedeği tutar)
            yedekler = [f for f in os.listdir("Yedekler") if f.startswith("oto_yedek_") and f.endswith(".db")]
            
            # İsimleri tarihe göre ters sırala (En yeniler en başta olsun)
            yedekler.sort(reverse=True)
            
            # Eğer 5'ten fazla dosya varsa, 5. dosyadan sonrakilerin hepsini sil
            if len(yedekler) > 5:
                silinecekler = yedekler[5:]
                for eski_dosya in silinecekler:
                    try:
                        os.remove(os.path.join("Yedekler", eski_dosya))
                    except Exception as e:
                        print(f"Eski yedek silinemedi: {e}")
                        
        except Exception as e: 
            logging.error(f"Yedekleme ve temizlik hatası: {e}")
            
        finally: 
            self.db.kapat()
            self.destroy()

    def login_ekrani_goster(self):
        self.withdraw()
        
        self.login = ctk.CTkToplevel(self)
        self.login.title(metinler[self.aktif_dil]["title"])
        self.login.geometry("400x480")
        self.login.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.login.attributes("-topmost", True)
        self.login.configure(fg_color=renkler["arkaplan"])

        ctk.CTkLabel(
            self.login, text=metinler[self.aktif_dil]["kim_giris"], 
            font=FontManager.get_font(24, "bold"), text_color=renkler["yazi_ana"]
        ).pack(pady=(20, 10))
        
        self.kullanici_frame = ctk.CTkScrollableFrame(self.login, fg_color="transparent", height=200)
        self.kullanici_frame.pack(fill="x", padx=20, pady=10)
        
        self.kullanici_listesini_ciz()

        ctk.CTkLabel(
            self.login, text=metinler[self.aktif_dil]["yeni_kullanici"], 
            font=FontManager.get_font(14), text_color=renkler["yazi_ikincil"]
        ).pack(pady=(10, 0))
        
        yeni_f = ctk.CTkFrame(self.login, fg_color="transparent")
        yeni_f.pack(pady=5)
        
        self.yeni_isim_entry = ctk.CTkEntry(
            yeni_f, placeholder_text=metinler[self.aktif_dil]["isim_girin"], 
            font=FontManager.get_font(14), width=160
        )
        self.yeni_isim_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            yeni_f, text=metinler[self.aktif_dil]["ekle_btn"], width=60, 
            font=FontManager.get_font(14, "bold"), fg_color=renkler["buton_mavi"], 
            command=self.kullanici_ekle
        ).pack(side="left")

    def kullanici_ekle(self):
        isim = self.yeni_isim_entry.get().strip()
        if isim:
            self.db.kullanici_ekle(isim)
            self.yeni_isim_entry.delete(0, 'end')
            self.kullanici_listesini_ciz()

    def kullanici_listesini_ciz(self):
        for widget in self.kullanici_frame.winfo_children(): 
            widget.destroy()
            
        kullanicilar = self.db.kullanicilari_getir()
        
        if not kullanicilar: 
            ctk.CTkLabel(
                self.kullanici_frame, text=metinler[self.aktif_dil]["kayitli_yok"], 
                text_color=renkler["yazi_ikincil"]
            ).pack(pady=20)
        else:
            for k in kullanicilar:
                row = ctk.CTkFrame(self.kullanici_frame, fg_color=renkler["kart"])
                row.pack(fill="x", pady=4)
                
                ctk.CTkButton(
                    row, text=k, fg_color="transparent", text_color=renkler["yazi_ana"], 
                    anchor="w", command=lambda isim=k: self.kullanici_secildi(isim)
                ).pack(side="left", expand=True, fill="x", padx=10, pady=5)
                
                ctk.CTkButton(
                    row, text="X", width=30, fg_color=renkler["tehlike"], 
                    command=lambda isim=k: self.kullanici_sil_onay(isim)
                ).pack(side="right", padx=5, pady=5)

    def kullanici_sil_onay(self, isim):
        OzelOnayKutusu(
            self.login, metinler[self.aktif_dil]["sil"], 
            metinler[self.aktif_dil]["emin_misin_kullanici"].format(isim), 
            lambda: (self.db.kullanici_sil(isim), self.kullanici_listesini_ciz())
        )

    def kullanici_secildi(self, isim):
        self.kullanici_adi = isim
        self.login.destroy()
        self.deiconify() 
        self.ana_arayuzu_kur() 

    def ana_arayuzu_kur(self):
        for w in self.winfo_children(): 
            w.destroy()

        self.title(f"{metinler[self.aktif_dil]['title']} - {self.kullanici_adi}")
        self.geometry("1200x750")
        self.configure(fg_color=renkler["arkaplan"])
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.sol_menu = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=renkler["menu"])
        self.sol_menu.grid(row=0, column=0, sticky="nsew")
        self.sol_menu.grid_rowconfigure(5, weight=1) 

        ctk.CTkLabel(
            self.sol_menu, text=metinler[self.aktif_dil]["logo"], 
            font=FontManager.get_font(24, "bold"), text_color=renkler["buton_mavi"]
        ).grid(row=0, column=0, padx=20, pady=(30, 40))
        
        def menu_btn(r, key, sayfa_adi):
            ctk.CTkButton(
                self.sol_menu, text=metinler[self.aktif_dil][key], 
                font=FontManager.get_font(16, "bold"), fg_color="transparent", 
                text_color=renkler["yazi_ana"], hover_color=renkler["arkaplan"], 
                height=45, anchor="w", command=lambda: self.sayfa_goster(sayfa_adi)
            ).grid(row=r, column=0, padx=15, pady=5, sticky="ew")
        
        menu_btn(1, "envanter", "EnvanterSayfasi")
        menu_btn(2, "yeni_ekle", "EkleSayfasi")
        menu_btn(3, "gecmis", "GecmisSayfasi")
        menu_btn(4, "yedekleme", "YedeklemeSayfasi")
        
        self.sag_icerik = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.sag_icerik.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.sag_icerik.grid_rowconfigure(0, weight=1)
        self.sag_icerik.grid_columnconfigure(0, weight=1)
        
        self.sayfalar = {}
        
        try:
            self.sayfalar["EnvanterSayfasi"] = EnvanterSayfasi(self.sag_icerik, self)
        except Exception as e:
            print("ENVANTER SAYFASI HATASI:", e)
            traceback.print_exc()
            
        try:
            self.sayfalar["EkleSayfasi"] = EkleSayfasi(self.sag_icerik, self)
        except Exception as e:
            print("EKLE SAYFASI HATASI:", e)
            
        try:
            self.sayfalar["GecmisSayfasi"] = GecmisSayfasi(self.sag_icerik, self)
        except Exception as e:
            print("GECMIS SAYFASI HATASI:", e)
            
        try:
            self.sayfalar["YedeklemeSayfasi"] = YedeklemeSayfasi(self.sag_icerik, self)
        except Exception as e:
            print("YEDEKLEME SAYFASI HATASI:", e)

        for s in self.sayfalar.values(): 
            s.grid(row=0, column=0, sticky="nsew")
        
        nav_f = ctk.CTkFrame(self.sol_menu, fg_color="transparent")
        nav_f.grid(row=6, column=0, padx=20, pady=10)
        
        self.btn_geri = ctk.CTkButton(
            nav_f, text="⟲", font=FontManager.get_font(24, "bold"), width=45, height=45, 
            corner_radius=22, command=self.islemi_geri_al, fg_color="transparent", state="disabled"
        )
        self.btn_geri.pack(side="left", padx=5)
        
        self.btn_ileri = ctk.CTkButton(
            nav_f, text="⟳", font=FontManager.get_font(24, "bold"), width=45, height=45, 
            corner_radius=22, command=self.islemi_ileri_al, fg_color="transparent", state="disabled"
        )
        self.btn_ileri.pack(side="left", padx=5)

        ctk.CTkButton(
            self.sol_menu, text=metinler[self.aktif_dil]["kullanici_degistir"], 
            font=FontManager.get_font(13), command=self.kullanici_degistir, 
            fg_color="transparent", text_color=renkler["uyari"]
        ).grid(row=7, column=0, padx=20, pady=5)
        
        ctk.CTkButton(
            self.sol_menu, text=metinler[self.aktif_dil]["tema_degistir"], 
            font=FontManager.get_font(13), command=self.tema_degistir, 
            fg_color="transparent", text_color=renkler["yazi_ana"]
        ).grid(row=8, column=0, padx=20, pady=5)
        
        ctk.CTkButton(
            self.sol_menu, text=metinler[self.aktif_dil]["dil_sec"], 
            font=FontManager.get_font(13), command=self.dil_degistir, 
            fg_color="transparent", text_color=renkler["yazi_ana"]
        ).grid(row=9, column=0, padx=20, pady=(5, 20))

        if "EnvanterSayfasi" in self.sayfalar:
            self.sayfa_goster("EnvanterSayfasi")

    def kullanici_degistir(self):
        self.islem_gecmisi.clear()
        self.ileri_gecmisi.clear()
        self.login_ekrani_goster()

    def gui_guncelle(self):
        self.btn_geri.configure(
            state="normal" if self.islem_gecmisi else "disabled", 
            fg_color=renkler["buton_mavi"] if self.islem_gecmisi else "transparent",
            text_color="#FFFFFF" if self.islem_gecmisi else renkler["yazi_ikincil"]
        )
        self.btn_ileri.configure(
            state="normal" if self.ileri_gecmisi else "disabled", 
            fg_color="#8B5CF6" if self.ileri_gecmisi else "transparent",
            text_color="#FFFFFF" if self.ileri_gecmisi else renkler["yazi_ikincil"]
        )
        if "EnvanterSayfasi" in self.sayfalar:
            self.sayfa_goster("EnvanterSayfasi")

    def sayfa_goster(self, sayfa_adi):
        if sayfa_adi not in self.sayfalar:
            print(f"HATA: {sayfa_adi} Yuklenemedigi Icin Acilamiyor!")
            return
            
        sayfa = self.sayfalar[sayfa_adi]
        if sayfa_adi == "EnvanterSayfasi": 
            sayfa.envanter_kartlarini_ciz()
        elif sayfa_adi == "GecmisSayfasi": 
            sayfa.gecmisi_yenile()
        sayfa.tkraise()

    def islemi_geri_al(self):
        if not self.islem_gecmisi: return
        islem = self.islem_gecmisi.pop() 
        self.db.gecmis_sil(islem.log_id)
        
        if islem.tip == "ekleme": 
            self.db.malzeme_sil(islem.malzeme_id)
        elif islem.tip == "silme": 
            self.db.malzeme_geri_yukle(islem.eski_malzeme)
        elif islem.tip == "guncelleme": 
            self.db.stok_guncelle(islem.eski_malzeme)
            
        self.ileri_gecmisi.append(islem) 
        self.gui_guncelle()

    def islemi_ileri_al(self):
        if not self.ileri_gecmisi: return
        islem = self.ileri_gecmisi.pop()
        dil = self.aktif_dil
        
        if islem.tip == "ekleme":
            self.db.malzeme_geri_yukle(islem.yeni_malzeme)
            m = islem.yeni_malzeme
            sm = stok_metni_olustur(m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.dorduncu_miktar, m.dorduncu_birim, m.besinci_miktar, m.besinci_birim, dil)
            tx = f"{metinler[dil]['log_eklendi']} ({metinler[dil]['log_miktar']}: {sm})"
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, tx, self.kullanici_adi)
        elif islem.tip == "silme":
            self.db.malzeme_sil(islem.malzeme_id)
            m = islem.eski_malzeme
            sm = stok_metni_olustur(m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.dorduncu_miktar, m.dorduncu_birim, m.besinci_miktar, m.besinci_birim, dil)
            tx = f"{metinler[dil]['log_silindi']} ({metinler[dil]['log_stok']}: {sm})"
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, tx, self.kullanici_adi)
        elif islem.tip == "guncelleme":
            self.db.stok_guncelle(islem.yeni_malzeme)
            islem.log_id = self.db.gecmis_ekle(islem.malzeme_id, islem.malzeme_isim, metinler[dil]['log_guncellendi'], self.kullanici_adi)
            
        self.islem_gecmisi.append(islem)
        self.gui_guncelle()

    def tema_degistir(self):
        self.aktif_tema = "light" if self.aktif_tema == "dark" else "dark"
        ctk.set_appearance_mode(self.aktif_tema)

    def dil_degistir(self):
        self.aktif_dil = "EN" if self.aktif_dil == "TR" else "TR"
        self.ana_arayuzu_kur()

if __name__ == "__main__":
    app_db = DatabaseManager()
    uygulama = EnvanterUygulamasi(app_db)
    uygulama.mainloop()