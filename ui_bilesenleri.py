# ui_bilesenleri.py
import flet as ft
import ayarlar
import tkinter as tk
from tkinter import filedialog
import os
import subprocess

def goster_toast(page: ft.Page, mesaj: str, basari: bool = True):
    renk = ayarlar.TEMA_RENKLER["basari_yesil"] if basari else ayarlar.TEMA_RENKLER["tehlike_kirmizi"]
    ikon = "✅" if basari else "❌"
    snack = ft.SnackBar(content=ft.Row([ft.Text(ikon, size=16), ft.Text(mesaj, color="#FFFFFF", weight="bold")]), bgcolor=renk, duration=2000, behavior="floating", width=400)
    page.overlay.append(snack); snack.open = True; page.update()

def dialog_ac(page: ft.Page, dlg: ft.AlertDialog):
    page.overlay.append(dlg); dlg.open = True; page.update()

def dialog_kapat(page: ft.Page, dlg: ft.AlertDialog):
    dlg.open = False; page.update()

def dosya_kaydet_dialog(baslik, varsayilan_isim, uzanti):
    try:
        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
        yol = filedialog.asksaveasfilename(title=baslik, initialfile=varsayilan_isim, defaultextension=uzanti, filetypes=[("Dosya", f"*{uzanti}")])
        root.destroy()
        return yol
    except: return None

def dosya_sec_dialog(baslik, uzanti):
    try:
        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
        yol = filedialog.askopenfilename(title=baslik, filetypes=[("Dosya", f"*{uzanti}")])
        root.destroy()
        return yol
    except: return None

def panoya_kopyala(metin):
    try:
        # Windows için CMD üzerinden %100 çökmeyen native kopyalama
        if os.name == 'nt': 
            subprocess.run("clip", text=True, input=metin, shell=True)
            return True
        else:
            # Mac/Linux sistemleri için standart yöntem
            root = tk.Tk(); root.withdraw()
            root.clipboard_clear(); root.clipboard_append(metin); root.update()
            root.destroy()
            return True
    except: return False