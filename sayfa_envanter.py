# dosya: sayfa_envanter.py
# ---------------------------------------------------------
import customtkinter as ctk
from tkinter import filedialog
import csv
from modeller import Malzeme, IslemTipi, stok_metni_olustur, miktar_dogrula, UndoIslemi
from ayarlar import metinler, renkler
from ui_bilesenleri import FontManager, OzelOnayKutusu, OzelBilgiKutusu

class EnvanterSayfasi(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.db = app.db
        self.kur()

    def kur(self):
        ust_frame = ctk.CTkFrame(self, fg_color="transparent")
        ust_frame.pack(fill="x", padx=10, pady=(0, 15))

        dash_frame = ctk.CTkFrame(ust_frame, fg_color=renkler["buton_mavi"], corner_radius=10)
        dash_frame.pack(side="left", fill="y", ipadx=15, ipady=5)
        self.lbl_istatistik = ctk.CTkLabel(dash_frame, text=metinler[self.app.aktif_dil]["yukleniyor"], font=FontManager.get_font(15, "bold"), text_color="#FFFFFF")
        self.lbl_istatistik.pack(expand=True)

        self.arama_degiskeni = ctk.StringVar()
        self.arama_entry = ctk.CTkEntry(ust_frame, textvariable=self.arama_degiskeni, placeholder_text=metinler[self.app.aktif_dil]["arama"], font=FontManager.get_font(14), width=300, height=35)
        self.arama_entry.pack(side="left", padx=(20, 10))
        self.arama_degiskeni.trace_add("write", lambda *args: self.envanter_kartlarini_ciz())

        btn_export = ctk.CTkButton(ust_frame, text=metinler[self.app.aktif_dil]["disa_aktar"], font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], hover_color="#059669", height=35, width=120, command=self.excel_disa_aktar)
        btn_export.pack(side="right")

        self.liste_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=5, pady=0)
        self.envanter_kartlarini_ciz()

    def envanter_kartlarini_ciz(self):
        for widget in self.liste_frame.winfo_children(): widget.destroy()
        gosterilecekler = self.db.malzemeleri_getir(self.arama_degiskeni.get().strip())
        self.lbl_istatistik.configure(text=f"{metinler[self.app.aktif_dil]['toplam']}\n{len(gosterilecekler)} Adet")

        if not gosterilecekler: 
            ctk.CTkLabel(self.liste_frame, text=metinler[self.app.aktif_dil]["bulunamadi"], text_color=renkler["yazi_ikincil"], font=FontManager.get_font(16)).pack(pady=40)
        else:
            for m in gosterilecekler:
                kart = ctk.CTkFrame(self.liste_frame, corner_radius=12, fg_color=renkler["kart"])
                kart.pack(fill="x", pady=8, padx=5)
                kart.grid_columnconfigure(0, weight=1); kart.grid_columnconfigure(1, weight=1); kart.grid_columnconfigure(2, weight=0)

                isim_frame = ctk.CTkFrame(kart, fg_color="transparent")
                isim_frame.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")
                ctk.CTkLabel(isim_frame, text=m['isim'], font=FontManager.get_font(20, "bold"), text_color=renkler["yazi_ana"]).pack(anchor="w")
                if m['lokasyon']: ctk.CTkLabel(isim_frame, text=f"📍 {m['lokasyon']}", text_color=renkler["yazi_ikincil"], font=FontManager.get_font(13)).pack(anchor="w", pady=(2, 0))
                if m['notlar']: ctk.CTkLabel(isim_frame, text=f"📝 {m['notlar']}", text_color=renkler["uyari"], font=FontManager.get_font(13, "normal", "italic")).pack(anchor="w", pady=(4, 0))
                
                stok_metni = stok_metni_olustur(m['miktar'], m['birim'], m['ikinci_miktar'], m['ikinci_birim'], m['ucuncu_miktar'], m['ucuncu_birim'])
                stok_renk = renkler["basari"] if m['miktar'] > 0 else renkler["tehlike"]
                ctk.CTkLabel(kart, text=stok_metni, font=FontManager.get_font(18, "bold"), text_color=stok_renk).grid(row=0, column=1, padx=20, pady=15, sticky="w")

                buton_frame = ctk.CTkFrame(kart, fg_color="transparent")
                buton_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")
                ctk.CTkButton(buton_frame, text=metinler[self.app.aktif_dil]["guncelle"], width=90, font=FontManager.get_font(14, "bold"), fg_color=renkler["buton_mavi"], hover_color=renkler["buton_mavi_hover"], command=lambda m_id=m['id']: self.stok_guncelle_penceresi(m_id)).pack(side="left", padx=5)
                ctk.CTkButton(buton_frame, text=metinler[self.app.aktif_dil]["sil"], width=70, font=FontManager.get_font(14, "bold"), fg_color=renkler["tehlike"], hover_color="#B91C1C", command=lambda m_id=m['id']: self.malzeme_sil_onay(m_id)).pack(side="left", padx=5)

    def excel_disa_aktar(self):
        dosya_yolu = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")], title="Envanteri Kaydet")
        if not dosya_yolu: return
        try:
            with open(dosya_yolu, 'w', newline='', encoding='utf-8-sig') as dosya:
                yazici = csv.writer(dosya, delimiter=';')
                yazici.writerow(["ID", "İsim", "Miktar 1", "Birim 1", "Miktar 2", "Birim 2", "Miktar 3", "Birim 3", "Lokasyon", "Notlar"])
                for m in self.db.malzemeleri_getir(): 
                    yazici.writerow([m['id'], m['isim'], m['miktar'], m['birim'], m['ikinci_miktar'], m['ikinci_birim'], m['ucuncu_miktar'], m['ucuncu_birim'], m['lokasyon'], m['notlar']])
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", f"Envanter başarıyla dışa aktarıldı:\n{dosya_yolu}", renk=renkler["basari"])
        except Exception as e: OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])

    def stok_guncelle_penceresi(self, malzeme_id):
        eski_m = self.db.malzeme_getir_id(malzeme_id)
        if not eski_m: return
        p = ctk.CTkToplevel(self)
        p.title(metinler[self.app.aktif_dil]["guncelle"])
        p.geometry("450x550")
        p.attributes("-topmost", True)
        p.transient(self.winfo_toplevel())
        p.grab_set()
        p.configure(fg_color=renkler["arkaplan"])

        ctk.CTkLabel(p, text=f"{eski_m.isim} {metinler[self.app.aktif_dil]['guncelle']}", font=FontManager.get_font(18, "bold"), text_color=renkler["yazi_ana"]).pack(pady=10)
        lbl_font = FontManager.get_font(13)
        
        ctk.CTkLabel(p, text=metinler[self.app.aktif_dil]["lokasyon_guncelle"], font=lbl_font, text_color=renkler["yazi_ana"]).pack(anchor="w", padx=20)
        entry_lok = ctk.CTkEntry(p, width=410, font=FontManager.get_font(14))
        entry_lok.insert(0, eski_m.lokasyon)
        entry_lok.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(p, text=metinler[self.app.aktif_dil]["sayilan_miktarlar"], font=FontManager.get_font(13, "bold"), text_color=renkler["buton_mavi"]).pack(anchor="w", padx=20, pady=(10, 5))
        birimler = ["Koli", "Paket", "Kutu", "Şişe", "Adet", "ml", "L", "g", "mg", ""]

        def satir(isim, m_val, b_val):
            f = ctk.CTkFrame(p, fg_color="transparent")
            f.pack(padx=20, pady=5, fill="x")
            ctk.CTkLabel(f, text=isim, width=100, anchor="w", font=lbl_font, text_color=renkler["yazi_ana"]).pack(side="left")
            e = ctk.CTkEntry(f, width=100, font=FontManager.get_font(14))
            e.insert(0, str(m_val))
            e.pack(side="left", padx=10)
            c = ctk.CTkComboBox(f, values=birimler, width=120, font=FontManager.get_font(14))
            c.set(b_val if b_val in birimler else "")
            c.pack(side="left")
            return e, c

        e_m1, c_b1 = satir(metinler[self.app.aktif_dil]["ana_miktar"], eski_m.miktar, eski_m.birim)
        e_m2, c_b2 = satir(metinler[self.app.aktif_dil]["ek_miktar_2"], eski_m.ikinci_miktar, eski_m.ikinci_birim)
        e_m3, c_b3 = satir(metinler[self.app.aktif_dil]["ek_miktar_3"], eski_m.ucuncu_miktar, eski_m.ucuncu_birim)

        ctk.CTkLabel(p, text=metinler[self.app.aktif_dil]["notlar"], font=lbl_font, text_color=renkler["yazi_ana"]).pack(anchor="w", padx=20, pady=(10, 0))
        t_not = ctk.CTkTextbox(p, width=410, height=60, font=FontManager.get_font(14))
        if eski_m.notlar: t_not.insert("1.0", eski_m.notlar)
        t_not.pack(padx=20, pady=(0, 10))

        def kaydet():
            try:
                yeni_m = Malzeme(
                    id=malzeme_id, isim=eski_m.isim, ambalaj_tipi="", 
                    miktar=miktar_dogrula(e_m1.get().strip()), birim=c_b1.get(),
                    ikinci_miktar=miktar_dogrula(e_m2.get().strip()), ikinci_birim=c_b2.get(), 
                    ucuncu_miktar=miktar_dogrula(e_m3.get().strip()), ucuncu_birim=c_b3.get(),
                    donusum_orani=0.0, lokasyon=entry_lok.get(), notlar=t_not.get("1.0", "end-1c")
                )
                self.db.stok_guncelle(yeni_m)
                
                degisim = []
                if eski_m.miktar != yeni_m.miktar: degisim.append(f"Ana: {eski_m.miktar}->{yeni_m.miktar}")
                if eski_m.ikinci_miktar != yeni_m.ikinci_miktar: degisim.append(f"Ek1: {eski_m.ikinci_miktar}->{yeni_m.ikinci_miktar}")
                if eski_m.ucuncu_miktar != yeni_m.ucuncu_miktar: degisim.append(f"Ek2: {eski_m.ucuncu_miktar}->{yeni_m.ucuncu_miktar}")
                detay = f"{IslemTipi.GUNCELLEME.value} [{', '.join(degisim)}]" if degisim else "Bilgiler Güncellendi"
                
                log_id = self.db.gecmis_ekle(malzeme_id, eski_m.isim, detay, self.app.kullanici_adi)
                self.app.islem_gecmisi.append(UndoIslemi(tip="guncelleme", malzeme_id=malzeme_id, malzeme_isim=eski_m.isim, log_id=log_id, eski_malzeme=eski_m, yeni_malzeme=yeni_m))
                self.app.ileri_gecmisi.clear()
                
                p.destroy()
                self.app.gui_guncelle()
            except ValueError as e: OzelBilgiKutusu(p, "Hata", str(e), renk=renkler["tehlike"])

        ctk.CTkButton(p, text=metinler[self.app.aktif_dil]["yeni_deger_kaydet"], font=FontManager.get_font(14, "bold"), fg_color=renkler["basari"], hover_color="#059669", height=40, command=kaydet).pack(pady=10)

    def malzeme_sil_onay(self, malzeme_id):
        mesaj = metinler[self.app.aktif_dil]["emin_misin_malzeme"]
        OzelOnayKutusu(self.winfo_toplevel(), baslik=metinler[self.app.aktif_dil]["sil"], mesaj=mesaj, evet_komut=lambda: self.malzeme_sil_islemi(malzeme_id), evet_metni=metinler[self.app.aktif_dil]["evet"], hayir_metni=metinler[self.app.aktif_dil]["hayir"])

    def malzeme_sil_islemi(self, malzeme_id):
        m = self.db.malzeme_getir_id(malzeme_id) 
        if not m: return
        self.db.malzeme_sil(malzeme_id)
        stok_log = stok_metni_olustur(m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim)
        log_id = self.db.gecmis_ekle(malzeme_id, m.isim, f"{IslemTipi.SILME.value} (Son: {stok_log})", self.app.kullanici_adi)
        self.app.islem_gecmisi.append(UndoIslemi(tip="silme", malzeme_id=malzeme_id, malzeme_isim=m.isim, log_id=log_id, eski_malzeme=m))
        self.app.ileri_gecmisi.clear()
        self.app.gui_guncelle()