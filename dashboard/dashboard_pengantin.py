import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import os
from datetime import datetime, date
import calendar

PRIMARY   = "#064E3B"
SECONDARY = "#149060"

def _header(parent, title, subtitle=""):
    h = ctk.CTkFrame(parent, fg_color="transparent")
    h.pack(fill="x", padx=30, pady=(20, 4))
    ctk.CTkLabel(h, text=title, font=("Segoe UI", 22, "bold"), text_color="#111827").pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(h, text=subtitle, font=("Segoe UI", 12), text_color="#6B7280").pack(anchor="w")
    ctk.CTkFrame(parent, height=1, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(6,0))

# ── Helper: ambil data pendaftaran terakhir milik nik_user ────
def _ambil_data_user(nik_user, path_db):
    """Return data[] terakhir milik nik_user, atau None."""
    hasil = None
    if os.path.exists(path_db):
        with open(path_db,"r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 10 and d[1] == nik_user:
                    hasil = d
    return hasil

# ── Panel: Dashboard ──────────────────────────────────────────
def _panel_dashboard(parent, nik_user, path_db):
    _header(parent, "Dashboard", "Ringkasan status pendaftaran Anda")
    data = _ambil_data_user(nik_user, path_db)
    status = data[9] if data else "Belum ada pendaftaran"
    nama_p = data[2] if data else "-"

    warna = {"Menunggu":"#F59E0B","Terverifikasi":"#3B82F6",
             "Selesai":"#10B981","Dibatalkan":"#EF4444"}
    w = warna.get(status,"#9CA3AF")

    card = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=12,
                        border_width=1, border_color="#D1FAE5")
    card.pack(fill="x", padx=30, pady=16)
    ctk.CTkLabel(card, text="Status Pendaftaran Terakhir",
                 font=("Segoe UI",13), text_color="#6B7280").pack(pady=(18,4))
    ctk.CTkLabel(card, text=status,
                 font=("Segoe UI",28,"bold"), text_color=w).pack(pady=4)
    ctk.CTkLabel(card, text=f"Nama Suami: {nama_p}",
                 font=("Segoe UI",12), text_color="#374151").pack(pady=(0,18))

    info = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=10,
                        border_width=1, border_color="#E5E7EB")
    info.pack(fill="x", padx=30, pady=6)
    ctk.CTkLabel(info, text="Panduan Cepat:",
                 font=("Segoe UI",14,"bold"), text_color=PRIMARY).pack(anchor="w", padx=20, pady=(14,4))
    tips = [
        "📝  Daftar Nikah  →  Isi formulir (hanya bisa jika belum punya pendaftaran aktif)",
        "✏️   Ubah / Batalkan  →  Hanya bisa jika status masih Menunggu",
        "🔍  Cek Status  →  Pantau progress verifikasi admin",
        "📄  Cetak Bukti  →  Tersedia jika status sudah Selesai",
    ]
    for t in tips:
        ctk.CTkLabel(info, text=t, font=("Segoe UI",12), text_color="#374151").pack(anchor="w", padx=30, pady=2)
    ctk.CTkFrame(info, height=1, fg_color="transparent").pack(pady=8)


# ── Widget: NIK Entry dengan validasi inline ───────────────────
class NIKEntry(ctk.CTkFrame):
    """Entry NIK dengan indikator validasi real-time (✓ / pesan error)."""
    def __init__(self, parent, placeholder="16 digit NIK", **kwargs):
        super().__init__(parent, fg_color="transparent")
        self._var = tk.StringVar()
        self._var.trace_add("write", self._validate)

        self.entry = ctk.CTkEntry(
            self, textvariable=self._var,
            placeholder_text=placeholder,
            height=38, width=300,
            border_width=2, border_color="#2E7D32",
            **kwargs
        )
        self.entry.pack(side="left")

        self.lbl = ctk.CTkLabel(self, text="", font=("Segoe UI", 11),
                                 text_color="#9CA3AF", width=210, anchor="w")
        self.lbl.pack(side="left", padx=(8, 0))

    def _validate(self, *_):
        val = self._var.get()
        if val == "":
            self.entry.configure(border_color="#2E7D32")
            self.lbl.configure(text="", text_color="#9CA3AF")
        elif not val.isdigit():
            self.entry.configure(border_color="#EF4444")
            self.lbl.configure(text="✗ Hanya boleh angka", text_color="#EF4444")
        elif len(val) < 16:
            self.entry.configure(border_color="#F59E0B")
            self.lbl.configure(text=f"⚠ Masih {16 - len(val)} digit lagi ({len(val)}/16)",
                                text_color="#D97706")
        elif len(val) == 16:
            self.entry.configure(border_color="#10B981")
            self.lbl.configure(text="✓ NIK valid (16 digit)", text_color="#10B981")
        else:
            self.entry.configure(border_color="#EF4444")
            self.lbl.configure(text=f"✗ Terlalu panjang ({len(val)}/16)", text_color="#EF4444")

    def get(self):
        return self._var.get().strip()

    def set(self, val):
        self._var.set(val)

    def delete(self, a, b):
        self._var.set("")

    def insert(self, idx, val):
        self._var.set(val)


# ── Widget: Kalender Popup ──────────────────────────────────────
class KalenderPopup(ctk.CTkToplevel):
    """Mini calendar picker yang muncul sebagai popup."""
    def __init__(self, parent, callback, min_date=None):
        super().__init__(parent)
        self.callback  = callback
        self.min_date  = min_date or date.today()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="white")

        today = date.today()
        self.year  = today.year
        self.month = today.month
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        PRIMARY = "#064E3B"
        HOVER   = "#149060"

        nav = tk.Frame(self, bg=PRIMARY)
        nav.pack(fill="x")

        tk.Button(nav, text="‹", bg=PRIMARY, fg="white", bd=0,
                  font=("Segoe UI", 14, "bold"), activebackground=HOVER,
                  activeforeground="white",
                  command=self._prev_month).pack(side="left", padx=8, pady=6)

        bulan_nama = ["Januari","Februari","Maret","April","Mei","Juni",
                      "Juli","Agustus","September","Oktober","November","Desember"]
        tk.Label(nav, text=f"{bulan_nama[self.month-1]} {self.year}",
                 bg=PRIMARY, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", expand=True)

        tk.Button(nav, text="›", bg=PRIMARY, fg="white", bd=0,
                  font=("Segoe UI", 14, "bold"), activebackground=HOVER,
                  activeforeground="white",
                  command=self._next_month).pack(side="right", padx=8, pady=6)

        days_frame = tk.Frame(self, bg="#F0FDF4")
        days_frame.pack(fill="x")
        for hari in ["Sen","Sel","Rab","Kam","Jum","Sab","Min"]:
            tk.Label(days_frame, text=hari, bg="#F0FDF4", fg="#374151",
                     font=("Segoe UI", 9, "bold"), width=4).pack(side="left", padx=1, pady=4)

        grid = tk.Frame(self, bg="white")
        grid.pack(padx=4, pady=4)

        cal = calendar.monthcalendar(self.year, self.month)
        today = date.today()
        for week in cal:
            row = tk.Frame(grid, bg="white")
            row.pack()
            for day in week:
                if day == 0:
                    tk.Label(row, text="", width=4, bg="white").pack(side="left", padx=1, pady=1)
                else:
                    d = date(self.year, self.month, day)
                    is_past     = d < self.min_date
                    is_today    = d == today
                    fg   = "#9CA3AF" if is_past else ("#064E3B" if is_today else "#111827")
                    bg   = "#F0FDF4" if is_today else "white"
                    font = ("Segoe UI", 9, "bold") if is_today else ("Segoe UI", 9)
                    btn = tk.Button(row, text=str(day), width=3,
                                    fg=fg, bg=bg, bd=0, font=font,
                                    activebackground="#D1FAE5",
                                    state="disabled" if is_past else "normal",
                                    command=lambda d=d: self._pilih(d))
                    btn.pack(side="left", padx=1, pady=1)

        tk.Button(self, text="Hari Ini", bg="#10B981", fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, pady=6,
                  activebackground="#059669", activeforeground="white",
                  command=lambda: self._pilih(date.today())).pack(fill="x", padx=4, pady=(0,4))

    def _prev_month(self):
        if self.month == 1: self.month = 12; self.year -= 1
        else: self.month -= 1
        self._build()

    def _next_month(self):
        if self.month == 12: self.month = 1; self.year += 1
        else: self.month += 1
        self._build()

    def _pilih(self, d):
        self.callback(d.strftime("%Y-%m-%d"))
        self.destroy()


# ── Widget: Date Picker Field ────────────────────────────────────
class DatePickerField(ctk.CTkFrame):
    """Tampilan tanggal dengan tombol kalender popup dan auto-fill hari ini."""
    def __init__(self, parent, default_val=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self._val = tk.StringVar(value=default_val or date.today().strftime("%Y-%m-%d"))

        self.entry = ctk.CTkEntry(
            self, textvariable=self._val,
            height=38, width=220,
            border_width=2, border_color="#2E7D32",
            font=("Segoe UI", 13),
            state="readonly",
        )
        self.entry.pack(side="left")

        ctk.CTkButton(
            self, text="📅", width=40, height=38,
            fg_color="#064E3B", hover_color="#149060",
            font=("Segoe UI", 15),
            command=self._buka_kalender
        ).pack(side="left", padx=(4, 0))

        ctk.CTkLabel(self, text="(klik 📅 untuk pilih tanggal)",
                     font=("Segoe UI", 10), text_color="#9CA3AF").pack(side="left", padx=(8, 0))

    def _buka_kalender(self):
        try:
            current = datetime.strptime(self._val.get(), "%Y-%m-%d").date()
        except ValueError:
            current = date.today()
        popup = KalenderPopup(self, callback=self._set_val, min_date=date.today())
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        popup.geometry(f"+{x}+{y}")

    def _set_val(self, val):
        self._val.set(val)

    def get(self):
        return self._val.get().strip()

    def set(self, val):
        self._val.set(val)


# ── Widget: Time Picker ──────────────────────────────────────────
class TimePicker(ctk.CTkFrame):
    """Jam + menit dipilih lewat dropdown — tampilan bersih tanpa tombol panah/preset."""
    def __init__(self, parent, default="09:00", **kwargs):
        super().__init__(parent, fg_color="transparent")

        jam_def, mnt_def = default.split(":") if ":" in default else ("09", "00")

        jam_values = [f"{h:02d}" for h in range(0, 24)]
        mnt_values = [f"{m:02d}" for m in range(0, 60, 5)]

        self.cb_jam = ctk.CTkComboBox(
            self, values=jam_values, width=70, height=38,
            font=("Segoe UI", 13, "bold"),
            border_color="#2E7D32", border_width=2,
            button_color="#064E3B", button_hover_color="#149060",
            dropdown_hover_color="#D1FAE5",
            justify="center",
        )
        self.cb_jam.set(jam_def.zfill(2) if jam_def.zfill(2) in jam_values else "09")
        self.cb_jam.pack(side="left")

        ctk.CTkLabel(self, text=":", font=("Segoe UI", 16, "bold"),
                     text_color="#064E3B").pack(side="left", padx=6)

        # Bulatkan menit default ke kelipatan 5 terdekat yang tersedia di dropdown
        mnt_def_2 = mnt_def.zfill(2)
        if mnt_def_2 not in mnt_values:
            mnt_def_2 = f"{round(int(mnt_def) / 5) * 5 % 60:02d}"

        self.cb_mnt = ctk.CTkComboBox(
            self, values=mnt_values, width=70, height=38,
            font=("Segoe UI", 13, "bold"),
            border_color="#2E7D32", border_width=2,
            button_color="#064E3B", button_hover_color="#149060",
            dropdown_hover_color="#D1FAE5",
            justify="center",
        )
        self.cb_mnt.set(mnt_def_2 if mnt_def_2 in mnt_values else "00")
        self.cb_mnt.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(self, text="WIB", font=("Segoe UI", 12, "bold"),
                     text_color="#064E3B").pack(side="left", padx=(8, 0))

    def get(self):
        return f"{self.cb_jam.get()}:{self.cb_mnt.get()}"

    def set(self, val):
        if ":" in val:
            h, m = val.split(":")
            self.cb_jam.set(h.zfill(2))
            self.cb_mnt.set(m.zfill(2))


# ── Panel: Daftar / Ubah Data ─────────────────────────────────
def _panel_daftar(parent, nik_user, path_db, path_pengguna):
    data_existing = _ambil_data_user(nik_user, path_db)
    status_existing = data_existing[9] if data_existing else None

    # ── Kasus: sudah Selesai atau Terverifikasi → form dikunci
    if status_existing in ("Terverifikasi", "Selesai"):
        _header(parent, "Daftar Nikah", "Formulir pendaftaran pernikahan")
        kunci = ctk.CTkFrame(parent, fg_color="#FFF7ED", corner_radius=12,
                             border_width=1, border_color="#FED7AA")
        kunci.pack(fill="x", padx=30, pady=20)
        icon = "✅" if status_existing == "Selesai" else "🔒"
        ctk.CTkLabel(kunci, text=f"{icon}  Pendaftaran {status_existing}",
                     font=("Segoe UI",18,"bold"),
                     text_color="#10B981" if status_existing=="Selesai" else "#185FA5").pack(pady=(20,6))
        ctk.CTkLabel(kunci,
                     text="Form pendaftaran dikunci karena pendaftaran Anda sudah diproses oleh admin.\n"
                          "Silakan cek status atau cetak bukti pernikahan di menu Cek Status.",
                     font=("Segoe UI",12), text_color="#374151",
                     wraplength=700).pack(pady=(0,20))
        return

    # ── Kasus: sudah Menunggu → tampilkan form edit + batalkan
    mode_edit = (status_existing == "Menunggu")
    if mode_edit:
        _header(parent, "Ubah Data Pendaftaran", "Edit data pendaftaran yang masih menunggu verifikasi")
    else:
        _header(parent, "Daftar Nikah", "Isi formulir pendaftaran pernikahan")

    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(expand=True, fill="both", padx=30, pady=10)

    # Banner info jika mode edit
    if mode_edit:
        banner = ctk.CTkFrame(scroll, fg_color="#FFF7ED", corner_radius=8,
                              border_width=1, border_color="#FED7AA")
        banner.pack(fill="x", pady=(0,10), padx=10)
        ctk.CTkLabel(banner,
                     text=f"⚠️  Pendaftaran {data_existing[0]} masih Menunggu verifikasi admin. "
                          "Anda dapat mengubah data atau membatalkan pendaftaran.",
                     font=("Segoe UI",12), text_color="#92400E",
                     wraplength=800).pack(padx=16, pady=12)

    form = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=12,
                        border_width=1, border_color="#E5E7EB")
    form.pack(fill="x", pady=8, padx=10)

    fields = {}
    def baris(label, key, placeholder="", val=""):
        r = ctk.CTkFrame(form, fg_color="transparent"); r.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(r, text=label, font=("Segoe UI",12,"bold"), width=180, anchor="w").pack(side="left")
        e = ctk.CTkEntry(r, placeholder_text=placeholder, height=38, width=420,
                         border_color="#2E7D32", border_width=2)
        if val: e.insert(0, val)
        e.pack(side="left")
        fields[key] = e
        return e

    def baris_nik(label, key, val=""):
        r = ctk.CTkFrame(form, fg_color="transparent"); r.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(r, text=label, font=("Segoe UI",12,"bold"), width=180, anchor="w").pack(side="left")
        w = NIKEntry(r, placeholder="16 digit NIK")
        if val: w.set(val)
        w.pack(side="left")
        fields[key] = w
        return w

    def baris_tanggal(label, key, val=""):
        r = ctk.CTkFrame(form, fg_color="transparent"); r.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(r, text=label, font=("Segoe UI",12,"bold"), width=180, anchor="w").pack(side="left")
        w = DatePickerField(r, default_val=val if val else None)
        w.pack(side="left")
        fields[key] = w
        return w

    def baris_jam(label, key, val=""):
        r = ctk.CTkFrame(form, fg_color="transparent"); r.pack(fill="x", padx=24, pady=6)
        ctk.CTkLabel(r, text=label, font=("Segoe UI",12,"bold"), width=180, anchor="w").pack(side="left")
        w = TimePicker(r, default=val if val else "09:00")
        w.pack(side="left")
        fields[key] = w
        return w

    # Prefill jika mode edit
    v = data_existing if mode_edit else [""]*12

    ctk.CTkLabel(form, text="Data Calon Suami",
                 font=("Segoe UI",15,"bold"), text_color=PRIMARY).pack(anchor="w", padx=24, pady=(18,4))
    baris_nik("NIK Suami *",    "nik_suami",  v[1] if mode_edit else "")
    baris("Nama Suami *",   "nama_suami", "Nama lengkap sesuai KTP", v[2] if mode_edit else "")

    ctk.CTkFrame(form, height=1, fg_color="#E5E7EB").pack(fill="x", padx=24, pady=8)
    ctk.CTkLabel(form, text="Data Calon Istri",
                 font=("Segoe UI",15,"bold"), text_color=PRIMARY).pack(anchor="w", padx=24, pady=(4,4))
    baris_nik("NIK Istri *",    "nik_istri",  v[3] if mode_edit else "")
    baris("Nama Istri *",   "nama_istri", "Nama lengkap sesuai KTP", v[4] if mode_edit else "")

    ctk.CTkFrame(form, height=1, fg_color="#E5E7EB").pack(fill="x", padx=24, pady=8)
    ctk.CTkLabel(form, text="Data Wali & Akad",
                 font=("Segoe UI",15,"bold"), text_color=PRIMARY).pack(anchor="w", padx=24, pady=(4,4))
    baris("Nama Wali *",      "wali",    "Nama wali nikah",          v[5] if mode_edit else "")
    baris_tanggal("Tanggal Nikah *",  "tanggal", v[6] if mode_edit else "")
    baris_jam("Jam Akad *",       "jam",     v[7] if mode_edit else "")
    baris("Lokasi *",         "lokasi",  "Nama masjid/gedung/rumah", v[8] if mode_edit else "")

    def generate_id():
        existing = []
        if os.path.exists(path_db):
            with open(path_db,"r") as f:
                for line in f:
                    d = line.strip().split("|")
                    if d[0].startswith("REG"):
                        try: existing.append(int(d[0][3:]))
                        except: pass
        nxt = max(existing)+1 if existing else 1
        return f"REG{nxt:03d}"

    def kirim():
        vals = {k: w.get().strip() for k,w in fields.items()}
        if any(not v for v in vals.values()):
            messagebox.showerror("Error","Semua field wajib diisi!"); return

        if not vals["nik_suami"].isdigit() or len(vals["nik_suami"]) != 16:
            messagebox.showerror("Error","NIK Suami harus tepat 16 digit angka!"); return
        if not vals["nik_istri"].isdigit() or len(vals["nik_istri"]) != 16:
            messagebox.showerror("Error","NIK Istri harus tepat 16 digit angka!"); return
        if vals["nik_suami"] == vals["nik_istri"]:
            messagebox.showerror("Error","NIK Suami dan Istri tidak boleh sama!"); return

        try:
            tgl_obj = datetime.strptime(vals["tanggal"], "%Y-%m-%d").date()
            if tgl_obj < date.today():
                messagebox.showerror("Error","Tanggal tidak boleh di masa lampau!"); return
        except ValueError:
            messagebox.showerror("Error","Format tanggal tidak valid!"); return

        if mode_edit:
            # Update baris yang ada
            id_reg = data_existing[0]
            with open(path_db,"r") as f: lines = f.readlines()
            with open(path_db,"w") as f:
                for line in lines:
                    d = line.strip().split("|")
                    if d[0] == id_reg:
                        d[1]=vals["nik_suami"]; d[2]=vals["nama_suami"]
                        d[3]=vals["nik_istri"]; d[4]=vals["nama_istri"]
                        d[5]=vals["wali"]; d[6]=vals["tanggal"]
                        d[7]=vals["jam"];  d[8]=vals["lokasi"]
                        f.write("|".join(d)+"\n")
                    else: f.write(line)
            messagebox.showinfo("Sukses","Data pendaftaran berhasil diperbarui!")
            for w in parent.winfo_children(): w.destroy()
            _panel_daftar(parent, nik_user, path_db, path_pengguna)
            return
        else:
            # Cek duplikat
            if os.path.exists(path_db):
                with open(path_db,"r") as f:
                    for line in f:
                        d = line.strip().split("|")
                        if len(d) >= 10 and d[1] == vals["nik_suami"] and d[9] not in ("Dibatalkan",):
                            messagebox.showerror("Error",
                                "NIK suami ini sudah memiliki pendaftaran aktif.\n"
                                "Cek status di menu Cek Status."); return
            id_reg = generate_id()
            row = "|".join([id_reg, vals["nik_suami"], vals["nama_suami"],
                            vals["nik_istri"], vals["nama_istri"], vals["wali"],
                            vals["tanggal"], vals["jam"], vals["lokasi"],
                            "Menunggu", "-"])
            with open(path_db,"a") as f: f.write(row+"\n")
            messagebox.showinfo("Sukses",
                f"Pendaftaran berhasil!\nID Anda: {id_reg}\nStatus: Menunggu Verifikasi Admin")
            for w in parent.winfo_children(): w.destroy()
            _panel_daftar(parent, nik_user, path_db, path_pengguna)
            return

    def batalkan_sendiri():
        if not mode_edit: return
        if not messagebox.askyesno("Konfirmasi",
            f"Batalkan pendaftaran {data_existing[0]}?\n"
            "Tindakan ini tidak bisa dibatalkan."):
            return
        with open(path_db,"r") as f: lines = f.readlines()
        with open(path_db,"w") as f:
            for line in lines:
                d = line.strip().split("|")
                if d[0] == data_existing[0]:
                    d[9] = "Dibatalkan"; d[10] = "-"
                    while len(d) < 12: d.append("-")
                    d[11] = "Dibatalkan oleh Calon Pengantin"
                    f.write("|".join(d)+"\n")
                else: f.write(line)
        messagebox.showinfo("Sukses","Pendaftaran berhasil dibatalkan.")
        # Reload panel
        for w in parent.winfo_children(): w.destroy()
        _panel_daftar(parent, nik_user, path_db, path_pengguna)

    btn_bar = ctk.CTkFrame(form, fg_color="transparent")
    btn_bar.pack(pady=20)
    label_btn = "💾 Simpan Perubahan" if mode_edit else "📋 Kirim Pendaftaran"
    ctk.CTkButton(btn_bar, text=label_btn, height=44,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI",14,"bold"),
                  command=kirim).pack(side="left", padx=8)
    if mode_edit:
        ctk.CTkButton(btn_bar, text="❌ Batalkan Pendaftaran", height=44,
                      fg_color="#D32F2F", hover_color="#B71C1C",
                      font=("Segoe UI",13,"bold"),
                      command=batalkan_sendiri).pack(side="left", padx=8)


# ── Panel: Cek Status ─────────────────────────────────────────
def _panel_status(parent, nik_user, path_db, on_navigate=None):
    _header(parent, "Cek Status Pendaftaran", "Status terkini pendaftaran Anda dari sistem admin")

    status_card = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=12,
                               border_width=1, border_color="#D1FAE5", height=120)
    status_card.pack(fill="x", padx=30, pady=12)
    status_card.pack_propagate(False)

    # Baris atas: badge status + detail nama (horizontal, sejajar)
    top_row = ctk.CTkFrame(status_card, fg_color="transparent")
    top_row.pack(fill="x", padx=20, pady=(14, 4))

    lbl_status   = ctk.CTkLabel(top_row, text="Memuat...",
                                 font=("Segoe UI",20,"bold"), text_color="#9CA3AF", anchor="w")
    lbl_status.pack(side="left")

    lbl_detail   = ctk.CTkLabel(top_row, text="", font=("Segoe UI",12), text_color="#374151", anchor="e")
    lbl_detail.pack(side="right")

    # Baris bawah: penghulu + tanggal (horizontal, sejajar)
    bottom_row = ctk.CTkFrame(status_card, fg_color="transparent")
    bottom_row.pack(fill="x", padx=20, pady=(0, 10))

    lbl_penghulu = ctk.CTkLabel(bottom_row, text="", font=("Segoe UI",11), text_color="#6B7280", anchor="w")
    lbl_penghulu.pack(side="left")

    lbl_waktu    = ctk.CTkLabel(bottom_row, text="", font=("Segoe UI",11), text_color="#6B7280", anchor="e")
    lbl_waktu.pack(side="right")

    # Tombol cetak bukti — hanya muncul jika Selesai
    btn_cetak_ref = {"btn": None}
    cetak_frame = ctk.CTkFrame(status_card, fg_color="transparent")
    cetak_frame.pack(pady=(0,8))

    ctk.CTkLabel(parent, text="Riwayat Pendaftaran",
                 font=("Segoe UI",14,"bold"), text_color=PRIMARY).pack(anchor="w", padx=30, pady=(4,2))
    tbl_frame = ctk.CTkFrame(parent, corner_radius=8)
    tbl_frame.pack(expand=True, fill="both", padx=30, pady=(0,6))

    cols = ("id","nama_suami","nama_istri","tanggal","jam","lokasi","status","penghulu","keterangan")
    col_labels = ("ID","Nama Suami","Nama Istri","Tgl Nikah","Jam","Lokasi","Status","Penghulu","Keterangan")
    tree = ttk.Treeview(tbl_frame, columns=cols, show="headings")
    tree.tag_configure("menunggu",     foreground="#D97706")
    tree.tag_configure("terverifikasi",foreground="#185FA5")
    tree.tag_configure("selesai",      foreground="#149060")
    tree.tag_configure("dibatalkan",   foreground="#DC2626")
    col_widths = [70,130,130,95,55,130,110,130,160]
    for col, lbl, w in zip(cols, col_labels, col_widths):
        tree.heading(col, text=lbl); tree.column(col, width=w, anchor="center")
    sbx = ttk.Scrollbar(tbl_frame, orient="horizontal", command=tree.xview)
    tree.configure(xscroll=sbx.set)
    sbx.pack(side="bottom", fill="x"); tree.pack(expand=True, fill="both")

    last_modified = {"val": 0}
    pending_after = {"id": None}
    data_terakhir = {"d": None}

    warna = {"Menunggu":"#D97706","Terverifikasi":"#185FA5",
             "Selesai":"#149060","Dibatalkan":"#DC2626"}

    def cetak_bukti():
        d = data_terakhir["d"]
        if not d or d[9] != "Selesai":
            messagebox.showwarning("Peringatan","Bukti hanya bisa dicetak jika status Selesai."); return
        _cetak_bukti_pdf(d)

    def muat(force=False):
        try:
            mtime = os.path.getmtime(path_db) if os.path.exists(path_db) else 0
        except: mtime = 0
        if not force and mtime == last_modified["val"]: return
        last_modified["val"] = mtime

        for i in tree.get_children(): tree.delete(i)
        data_user = []
        if os.path.exists(path_db):
            with open(path_db,"r") as f:
                for line in f:
                    d = line.strip().split("|")
                    if len(d) >= 10 and d[1] == nik_user:
                        data_user.append(d)

        if data_user:
            terakhir = data_user[-1]
            data_terakhir["d"] = terakhir
            st = terakhir[9]
            w  = warna.get(st,"#9CA3AF")
            lbl_status.configure(text=st, text_color=w)
            lbl_detail.configure(text=f"📋 ID: {terakhir[0]}  |  {terakhir[2]} & {terakhir[4]}")
            ph = terakhir[10] if len(terakhir)>10 and terakhir[10]!="-" else "Belum ditentukan"
            lbl_penghulu.configure(text=f"👤 Penghulu: {ph}")
            ket = terakhir[11] if len(terakhir)>11 else ""
            if ket and ket!="-":
                lbl_waktu.configure(text=f"ℹ️  Keterangan: {ket}")
            else:
                lbl_waktu.configure(text=f"📅 Tanggal Nikah: {terakhir[6]} pukul {terakhir[7]}")

            # Tampilkan/sembunyikan tombol cetak
            for w2 in cetak_frame.winfo_children(): w2.destroy()
            if st == "Selesai":
                ctk.CTkButton(cetak_frame, text="📄 Cetak Bukti Pernikahan (PDF)",
                              height=40, fg_color="#10B981", hover_color="#059669",
                              font=("Segoe UI",13,"bold"),
                              command=cetak_bukti).pack()
        else:
            data_terakhir["d"] = None
            lbl_status.configure(text="Belum Ada Pendaftaran", text_color="#9CA3AF")
            lbl_detail.configure(text="Silakan daftar lewat menu Daftar Nikah")
            lbl_penghulu.configure(text=""); lbl_waktu.configure(text="")
            for w2 in cetak_frame.winfo_children(): w2.destroy()

        for d in data_user:
            ph  = d[10] if len(d)>10 else "-"
            ket = d[11] if len(d)>11 else "-"
            st  = d[9]
            tag = st.lower().replace(" ","_")
            tree.insert("","end",
                        values=(d[0],d[2],d[4],d[6],d[7],d[8],st,ph,ket),
                        tags=(tag,))

    def auto_refresh():
        muat()
        if pending_after["id"]: parent.after_cancel(pending_after["id"])
        pending_after["id"] = parent.after(3000, auto_refresh)

    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=30, pady=(0,4))
    ctk.CTkLabel(bar, text="🔄  Status otomatis diperbarui setiap 3 detik",
                 font=("Segoe UI",11), text_color="#9CA3AF").pack(side="left")

    auto_refresh()
    def on_destroy(e):
        if pending_after["id"]: parent.after_cancel(pending_after["id"])
    parent.bind("<Destroy>", on_destroy)


# ── Cetak Bukti PDF ───────────────────────────────────────────
def _cetak_bukti_pdf(data):
    from tkinter import filedialog
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_file = f"Bukti_Nikah_{data[0]}_{now}.pdf"
    save_path = filedialog.asksaveasfilename(
        title="Simpan Bukti Pernikahan",
        defaultextension=".pdf",
        filetypes=[("PDF Files","*.pdf"),("All Files","*.*")],
        initialfile=nama_file
    )
    if not save_path: return
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(save_path, pagesize=A4,
                                topMargin=2*cm, bottomMargin=2*cm,
                                leftMargin=2.5*cm, rightMargin=2.5*cm)
        hijau_tua  = colors.HexColor("#064E3B")
        hijau_muda = colors.HexColor("#D1FAE5")
        abu        = colors.HexColor("#6B7280")
        styles     = getSampleStyleSheet()

        s_judul = ParagraphStyle("j", parent=styles["Normal"], fontSize=18,
                                  fontName="Helvetica-Bold", textColor=hijau_tua,
                                  alignment=TA_CENTER, spaceAfter=4)
        s_sub   = ParagraphStyle("s", parent=styles["Normal"], fontSize=11,
                                  fontName="Helvetica", textColor=abu,
                                  alignment=TA_CENTER, spaceAfter=2)
        s_body  = ParagraphStyle("b", parent=styles["Normal"], fontSize=11,
                                  fontName="Helvetica", textColor=colors.HexColor("#111827"),
                                  alignment=TA_LEFT, leading=18)
        s_bold  = ParagraphStyle("bb", parent=s_body, fontName="Helvetica-Bold")

        id_reg   = data[0]
        nik_s    = data[1] if len(data)>1 else "-"
        nama_s   = data[2] if len(data)>2 else "-"
        nik_i    = data[3] if len(data)>3 else "-"
        nama_i   = data[4] if len(data)>4 else "-"
        wali     = data[5] if len(data)>5 else "-"
        tgl      = data[6] if len(data)>6 else "-"
        jam      = data[7] if len(data)>7 else "-"
        lokasi   = data[8] if len(data)>8 else "-"
        penghulu = data[10] if len(data)>10 and data[10]!="-" else "—"
        catatan  = data[11] if len(data)>11 and data[11]!="-" else "—"

        story = [
            Paragraph("BUKTI PENCATATAN PERNIKAHAN", s_judul),
            Paragraph("Kantor Urusan Agama (KUA) — Sistem Layanan KUA Digital", s_sub),
            Spacer(1, 0.3*cm),
            HRFlowable(width="100%", thickness=2, color=hijau_tua),
            Spacer(1, 0.4*cm),
        ]

        # Badge No. Registrasi
        reg_tbl = Table([[f"No. Registrasi:  {id_reg}"]],
                        colWidths=[13*cm])
        reg_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),hijau_muda),
            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),13),
            ("TEXTCOLOR",(0,0),(-1,-1),hijau_tua),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("TOPPADDING",(0,0),(-1,-1),10),
            ("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("ROUNDEDCORNERS",[6]),
        ]))
        story += [reg_tbl, Spacer(1,0.5*cm)]

        # Tabel data
        data_tbl = [
            ["Nama Suami",   nama_s,  "NIK Suami",   nik_s],
            ["Nama Istri",   nama_i,  "NIK Istri",   nik_i],
            ["Wali Nikah",   wali,    "Penghulu",     penghulu],
            ["Tanggal Nikah",tgl,     "Jam Akad",     jam],
            ["Lokasi",       lokasi,  "Status",       "SELESAI ✓"],
        ]
        col_w = [3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm]
        main_tbl = Table(data_tbl, colWidths=col_w)
        main_tbl.setStyle(TableStyle([
            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
            ("FONTNAME",(1,0),(1,-1),"Helvetica"),
            ("FONTNAME",(3,0),(3,-1),"Helvetica"),
            ("FONTSIZE",(0,0),(-1,-1),11),
            ("TEXTCOLOR",(0,0),(0,-1),hijau_tua),
            ("TEXTCOLOR",(2,0),(2,-1),hijau_tua),
            ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#E5E7EB")),
            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F0FDF4")),
            ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#F0FDF4")),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            # Warna hijau untuk status selesai
            ("TEXTCOLOR",(3,4),(3,4),colors.HexColor("#10B981")),
            ("FONTNAME",(3,4),(3,4),"Helvetica-Bold"),
        ]))
        story += [main_tbl, Spacer(1,0.5*cm)]

        if catatan != "—":
            story += [
                Paragraph(f"Catatan Penghulu: {catatan}", s_body),
                Spacer(1,0.3*cm),
            ]

        story += [
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")),
            Spacer(1,0.5*cm),
        ]

        # Area tanda tangan
        ttd_data = [
            ["Mengetahui,", "", "Dicetak oleh Sistem,"],
            ["", "", ""],
            ["", "", ""],
            ["( Kepala KUA )", "",
             f"Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}"],
        ]
        ttd_tbl = Table(ttd_data, colWidths=[6*cm,6*cm,6*cm])
        ttd_tbl.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
            ("FONTNAME",(0,0),(0,0),"Helvetica-Bold"),
            ("FONTNAME",(2,0),(2,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),10),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("LINEBELOW",(0,2),(0,2),0.8,hijau_tua),
            ("LINEBELOW",(2,2),(2,2),0.8,hijau_tua),
            ("TOPPADDING",(0,0),(-1,-1),4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(ttd_tbl)
        story += [
            Spacer(1,0.4*cm),
            HRFlowable(width="100%", thickness=1, color=hijau_tua),
            Paragraph("Dokumen ini dicetak secara digital dari Sistem Layanan KUA Digital. "
                      "Sah sebagai bukti pencatatan pernikahan.",
                      ParagraphStyle("ft", parent=styles["Normal"], fontSize=8,
                                     textColor=abu, alignment=TA_CENTER)),
        ]

        doc.build(story)
        messagebox.showinfo("Sukses",f"Bukti pernikahan berhasil disimpan:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error PDF",f"Gagal membuat PDF:\n{e}")


# ── Panel: Info Layanan ───────────────────────────────────────
def _panel_info(parent):
    _header(parent, "Informasi Layanan", "Syarat, biaya & jam operasional KUA")
    path = "database/informasi_layanan.txt"
    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(expand=True, fill="both", padx=30, pady=10)

    def seksi(title, konten_list, icon="📌"):
        frame = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=10,
                             border_width=1, border_color="#E5E7EB")
        frame.pack(fill="x", pady=8)
        ctk.CTkLabel(frame, text=f"{icon}  {title}",
                     font=("Segoe UI",14,"bold"), text_color=PRIMARY).pack(anchor="w", padx=20, pady=(14,6))
        for item in konten_list:
            ctk.CTkLabel(frame, text=item, font=("Segoe UI",12),
                         text_color="#374151", anchor="w",
                         wraplength=800).pack(anchor="w", padx=30, pady=2)
        ctk.CTkFrame(frame, height=1, fg_color="transparent").pack(pady=6)

    syarat=[]; biaya=[]; jam=[]; kontak=[]
    if os.path.exists(path):
        with open(path,"r") as f:
            for line in f:
                if "|" in line:
                    kat, isi = line.strip().split("|",1)
                    if kat=="SYARAT":   syarat.append(isi)
                    elif kat=="BIAYA":  biaya.append(isi)
                    elif kat=="JAMKERJA": jam.append(isi)
                    elif kat=="KONTAK": kontak.append(isi)

    if syarat:  seksi("Persyaratan Dokumen", syarat,  "📋")
    if biaya:   seksi("Informasi Biaya",     biaya,   "💰")
    if jam:     seksi("Jam Operasional KUA", jam,     "🕐")
    if kontak:  seksi("Kontak KUA",          kontak,  "📞")


# ── MAIN ─────────────────────────────────────────────────────
def dashboard_pengantin(nik_user="", nama_user="Pengantin"):
    from assets.sidebar import buat_sidebar

    app = ctk.CTk()
    app.after(0, lambda: app.state("zoomed"))
    app.title("Sistem Layanan Administrasi Nikah KUA")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    path_db      = "database/pendaftaran.txt"
    path_pengguna= "database/pengguna.txt"

    MENU = [
        ("dashboard","Dashboard"),
        ("daftar",   "Daftar Nikah"),
        ("status",   "Cek Status"),
        ("info",     "Info Layanan"),
    ]

    content_ref  = {"frame": None}
    btn_refs_ref = {"refs": {}}

    def tampil_konten(key):
        if content_ref["frame"]: content_ref["frame"].destroy()
        cf = ctk.CTkFrame(main_area, fg_color="white", corner_radius=0)
        cf.pack(expand=True, fill="both")
        content_ref["frame"] = cf
        for k, btn in btn_refs_ref["refs"].items():
            is_act = (k == key)
            btn.configure(
                fg_color="white" if is_act else "transparent",
                text_color=PRIMARY if is_act else "white",
                font=("Segoe UI",13,"bold" if is_act else "normal"),
                hover_color="#e8f5f0" if is_act else "#0D6342",
            )
        if key=="dashboard": _panel_dashboard(cf, nik_user, path_db)
        elif key=="daftar":  _panel_daftar(cf, nik_user, path_db, path_pengguna)
        elif key=="status":  _panel_status(cf, nik_user, path_db)
        elif key=="info":    _panel_info(cf)

    def logout():
        if messagebox.askyesno("Logout","Apakah Anda ingin keluar?"):
            app.destroy()
            from login import login_page
            login_page()

    outer = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
    outer.pack(expand=True, fill="both")
    sidebar, btn_refs = buat_sidebar(outer, "pengantin", nama_user, MENU,
                                     "dashboard", on_select=tampil_konten, on_logout=logout)
    btn_refs_ref["refs"] = btn_refs
    main_area = ctk.CTkFrame(outer, fg_color="white", corner_radius=0)
    main_area.pack(side="left", expand=True, fill="both")
    tampil_konten("dashboard")
    app.mainloop()
