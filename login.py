import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from register import register_page
from assets.header import buat_header

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Fungsi memeriksa login
def check_login(user_input, password, app=None):
    from dashboard.dashboard_admin import dashboard_admin
    from dashboard.dashboard_penghulu import dashboard_penghulu
    from dashboard.dashboard_pengantin import dashboard_pengantin
    
    path = "database/pengguna.txt"
    if not os.path.exists(path):
        messagebox.showerror("Error", "Database tidak ditemukan!")
        return
    
    try:
        with open(path, "r") as file:
            for line in file:
                data = line.strip().split("|")
                if len(data) >= 3 and user_input == data[0] and password == data[1]:
                    role, nama_user = data[2], data[3] if len(data) > 3 else data[0]
                    messagebox.showinfo("Login Berhasil", f"Login sebagai: {nama_user}")
                    if app: app.destroy()
                    if role == "admin": dashboard_admin(nama_user)
                    elif role == "penghulu": dashboard_penghulu(nama_user)
                    elif role == "pengantin": dashboard_pengantin(nik_user=data[0], nama_user=nama_user)
                    return
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
        return
    messagebox.showerror("Gagal Masuk", "Username atau Password salah!")

def login_page():
    app = ctk.CTk()
    app.after(0, lambda: app.state('zoomed'))
    app.title("Sistem Layanan Administrasi Nikah KUA")

    buat_header(app, "SILAKU", "Tamu")

    body_frame = ctk.CTkFrame(app, fg_color="transparent")
    body_frame.pack(expand=True, fill="both")

    body_frame.grid_columnconfigure((0,1), weight=1)
    body_frame.grid_rowconfigure(0, weight=1)
    body_frame.grid_rowconfigure(1, weight=0)

    # Sidebar Kiri
    left_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
    left_frame.grid(row=0, column=0, sticky="nsew")

    try:
        bg_img_raw = Image.open("assets/bg_kua.png")
        bg_img = ctk.CTkImage(bg_img_raw, size=(1000, 1000))
        
        bg_label = ctk.CTkLabel(left_frame, image=bg_img, text="")
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    except:
        pass

    # Kontainer Konten 
    left_content = ctk.CTkFrame(left_frame, fg_color="#149060", border_width=3, border_color="#064E3B")
    left_content.pack(fill="x", padx=80, pady=(80, 0), anchor="w")

    ctk.CTkLabel(left_content, text="Sistem Layanan\nAdministrasi Nikah KUA", text_color="white",
                font=("Inter", 38, "bold"), anchor="w", justify="left", 
                fg_color="transparent").pack(fill="x",padx=40, pady=(40, 10))

    kemenag_mid = ctk.CTkFrame(left_content, fg_color="transparent")
    kemenag_mid.pack(fill="x",padx=40, pady=(10))

    try:
        k_img = ctk.CTkImage(Image.open("assets/kemenag_logo.png"), size=(55, 55))
        ctk.CTkLabel(kemenag_mid, image=k_img, text="", fg_color="transparent").pack(side="left")
    except: pass

    ctk.CTkLabel(kemenag_mid, text="KEMENTERIAN AGAMA\nREPUBLIK INDONESIA",
                text_color="white", font=("Segoe UI", 12, "bold"), justify="left", 
                fg_color="transparent").pack(side="left", padx=20)

    ctk.CTkLabel(left_content, text="Memudahkan pendaftaran pernikahan secara digital\ntanpa antri, kapan saja dan di mana saja.",
                text_color="#D1FAE5", justify="left", anchor="w", font=("Segoe UI", 15), 
                fg_color="transparent").pack(fill="x",padx=40, pady=(20, 40))

    # Sidebar Kanan 
    right_frame = ctk.CTkFrame(body_frame, corner_radius=0, fg_color="#FFFFFF")
    right_frame.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(right_frame, text="MASUK KE SISTEM", 
                font=("Segoe UI", 32, "bold"), text_color="#111827").pack(pady=(80, 40))

    u_entry = ctk.CTkEntry(right_frame, placeholder_text="🖂 Username", width=350, height=45, corner_radius=10, border_width=2, border_color="#2E7D32")
    u_entry.pack(pady=10)

    p_entry = ctk.CTkEntry(right_frame, placeholder_text="🔑 Password", show="*", width=350, height=45, corner_radius=10, border_width=2, border_color="#2E7D32")
    p_entry.pack(pady=10)

    # Tombol Login & Register
    ctk.CTkButton(right_frame, text="MASUK", width=350, height=48, corner_radius=10,
                    fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 15, "bold"),   
                    command=lambda: check_login(u_entry.get(), p_entry.get(), app)).pack(pady=(20, 15))

    ctk.CTkButton(right_frame, text="BELUM PUNYA AKUN? REGISTRASI!", width=350, height=48, corner_radius=10,
                    fg_color="#149060", hover_color="#10B981", font=("Segoe UI", 15, "bold"),
                    command=lambda: [app.destroy(), register_page()]).pack()

    # Alur Pendaftaran
    flow_frame = ctk.CTkFrame(body_frame, height=180, fg_color="#F9FAFB", corner_radius=0)
    flow_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    ctk.CTkLabel(flow_frame, text="ALUR PENDAFTARAN NIKAH ONLINE", font=("Segoe UI", 18, "bold"), text_color="#1F2937").pack(pady=(20,5))
    
    step_container = ctk.CTkFrame(flow_frame, fg_color="transparent")
    step_container.pack(pady=5)

    steps_data = [
        ("1. Daftar Akun", "Registrasi menggunakan NIK"),
        ("2. Isi Data", "Lengkapi formulir pendaftaran"),
        ("3. Plotting Penghulu", "Admin menentukan petugas"),
        ("4. Cek Status", "Lihat progres hingga selesai")
    ]

    for i, (judul, sub) in enumerate(steps_data):
        s_box = ctk.CTkFrame(step_container, fg_color="transparent")
        s_box.grid(row=0, column=i, padx=40)
        
        ctk.CTkLabel(s_box, text=judul, font=("Segoe UI", 13, "bold"), text_color="#111827").pack(pady=(0, 3))
        ctk.CTkLabel(s_box, text=sub, font=("Segoe UI", 11), text_color="#6B7280", wraplength=140).pack()

    app.mainloop()

if __name__ == "__main__":
    login_page()