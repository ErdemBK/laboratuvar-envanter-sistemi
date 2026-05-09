import customtkinter as ctk
from ayarlar import font_tipi, renkler

class FontManager:
    @staticmethod
    def get_font(size, weight="normal", slant="roman"):
        return ctk.CTkFont(family=font_tipi, size=size, weight=weight, slant=slant)

def OzelBilgiKutusu(master, baslik, mesaj, renk=renkler["basari"]):
    p = ctk.CTkToplevel(master)
    p.title(baslik)
    p.geometry("300x150")
    p.attributes("-topmost", True)
    p.grab_set()
    p.configure(fg_color=renkler["arkaplan"])
    
    ctk.CTkLabel(p, text=baslik, font=FontManager.get_font(16, "bold"), text_color=renk).pack(pady=(20, 10))
    ctk.CTkLabel(p, text=mesaj, font=FontManager.get_font(13), text_color=renkler["yazi_ana"], wraplength=260).pack(pady=5)
    ctk.CTkButton(p, text="Tamam", command=p.destroy, fg_color=renk).pack(pady=10)

def OzelOnayKutusu(master, baslik, mesaj, evet_komut):
    p = ctk.CTkToplevel(master)
    p.title(baslik)
    p.geometry("350x180")
    p.attributes("-topmost", True)
    p.grab_set()
    p.configure(fg_color=renkler["arkaplan"])
    
    ctk.CTkLabel(p, text=baslik, font=FontManager.get_font(16, "bold"), text_color=renkler["yazi_ana"]).pack(pady=(20, 10))
    ctk.CTkLabel(p, text=mesaj, font=FontManager.get_font(13), text_color=renkler["yazi_ikincil"], wraplength=300).pack(pady=5)
    
    f = ctk.CTkFrame(p, fg_color="transparent")
    f.pack(pady=10)
    
    def on_evet():
        p.destroy()     # Önce onay kutusunu yok et
        master.update() # Ekranı hemen tazele
        evet_komut()    # SONRA dosya seçme işlemini başlat (Böylece takılıp kalmayacak)
        
    ctk.CTkButton(f, text="Evet", fg_color=renkler["basari"], width=100, command=on_evet).pack(side="left", padx=10)
    ctk.CTkButton(f, text="Hayır", fg_color=renkler["tehlike"], width=100, command=p.destroy).pack(side="left", padx=10)