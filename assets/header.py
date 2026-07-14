import os
import customtkinter as ctk
from PIL import Image

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))


def buat_header(parent, title_text, username=None):

    header = ctk.CTkFrame(parent, height=80, fg_color="#064E3B")
    header.pack(fill="x")

    # kiri
    header_left = ctk.CTkFrame(header, fg_color="transparent")
    header_left.pack(side="left", padx=20)

    logo_img = ctk.CTkImage(
        light_image=Image.open(os.path.join(ASSETS_DIR, "logo.png")),
        size=(40, 40)
    )

    logo_label = ctk.CTkLabel(header_left, image=logo_img, text="")
    logo_label.pack(side="left", padx=(0, 10), pady=20)

    title = ctk.CTkLabel(
        header_left,
        text=title_text,
        text_color="white",
        font=("Segoe UI", 24, "bold")
    )
    title.pack(side="left")

    if username:
        user_label = ctk.CTkLabel(
            header,
            text=f"Selamat datang, {username}",
            text_color="white",
            font=("Segoe UI", 14, "bold")
        )
        user_label.pack(side="right", padx=20)