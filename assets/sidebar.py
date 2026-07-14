import customtkinter as ctk
from PIL import Image
import os

PRIMARY   = "#064E3B"
SECONDARY = "#149060"
SIDEBAR_W = 240

def buat_sidebar(parent, role, nama_user, menu_items, active_key, on_select, on_logout):
    sidebar = ctk.CTkFrame(parent, width=SIDEBAR_W, fg_color=PRIMARY, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # ── Logo
    top = ctk.CTkFrame(sidebar, fg_color="transparent")
    top.pack(fill="x", padx=16, pady=(20, 10))
    try:
        logo_img = ctk.CTkImage(Image.open("assets/logo.png"), size=(38, 38))
        ctk.CTkLabel(top, image=logo_img, text="").pack(side="left", padx=(0,10))
    except:
        pass
    txt = ctk.CTkFrame(top, fg_color="transparent")
    txt.pack(side="left")
    ctk.CTkLabel(txt, text="SISTEM LAYANAN", font=("Segoe UI", 12, "bold"),
                 text_color="#A7F3D0", height=14).pack(anchor="w", pady=(0,0))
    ctk.CTkLabel(txt, text="ADMINISTRASI NIKAH", font=("Segoe UI", 14, "bold"),
                 text_color="white", height=18).pack(anchor="w", pady=(0,0))

    ctk.CTkFrame(sidebar, height=1, fg_color="#1a6b4a").pack(fill="x", padx=16, pady=8)

    # ── Info user
    info = ctk.CTkFrame(sidebar, fg_color="transparent")
    info.pack(fill="x", padx=16, pady=(4, 12))
    ctk.CTkLabel(info, text="Selamat Datang,", font=("Segoe UI", 10),
                 text_color="#A7F3D0").pack(anchor="w")
    ctk.CTkLabel(info, text=nama_user, font=("Segoe UI", 12, "bold"),
                 text_color="white", wraplength=190, justify="left").pack(anchor="w")
    role_label = {"admin": "Administrator", "penghulu": "Penghulu", "pengantin": "Calon Pengantin"}
    ctk.CTkLabel(info, text=role_label.get(role, role),
                 font=("Segoe UI", 10, "bold"), text_color="white",
                 fg_color=SECONDARY, corner_radius=12, padx=10, pady=3).pack(anchor="w", pady=(6,0))

    ctk.CTkFrame(sidebar, height=1, fg_color="#1a6b4a").pack(fill="x", padx=16, pady=8)

    # ── Menu items
    btn_refs = {}
    menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    menu_frame.pack(fill="x")

    def make_btn(key, label):
        is_active = (key == active_key)
        btn = ctk.CTkButton(
            menu_frame, text=label,
            anchor="w", font=("Segoe UI", 13, "bold" if is_active else "normal"),
            fg_color="white" if is_active else "transparent",
            text_color=PRIMARY if is_active else "white",
            hover_color="#e8f5f0" if is_active else "#0D6342",
            height=42, corner_radius=8,
            command=lambda k=key: on_select(k)
        )
        btn.pack(fill="x", padx=12, pady=2)
        btn_refs[key] = btn

    for key, label in menu_items:
        make_btn(key, label)

    # ── Logout — place() di bottom agar tidak pernah terpotong
    logout_area = ctk.CTkFrame(sidebar, fg_color=PRIMARY, height=70)
    logout_area.pack(side="bottom", fill="x")
    logout_area.pack_propagate(False)
    ctk.CTkFrame(logout_area, height=1, fg_color="#1a6b4a").pack(fill="x", padx=16, pady=(0,6))
    ctk.CTkButton(logout_area, text="KELUAR",
                  fg_color="#D32F2F", hover_color="#B71C1C",
                  font=("Segoe UI", 13, "bold"), height=42, corner_radius=8,
                  command=on_logout).pack(fill="x", padx=12, pady=(0,8))

    return sidebar, btn_refs
