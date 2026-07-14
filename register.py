import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

def register_user(nik, nama, password, confirm):
    # Validasi Input Kosong
    if nik == "" or nama == "" or password == "":
        messagebox.showerror("Error", "Semua field harus diisi")
        return False

    # Validasi NIK (Standar 16 digit)
    if not nik.isdigit() or len(nik) != 16:
        messagebox.showerror("Error", "NIK harus berupa 16 digit angka")
        return False

    # Validasi Konfirmasi Password
    if password != confirm:
        messagebox.showerror("Error", "Password tidak sama")
        return False

    # Cek Duplikasi NIK di Database
    path = "database/pengguna.txt"
    if not os.path.exists("database"): os.makedirs("database")
    
    try:
        with open(path, "r") as file:
            users = file.readlines()
    except FileNotFoundError:
        users = []

    for user in users:
        data = user.strip().split("|")
        # data[0] adalah NIK
        if len(data) > 0 and nik == data[0]:
            messagebox.showerror("Error", "NIK sudah terdaftar!")
            return False

    # impan Data pengguna
    with open(path, "a") as file:
        file.write(f"{nik}|{password}|pengantin|{nama}\n")

    messagebox.showinfo("Sukses", "Akun berhasil dibuat! Silakan Login.")
    return True

def register_page():
    window = ctk.CTk()
    window.title("Register Akun - Sistem KUA")
    window.after(0, lambda: window.state('zoomed'))

    # Header
    header = ctk.CTkFrame(window, height=80, fg_color="#064E3B")
    header.pack(fill="x")
    header_left = ctk.CTkFrame(header, fg_color="transparent")
    header_left.pack(side="left", padx=20)

    try:
        logo_img = ctk.CTkImage(light_image=Image.open("assets/logo.png"), size=(40, 40))
        logo = ctk.CTkLabel(header_left, image=logo_img, text="")
        logo.pack(side="left", padx=(0, 10), pady=20)
    except:
        pass

    ctk.CTkLabel(header_left, text="Registrasi Akun Baru", text_color="white", 
                    font=("Segoe UI", 22, "bold")).pack(side="left")

    # form register
    main_frame = ctk.CTkFrame(window, fg_color="transparent")
    main_frame.pack(expand=True, fill="both")

    form_card = ctk.CTkFrame(main_frame, fg_color="transparent")
    form_card.place(relx=0.5, rely=0.5, anchor="center") 

    ctk.CTkLabel(form_card, text="Lengkapi Data Diri", font=("Segoe UI", 26, "bold")).pack(pady=20)

    # Input NIK
    nik_entry = ctk.CTkEntry(form_card, placeholder_text="NIK (Username)", 
                                width=350, height=45, border_width=2, border_color="#2E7D32")
    nik_entry.pack(pady=10)

    # Input Nama Lengkap
    nama_entry = ctk.CTkEntry(form_card, placeholder_text="Nama Lengkap Sesuai KTP", 
                                width=350, height=45, border_width=2, border_color="#2E7D32")
    nama_entry.pack(pady=10)

    # Input Password
    password_entry = ctk.CTkEntry(form_card, placeholder_text="Password", show="*", 
                                    width=350, height=45, border_width=2, border_color="#2E7D32")
    password_entry.pack(pady=10)

    # Konfirmasi Password
    confirm_entry = ctk.CTkEntry(form_card, placeholder_text="Konfirmasi Password", show="*", 
                                    width=350, height=45, border_width=2, border_color="#2E7D32")
    confirm_entry.pack(pady=10)

    def kembali_login():
        window.destroy()
        from login import login_page
        login_page()

    def proses_register():
        sukses = register_user(
            nik_entry.get(),
            nama_entry.get(),
            password_entry.get(),
            confirm_entry.get()
        )
        if sukses:
            kembali_login()

    ctk.CTkButton(form_card, text="DAFTAR SEKARANG", width=350, height=45, 
                    font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", command=proses_register).pack(pady=(20, 10))

    ctk.CTkButton(form_card, text="KEMBALI", width=350, height=40, 
                    font=("Segoe UI", 14, "bold"), fg_color="#149060", hover_color="#10B981", command=kembali_login).pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    register_page()