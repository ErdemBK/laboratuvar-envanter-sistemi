# dosya: ui_bilesenleri.py
# ---------------------------------------------------------
import customtkinter as ctk
from ayarlar import renkler, font_tipi

# 16. Madde: Singleton Font Yöneticisi (Performans Artışı)
class FontManager:
    _fonts = {}

    @classmethod
    def get_font(cls, size: int, weight: str = "normal", slant: str = "roman") -> ctk.CTkFont:
        key = f"{size}_{weight}_{slant}"
        if key not in cls._fonts:
            cls._fonts[key] = ctk.CTkFont(family=font_tipi, size=size, weight=weight, slant=slant)
        return cls._fonts[key]

class OzelOnayKutusu(ctk.CTkToplevel):
    def __init__(self, master, baslik, mesaj, evet_komut, evet_metni="Evet", hayir_metni="Hayır"):
        super().__init__(master)
        self.title(baslik)
        self.geometry("400x180")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=renkler["arkaplan"])
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        self.geometry(f"+{(self.winfo_screenwidth() - 400) // 2}+{(self.winfo_screenheight() - 180) // 2}")

        ctk.CTkLabel(self, text=mesaj, font=FontManager.get_font(16), text_color=renkler["yazi_ana"], wraplength=350).pack(pady=(30, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()
        ctk.CTkButton(btn_frame, text=hayir_metni, width=100, font=FontManager.get_font(14, "bold"), fg_color="#7f8c8d", hover_color="#95a5a6", command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=evet_metni, width=100, font=FontManager.get_font(14, "bold"), fg_color=renkler["tehlike"], hover_color="#B91C1C", command=lambda: self.onaylandi(evet_komut)).pack(side="left", padx=10)

    def onaylandi(self, komut):
        komut()
        self.destroy()

class OzelBilgiKutusu(ctk.CTkToplevel):
    def __init__(self, master, baslik, mesaj, renk="#3B82F6"):
        super().__init__(master)
        self.title(baslik)
        self.geometry("380x160")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=renkler["arkaplan"])
        self.transient(master)
        self.grab_set()

        self.update_idletasks()
        self.geometry(f"+{(self.winfo_screenwidth() - 380) // 2}+{(self.winfo_screenheight() - 160) // 2}")

        ctk.CTkLabel(self, text=mesaj, font=FontManager.get_font(15), text_color=renkler["yazi_ana"], wraplength=340).pack(pady=(25, 20))
        ctk.CTkButton(self, text="Tamam", width=100, font=FontManager.get_font(14, "bold"), fg_color=renk, command=self.destroy).pack()