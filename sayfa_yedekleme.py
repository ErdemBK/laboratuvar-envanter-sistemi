import customtkinter as ctk
from tkinter import filedialog
import csv, threading, logging, os
from datetime import datetime
from modeller import Malzeme
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelOnayKutusu, OzelBilgiKutusu

class YedeklemeSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ctk.CTkLabel(self, text=metinler[self.app.aktif_dil]["yedekleme"], font=FontManager.get_font(26, "bold"), text_color=renkler["yazi_ana"]).pack(pady=(10, 20), anchor="w", padx=20)
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20)
        
        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["db_islemleri"], font=FontManager.get_font(18, "bold"), text_color=renkler["yazi_ana"]).pack(anchor="w", pady=(10,5))
        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["db_aciklama"], text_color=renkler["yazi_ikincil"], font=FontManager.get_font(14)).pack(anchor="w", pady=(0,10))
        
        b1 = ctk.CTkFrame(f, fg_color="transparent")
        b1.pack(anchor="w", pady=10)
        ctk.CTkButton(b1, text=metinler[self.app.aktif_dil]["db_yedekle_btn"], font=FontManager.get_font(14, "bold"), fg_color=renkler["buton_mavi"], command=self.db_yedekle).pack(side="left", padx=(0, 10))
        ctk.CTkButton(b1, text=metinler[self.app.aktif_dil]["db_kurtar_btn"], font=FontManager.get_font(14, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", command=self.db_kurtar).pack(side="left")

        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["csv_islemleri"], font=FontManager.get_font(18, "bold"), text_color=renkler["yazi_ana"]).pack(anchor="w", pady=(40,5))
        ctk.CTkLabel(f, text=metinler[self.app.aktif_dil]["csv_aciklama"], text_color=renkler["yazi_ikincil"], font=FontManager.get_font(14)).pack(anchor="w", pady=(0,10))
        ctk.CTkButton(f, text=metinler[self.app.aktif_dil]["csv_yukle_btn"], font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], hover_color="#059669", command=self.csv_ice_aktar).pack(anchor="w", pady=10)

    def db_yedekle(self):
        hedef = filedialog.asksaveasfilename(defaultextension=".db", initialfile="lab_envanter_yedek.db", title="Kaydet")
        if hedef:
            try:
                self.db.yedek_al(hedef)
                OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"Yedeklendi:\n{hedef}", renk=renkler["basari"])
            except Exception as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])

    def db_kurtar(self):
        kaynak = filedialog.askopenfilename(filetypes=[("Veritabanı", "*.db")], title="Yedek Seç")
        if kaynak:
            def kurtar():
                try:
                    os.makedirs("Yedekler", exist_ok=True)
                    self.db.yedek_al(f"Yedekler/acil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                    self.db.yedek_kurtar(kaynak)
                    OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Kurtarıldı. Uygulama kapanacak.", renk=renkler["basari"])
                    self.after(3000, self.app.destroy)
                except Exception as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])
            OzelOnayKutusu(self.winfo_toplevel(), "⚠️ KRİTİK UYARI", "Mevcut veriler SİLİNECEK! Emin misiniz?", kurtar)

    def csv_ice_aktar(self):
        kaynak = filedialog.askopenfilename(filetypes=[("Excel CSV", "*.csv")], title="CSV Seç")
        if not kaynak: return
        def baslat():
            threading.Thread(target=self._csv_isleyici, args=(kaynak,), daemon=True).start()
            OzelBilgiKutusu(self.winfo_toplevel(), "İşlem Başladı", "Aktarılıyor...", renk=renkler["uyari"])
        OzelOnayKutusu(self.winfo_toplevel(), "⚠️ SIFIRLAMA", "Excel'i içeri aktarmak tüm envanteri SİLER. Onay?", baslat)

    def _csv_isleyici(self, kaynak: str):
        okunan, hatali = [], []
        try:
            with open(kaynak, 'r', encoding='utf-8-sig') as dosya:
                okuyucu = csv.reader(dosya, delimiter=';')
                # DÜZELTME: StopIteration hatasını defansif olarak yakala
                next(okuyucu, None) 
                
                for i, satir in enumerate(okuyucu, start=2):
                    if len(satir) < 10: 
                        hatali.append(str(i)); continue
                    try:
                        m = Malzeme(
                            isim=satir[1], ambalaj_tipi="", 
                            miktar=float(satir[2].strip() or 0.0), birim=satir[3],
                            ikinci_miktar=float(satir[4].strip() or 0.0), ikinci_birim=satir[5], 
                            ucuncu_miktar=float(satir[6].strip() or 0.0), ucuncu_birim=satir[7],
                            donusum_orani=0.0, lokasyon=satir[8], notlar=satir[9] if len(satir)>9 else ""
                        )
                        okunan.append(m)
                    except Exception as e: hatali.append(str(i)); logging.error(f"Satır {i}: {e}")
            
            if not okunan:
                raise ValueError("Seçilen CSV dosyası boş veya geçerli bir malzeme bulunamadı. Veritabanı korunuyor.")
                
            self.db.csv_ile_veri_aktar(okunan)
            def ui_basarili():
                if hatali: OzelBilgiKutusu(self.winfo_toplevel(), "Kısmi Başarı", f"{len(okunan)} eklendi. Hatalı satırlar atlandı: {', '.join(hatali)}", renk=renkler["uyari"])
                else: OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Excel aktarıldı!", renk=renkler["basari"])
                self.app.islem_gecmisi.clear(); self.app.ileri_gecmisi.clear()
                self.app.gui_guncelle()
            self.after(0, ui_basarili)
        except Exception as e:
            logging.error(f"CSV Hatası: {e}")
            self.after(0, lambda: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", f"İşlem başarısız.\n{e}", renk=renkler["tehlike"]))