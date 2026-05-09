import customtkinter as ctk
from tkinter import filedialog
import os
import csv
from datetime import datetime
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelOnayKutusu, OzelBilgiKutusu
from modeller import Malzeme, miktar_dogrula

class YedeklemeSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ctk.CTkLabel(
            self, text=metinler[self.app.aktif_dil]["yedekleme"], 
            font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]
        ).pack(pady=(10, 20), anchor="w", padx=20)
        
        f1 = ctk.CTkFrame(self, fg_color=renkler["kart"], corner_radius=10)
        f1.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            f1, text=metinler[self.app.aktif_dil]["db_islemleri"], 
            font=FontManager.get_font(18, "bold"), text_color=renkler["yazi_ana"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            f1, text=metinler[self.app.aktif_dil]["db_aciklama"], 
            font=FontManager.get_font(14), text_color=renkler["yazi_ikincil"]
        ).pack(anchor="w", padx=20, pady=5)
        
        bf = ctk.CTkFrame(f1, fg_color="transparent")
        bf.pack(anchor="w", padx=20, pady=(10, 20))
        
        ctk.CTkButton(
            bf, text=metinler[self.app.aktif_dil]["db_yedekle_btn"], 
            font=FontManager.get_font(14, "bold"), fg_color=renkler["buton_mavi"], command=self.yedek_al
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            bf, text=metinler[self.app.aktif_dil]["db_kurtar_btn"], 
            font=FontManager.get_font(14, "bold"), fg_color="#8B5CF6", command=self.kurtar_onay
        ).pack(side="left")

        f2 = ctk.CTkFrame(self, fg_color=renkler["kart"], corner_radius=10)
        f2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            f2, text=metinler[self.app.aktif_dil]["csv_islemleri"], 
            font=FontManager.get_font(18, "bold"), text_color=renkler["yazi_ana"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            f2, text=metinler[self.app.aktif_dil]["csv_aciklama"], 
            font=FontManager.get_font(14), text_color=renkler["yazi_ikincil"]
        ).pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkButton(
            f2, text=metinler[self.app.aktif_dil]["csv_yukle_btn"], 
            font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], command=self.csv_yukle_onay
        ).pack(anchor="w", padx=20, pady=(10, 20))

    def yedek_al(self):
        dosya = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")], initialfile=f"yedek_{datetime.now().strftime('%Y_%m_%d')}.db")
        if dosya:
            try:
                self.db.yedek_al(dosya)
                OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Yedekleme başarıyla tamamlandı.", renk=renkler["basari"])
            except Exception as e:
                OzelBilgiKutusu(self.winfo_toplevel(), "Hata", f"Yedek alınamadı:\n{e}", renk=renkler["tehlike"])

    def kurtar_onay(self):
        OzelOnayKutusu(
            self.winfo_toplevel(), metinler[self.app.aktif_dil]["onay_baslik"], 
            metinler[self.app.aktif_dil]["emin_misin_csv"], self.kurtar
        )
        
    def kurtar(self):
        dosya = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if dosya:
            try:
                self.db.geri_yukle(dosya)
                self.app.islem_gecmisi.clear()
                self.app.ileri_gecmisi.clear()
                self.app.gui_guncelle()
                OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Veritabanı geri yüklendi.", renk=renkler["basari"])
            except Exception as e:
                OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])

    def csv_yukle_onay(self):
        OzelOnayKutusu(
            self.winfo_toplevel(), metinler[self.app.aktif_dil]["onay_baslik"], 
            metinler[self.app.aktif_dil]["emin_misin_csv"], self.csv_yukle
        )
        
    def csv_yukle(self):
        dosya = filedialog.askopenfilename(filetypes=[("Excel CSV", "*.csv")])
        if not dosya: 
            return
        
        try:
            self.db.imlec.execute("DELETE FROM malzemeler")
            self.db.imlec.execute("DELETE FROM islemler")
            self.db.baglanti.commit()
            
            with open(dosya, 'r', encoding='utf-8-sig') as f:
                okuyucu = csv.reader(f, delimiter=';')
                basliklar = next(okuyucu, None) 
                
                # AKILLI TARAMA: Eski formattaki Excel'leri (10+ Sütunlu) algılamak için
                eski_format_mi = False
                if basliklar and len(basliklar) > 5:
                    eski_format_mi = True
                
                for satir in okuyucu:
                    # ESKİ FORMATI (10 SÜTUN) İÇERİ AKTARMA MANTIĞI
                    if eski_format_mi:
                        if len(satir) < 9: 
                            continue
                        
                        isim = satir[1]
                        m1 = miktar_dogrula(satir[2])
                        b1 = satir[3]
                        m2 = miktar_dogrula(satir[4])
                        b2 = satir[5]
                        m3 = miktar_dogrula(satir[6])
                        b3 = satir[7]
                        lokasyon = satir[8]
                        notlar = satir[9] if len(satir) > 9 else ""
                        
                        yeni_m = Malzeme(
                            isim=isim, 
                            miktar=m1, birim=b1, 
                            ikinci_miktar=m2, ikinci_birim=b2, 
                            ucuncu_miktar=m3, ucuncu_birim=b3, 
                            lokasyon=lokasyon, notlar=notlar
                        )
                        self.db.malzeme_ekle(yeni_m)
                        
                    # YENİ FORMATI (4 SÜTUN) İÇERİ AKTARMA MANTIĞI
                    else:
                        if len(satir) < 4: 
                            continue 
                        
                        isim = satir[0]
                        stok_detayi = satir[1]
                        lokasyon = satir[2]
                        notlar = satir[3]
                        
                        m_vals = [0.0] * 5
                        b_vals = [""] * 5
                        
                        parcalar = stok_detayi.split("•")
                        for i, p in enumerate(parcalar):
                            if i >= 5: break
                            p = p.strip()
                            if not p or p == "0": 
                                continue
                                
                            parts = p.split(" ", 1)
                            m_vals[i] = float(parts[0]) if len(parts) > 0 else 0.0
                            b_vals[i] = parts[1].strip() if len(parts) > 1 else ""
                            
                        yeni_m = Malzeme(
                            isim=isim, 
                            miktar=m_vals[0], birim=b_vals[0], 
                            ikinci_miktar=m_vals[1], ikinci_birim=b_vals[1], 
                            ucuncu_miktar=m_vals[2], ucuncu_birim=b_vals[2], 
                            dorduncu_miktar=m_vals[3], dorduncu_birim=b_vals[3],
                            besinci_miktar=m_vals[4], besinci_birim=b_vals[4],
                            lokasyon=lokasyon, notlar=notlar
                        )
                        self.db.malzeme_ekle(yeni_m)
                        
            self.app.islem_gecmisi.clear()
            self.app.ileri_gecmisi.clear()
            self.app.gui_guncelle()
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Excel verileri başarıyla içeri aktarıldı.", renk=renkler["basari"])
            
        except Exception as e:
            OzelBilgiKutusu(self.winfo_toplevel(), "Hata", f"Aktarım başarısız:\n{e}", renk=renkler["tehlike"])