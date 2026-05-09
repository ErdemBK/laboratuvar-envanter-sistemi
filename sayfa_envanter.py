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
        
        self.lbl_ist = ctk.CTkLabel(
            dash_frame, 
            text=metinler[self.app.aktif_dil]["yukleniyor"], 
            font=FontManager.get_font(15, "bold"), 
            text_color="#FFFFFF"
        )
        self.lbl_ist.pack(expand=True)
        
        self.arama_deg = ctk.StringVar()
        e_ara = ctk.CTkEntry(
            ust_frame, 
            textvariable=self.arama_deg, 
            placeholder_text=metinler[self.app.aktif_dil]["arama"], 
            width=300, 
            height=35,
            font=FontManager.get_font(14)
        )
        e_ara.pack(side="left", padx=(20, 10))
        self.arama_deg.trace_add("write", lambda *args: self.envanter_kartlarini_ciz())
        
        ctk.CTkButton(
            ust_frame, 
            text=metinler[self.app.aktif_dil]["disa_aktar"], 
            font=FontManager.get_font(14, "bold"),
            fg_color=renkler["basari"], 
            height=35, 
            command=self.excel_disa_aktar
        ).pack(side="right")
        
        self.liste_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=5)
        
        self.envanter_kartlarini_ciz()

    def envanter_kartlarini_ciz(self):
        for w in self.liste_frame.winfo_children(): 
            w.destroy()
            
        gs = self.db.malzemeleri_getir(self.arama_deg.get().strip())
        dil = self.app.aktif_dil
        
        self.lbl_ist.configure(text=f"{metinler[dil]['toplam']}\n{len(gs)} Adet")
        
        if not gs: 
            ctk.CTkLabel(
                self.liste_frame, 
                text=metinler[dil]["bulunamadi"], 
                font=FontManager.get_font(16),
                text_color=renkler["yazi_ikincil"]
            ).pack(pady=40)
        else:
            for m in gs:
                k = ctk.CTkFrame(self.liste_frame, corner_radius=12, fg_color=renkler["kart"])
                k.pack(fill="x", pady=8, padx=5)
                k.grid_columnconfigure(0, weight=1)
                k.grid_columnconfigure(1, weight=1)
                k.grid_columnconfigure(2, weight=0)
                
                isim_frame = ctk.CTkFrame(k, fg_color="transparent")
                isim_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")
                
                ctk.CTkLabel(
                    isim_frame, 
                    text=m.get('isim', ''), 
                    font=FontManager.get_font(20, "bold"),
                    text_color=renkler["yazi_ana"]
                ).pack(anchor="w")
                
                if m.get('lokasyon', ''): 
                    ctk.CTkLabel(
                        isim_frame, 
                        text=f"📍 {m['lokasyon']}", 
                        font=FontManager.get_font(13), 
                        text_color=renkler["yazi_ikincil"]
                    ).pack(anchor="w")
                    
                if m.get('notlar', ''):
                    # SİSTEMİ ÇÖKTÜREN HATA BURADAYDI! slant="italic" olarak düzeltildi.
                    ctk.CTkLabel(
                        isim_frame, 
                        text=f"📝 {m['notlar']}", 
                        font=FontManager.get_font(13, slant="italic"), 
                        text_color=renkler["uyari"]
                    ).pack(anchor="w", pady=(4, 0))
                
                stok_frame = ctk.CTkFrame(k, fg_color="transparent")
                stok_frame.grid(row=0, column=1, padx=20, sticky="w")
                
                sm = stok_metni_olustur(
                    m.get('miktar', 0.0), m.get('birim', ''), 
                    m.get('ikinci_miktar', 0.0), m.get('ikinci_birim', ''), 
                    m.get('ucuncu_miktar', 0.0), m.get('ucuncu_birim', ''), 
                    m.get('dorduncu_miktar', 0.0), m.get('dorduncu_birim', ''), 
                    m.get('besinci_miktar', 0.0), m.get('besinci_birim', ''), 
                    aktif_dil=dil
                )
                
                if sm == "0":
                    badge = ctk.CTkFrame(stok_frame, fg_color=renkler["tehlike"], corner_radius=6)
                    badge.pack(side="left", padx=2)
                    ctk.CTkLabel(badge, text="0", font=FontManager.get_font(14, "bold"), text_color="#FFFFFF").pack(padx=10, pady=2)
                else:
                    for p in sm.split("  •  "):
                        badge = ctk.CTkFrame(stok_frame, fg_color=renkler["basari"], corner_radius=6)
                        badge.pack(side="left", padx=3)
                        ctk.CTkLabel(badge, text=p.strip(), font=FontManager.get_font(14, "bold"), text_color="#FFFFFF").pack(padx=10, pady=2)

                bf = ctk.CTkFrame(k, fg_color="transparent")
                bf.grid(row=0, column=2, padx=20, sticky="e")
                
                ctk.CTkButton(
                    bf, 
                    text=metinler[dil]["guncelle"], 
                    width=90, 
                    font=FontManager.get_font(14, "bold"),
                    command=lambda x=m['id']: self.stok_guncelle_penceresi(x)
                ).pack(side="left", padx=5)
                
                ctk.CTkButton(
                    bf, 
                    text=metinler[dil]["sil"], 
                    width=70, 
                    font=FontManager.get_font(14, "bold"),
                    fg_color=renkler["tehlike"], 
                    command=lambda x=m['id']: self.malzeme_sil_onay(x)
                ).pack(side="left", padx=5)

    def excel_disa_aktar(self):
        y = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
        if not y: return
        try:
            dil = self.app.aktif_dil
            with open(y, 'w', newline='', encoding='utf-8-sig') as f:
                wr = csv.writer(f, delimiter=';')
                
                # İki noktalı "Özel Notlar:" yerine sade Excel başlığı kullandık
                notlar_baslik = "Notlar" if dil == "TR" else "Notes"
                
                wr.writerow([
                    metinler[dil]["excel_isim"], 
                    metinler[dil]["excel_miktar"], 
                    metinler[dil]["excel_lok"], 
                    notlar_baslik
                ])
                for m in self.db.malzemeleri_getir():
                    d = stok_metni_olustur(
                        m.get('miktar', 0.0), m.get('birim', ''), 
                        m.get('ikinci_miktar', 0.0), m.get('ikinci_birim', ''), 
                        m.get('ucuncu_miktar', 0.0), m.get('ucuncu_birim', ''), 
                        m.get('dorduncu_miktar', 0.0), m.get('dorduncu_birim', ''), 
                        m.get('besinci_miktar', 0.0), m.get('besinci_birim', ''), 
                        dil
                    )
                    wr.writerow([m.get('isim', ''), d, m.get('lokasyon', ''), m.get('notlar', '')])
                    
            OzelBilgiKutusu(self.winfo_toplevel(), "Başarılı", "Excel başarıyla oluşturuldu.", renk=renkler["basari"])
        except Exception as e: 
            OzelBilgiKutusu(self.winfo_toplevel(), "Hata", str(e), renk=renkler["tehlike"])

    def stok_guncelle_penceresi(self, mid):
        em = self.db.malzeme_getir_id(mid)
        if not em: return
        
        p = ctk.CTkToplevel(self)
        p.title(metinler[self.app.aktif_dil]["guncelle"])
        p.geometry("450x650")
        p.attributes("-topmost", True)
        p.grab_set()
        p.configure(fg_color=renkler["arkaplan"])
        
        ctk.CTkLabel(
            p, 
            text=f"{em.isim} {metinler[self.app.aktif_dil]['guncelle']}", 
            font=FontManager.get_font(18, "bold"),
            text_color=renkler["yazi_ana"]
        ).pack(pady=10)
        
        e_l = ctk.CTkEntry(p, width=410, font=FontManager.get_font(14))
        e_l.insert(0, em.lokasyon)
        e_l.pack(padx=20, pady=10)
        
        brs = metinler[self.app.aktif_dil]["birimler"]
        
        def satir(txt, mv, bv):
            f = ctk.CTkFrame(p, fg_color="transparent")
            f.pack(padx=20, pady=5, fill="x")
            
            ctk.CTkLabel(
                f, text=txt, width=100, anchor="w", 
                font=FontManager.get_font(14), text_color=renkler["yazi_ana"]
            ).pack(side="left")
            
            e = ctk.CTkEntry(f, width=100, font=FontManager.get_font(14))
            e.insert(0, str(mv))
            e.pack(side="left", padx=10)
            
            c = ctk.CTkComboBox(f, values=brs, width=120, font=FontManager.get_font(14))
            c.set(bv)
            c.pack(side="left")
            
            return e, c
            
        e1, c1 = satir(metinler[self.app.aktif_dil]["ana_miktar"], em.miktar, em.birim)
        e2, c2 = satir(metinler[self.app.aktif_dil]["ek_miktar_2"], em.ikinci_miktar, em.ikinci_birim)
        e3, c3 = satir(metinler[self.app.aktif_dil]["ek_miktar_3"], em.ucuncu_miktar, em.ucuncu_birim)
        e4, c4 = satir(metinler[self.app.aktif_dil]["ek_miktar_4"], em.dorduncu_miktar, em.dorduncu_birim)
        e5, c5 = satir(metinler[self.app.aktif_dil]["ek_miktar_5"], em.besinci_miktar, em.besinci_birim)
        
        t_n = ctk.CTkTextbox(p, width=410, height=60, font=FontManager.get_font(14))
        t_n.insert("1.0", em.notlar if em.notlar else "")
        t_n.pack(padx=20, pady=10)
        
        def kaydet():
            try:
                ym = Malzeme(
                    id=mid, isim=em.isim, 
                    miktar=miktar_dogrula(e1.get()), birim=c1.get(), 
                    ikinci_miktar=miktar_dogrula(e2.get()), ikinci_birim=c2.get(), 
                    ucuncu_miktar=miktar_dogrula(e3.get()), ucuncu_birim=c3.get(), 
                    dorduncu_miktar=miktar_dogrula(e4.get()), dorduncu_birim=c4.get(), 
                    besinci_miktar=miktar_dogrula(e5.get()), besinci_birim=c5.get(), 
                    lokasyon=e_l.get(), notlar=t_n.get("1.0", "end-1c")
                )
                self.db.stok_guncelle(ym)
                lid = self.db.gecmis_ekle(mid, em.isim, metinler[self.app.aktif_dil]["log_guncellendi"], self.app.kullanici_adi)
                self.app.islem_gecmisi.append(UndoIslemi(tip="guncelleme", malzeme_id=mid, malzeme_isim=em.isim, log_id=lid, eski_malzeme=em, yeni_malzeme=ym))
                
                p.destroy()
                self.app.gui_guncelle()
            except ValueError as e:
                OzelBilgiKutusu(p, "Hata", str(e), renk=renkler["tehlike"])
                
        ctk.CTkButton(
            p, 
            text=metinler[self.app.aktif_dil]["kaydet"], 
            font=FontManager.get_font(14, "bold"),
            fg_color=renkler["basari"], 
            command=kaydet
        ).pack(pady=10)

    def malzeme_sil_onay(self, mid):
        OzelOnayKutusu(
            self.winfo_toplevel(), 
            metinler[self.app.aktif_dil]["onay_baslik"], 
            metinler[self.app.aktif_dil]["emin_misin_malzeme"], 
            lambda: self.malzeme_sil_islemi(mid)
        )

    def malzeme_sil_islemi(self, mid):
        m = self.db.malzeme_getir_id(mid)
        dil = self.app.aktif_dil
        if m:
            self.db.malzeme_sil(mid)
            sl = stok_metni_olustur(m.miktar, m.birim, m.ikinci_miktar, m.ikinci_birim, m.ucuncu_miktar, m.ucuncu_birim, m.dorduncu_miktar, m.dorduncu_birim, m.besinci_miktar, m.besinci_birim, dil)
            tx = f"{metinler[dil]['log_silindi']} ({metinler[dil]['log_stok']}: {sl})"
            lid = self.db.gecmis_ekle(mid, m.isim, tx, self.app.kullanici_adi)
            
            self.app.islem_gecmisi.append(UndoIslemi(tip="silme", malzeme_id=mid, malzeme_isim=m.isim, log_id=lid, eski_malzeme=m))
            self.app.gui_guncelle()