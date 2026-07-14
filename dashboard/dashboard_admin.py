import customtkinter as ctk
from tkinter import messagebox, ttk
import os
from datetime import datetime

PRIMARY   = "#064E3B"
SECONDARY = "#149060"

#  Helper: header area konten
def _header(parent, title, subtitle=""):
    h = ctk.CTkFrame(parent, fg_color="transparent")
    h.pack(fill="x", padx=30, pady=(20, 4))
    ctk.CTkLabel(h, text=title, font=("Segoe UI", 22, "bold"),
                 text_color="#111827").pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(h, text=subtitle, font=("Segoe UI", 12),
                     text_color="#6B7280").pack(anchor="w")
    ctk.CTkFrame(parent, height=1, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(6,0))


#  Panel: Dashboard (ringkasan statistik)
def _panel_dashboard(parent, username, path_db):
    _header(parent, "Dashboard", "Ringkasan data pendaftaran nikah")

    counts = {"Menunggu": 0, "Terverifikasi": 0, "Selesai": 0, "Dibatalkan": 0}
    if os.path.exists(path_db):
        with open(path_db, "r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 10 and d[9] in counts:
                    counts[d[9]] += 1

    warna = {"Menunggu": "#F59E0B", "Terverifikasi": "#3B82F6",
             "Selesai": "#10B981", "Dibatalkan": "#EF4444"}

    stat_frame = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=10)
    stat_frame.pack(fill="x", padx=30, pady=16)
    inner = ctk.CTkFrame(stat_frame, fg_color="transparent")
    inner.pack(pady=16)

    for i, (lbl, val) in enumerate(counts.items()):
        box = ctk.CTkFrame(inner, fg_color="white", corner_radius=10, width=150, height=80)
        box.grid(row=0, column=i, padx=12)
        box.grid_propagate(False)
        ctk.CTkLabel(box, text=str(val), font=("Segoe UI", 28, "bold"),
                     text_color=warna[lbl]).place(relx=0.5, rely=0.38, anchor="center")
        ctk.CTkLabel(box, text=lbl, font=("Segoe UI", 11),
                     text_color="#6B7280").place(relx=0.5, rely=0.78, anchor="center")

    # Info sambutan
    info = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=10,
                        border_width=1, border_color="#E5E7EB")
    info.pack(fill="x", padx=30, pady=8)
    ctk.CTkLabel(info, text=f"👋  Selamat datang, {username}!",
                 font=("Segoe UI", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=20, pady=(14,4))
    ctk.CTkLabel(info,
                 text="Gunakan menu di sidebar untuk mengelola pendaftaran, penghulu, dan informasi layanan.",
                 font=("Segoe UI", 12), text_color="#374151").pack(anchor="w", padx=20, pady=(0,14))


# ─────────────────────────────────────────────────────────────
#  Panel: Verifikasi & Plotting Penghulu
# ─────────────────────────────────────────────────────────────
def _panel_verifikasi(parent, username, path_db):
    _header(parent, "Kelola Layanan", "Kelola data pendaftaran layanan")

    # ── Filter & Sort bar ──────────────────────────────────────
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=30, pady=(10, 4))

    ctk.CTkLabel(bar, text="Cari NIK:", font=("Segoe UI", 12)).pack(side="left", padx=(0,4))
    search_e = ctk.CTkEntry(bar, placeholder_text="Ketik NIK...", width=160, height=34)
    search_e.pack(side="left", padx=(0,12))

    ctk.CTkLabel(bar, text="Filter Status:", font=("Segoe UI", 12)).pack(side="left", padx=(0,4))
    status_cb = ctk.CTkComboBox(bar,
                                values=["Semua", "Menunggu", "Terverifikasi", "Selesai", "Dibatalkan"],
                                width=150, height=34)
    status_cb.set("Semua")
    status_cb.pack(side="left", padx=(0,10))

    ctk.CTkButton(bar, text="Terapkan", width=100, height=34,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  command=lambda: muat()).pack(side="left", padx=(0,6))
    ctk.CTkButton(bar, text="Reset", width=70, height=34,
                  fg_color="#6B7280",
                  command=lambda: [search_e.delete(0,"end"), status_cb.set("Semua"), muat()]).pack(side="left")

    # ── Sort radio ──────────────────────────────────────────────
    sort_bar = ctk.CTkFrame(parent, fg_color="transparent")
    sort_bar.pack(fill="x", padx=30, pady=(2,4))
    ctk.CTkLabel(sort_bar, text="Urutkan:", font=("Segoe UI", 12)).pack(side="left", padx=(0,6))
    import tkinter as tk
    sort_var = tk.StringVar(value="Waktu Terdekat")
    for opt in ["Waktu Terdekat", "Waktu Terjauh", "Status"]:
        ctk.CTkRadioButton(sort_bar, text=opt, variable=sort_var, value=opt,
                           font=("Segoe UI", 11),
                           command=lambda: muat()).pack(side="left", padx=6)

    # ── Tabel ───────────────────────────────────────────────────
    tbl_frame = ctk.CTkFrame(parent, corner_radius=8)
    tbl_frame.pack(expand=True, fill="both", padx=30, pady=6)

    cols = ("id","nik_suami","nama_suami","nik_istri","nama_istri","wali",
            "tanggal","jam","lokasi","status","penghulu")
    col_labels = ("ID","NIK Suami","Nama Suami","NIK Istri","Nama Istri","Wali",
                  "Tanggal","Jam","Lokasi","Status","Penghulu")
    tree = ttk.Treeview(tbl_frame, columns=cols, show="headings")
    tree.tag_configure("dibatalkan", foreground="red")
    tree.tag_configure("selesai",    foreground="#149060")
    tree.tag_configure("terverifikasi", foreground="#185FA5")

    col_widths = [70,110,120,110,120,110,85,55,120,100,120]
    for col, lbl, w in zip(cols, col_labels, col_widths):
        tree.heading(col, text=lbl)
        tree.column(col, width=w, anchor="center")

    sb_y = ttk.Scrollbar(tbl_frame, orient="vertical",   command=tree.yview)
    sb_x = ttk.Scrollbar(tbl_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=sb_y.set, xscroll=sb_x.set)
    sb_y.pack(side="right", fill="y")
    sb_x.pack(side="bottom", fill="x")
    tree.pack(expand=True, fill="both")

    # ── Action bar ──────────────────────────────────────────────
    act = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=8,
                       border_width=1, border_color="#E5E7EB")
    act.pack(fill="x", padx=30, pady=(6,12))

    act_left = ctk.CTkFrame(act, fg_color="transparent")
    act_left.pack(side="left", padx=12, pady=10)
    ctk.CTkLabel(act_left, text="Plotting Manual:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0,8))

    daftar_penghulu = ["-- Pilih Penghulu --"]
    if os.path.exists("database/penghulu.txt"):
        with open("database/penghulu.txt", "r") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    daftar_penghulu.append(f"{p[0]}-{p[1]}")

    penghulu_cb = ctk.CTkComboBox(act_left, values=daftar_penghulu, width=220, height=36)
    penghulu_cb.set("-- Pilih Penghulu --")
    penghulu_cb.pack(side="left", padx=(0,10))

    ctk.CTkButton(act_left, text="Verifikasi & Plot", height=36,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI", 12, "bold"),
                  command=lambda: proses_verifikasi()).pack(side="left", padx=4)

    ctk.CTkButton(act_left, text="Batalkan", height=36,
                  fg_color="#D32F2F", hover_color="#B71C1C",
                  font=("Segoe UI", 12, "bold"),
                  command=lambda: batalkan()).pack(side="left", padx=4)



    # ── Fungsi ──────────────────────────────────────────────────
    def muat():
        for i in tree.get_children(): tree.delete(i)
        if not os.path.exists(path_db): return
        rows = []
        with open(path_db, "r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 11: rows.append(d)

        nik_q = search_e.get().strip()
        if nik_q: rows = [r for r in rows if nik_q in r[1]]
        st = status_cb.get()
        if st != "Semua": rows = [r for r in rows if r[9] == st]

        def skey(r):
            try: return r[6]+r[7]
            except: return ""
        sv = sort_var.get()
        if sv == "Waktu Terdekat": rows.sort(key=skey)
        elif sv == "Waktu Terjauh": rows.sort(key=skey, reverse=True)
        else:
            urutan = {"Menunggu":0,"Terverifikasi":1,"Selesai":2,"Dibatalkan":3}
            rows.sort(key=lambda r: urutan.get(r[9], 9))

        for d in rows:
            tag = ""
            if d[9] == "Dibatalkan": tag = "dibatalkan"
            elif d[9] == "Selesai": tag = "selesai"
            elif d[9] == "Terverifikasi": tag = "terverifikasi"
            tree.insert("", "end", values=d[:11], tags=(tag,))

    def proses_verifikasi():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih data di tabel dulu!")
            return
        vals = tree.item(sel)['values']
        id_daftar, status_skrg = vals[0], vals[9]
        if status_skrg == "Dibatalkan":
            messagebox.showerror("Ditolak", "Pendaftaran sudah dibatalkan."); return
        if status_skrg in ("Terverifikasi", "Selesai"):
            messagebox.showinfo("Info", f"Status sudah: {status_skrg}"); return
        pilihan = penghulu_cb.get()
        if pilihan == "-- Pilih Penghulu --":
            messagebox.showwarning("Peringatan", "Pilih penghulu terlebih dahulu!"); return
        nama_penghulu = pilihan.split("-", 1)[1] if "-" in pilihan else pilihan
        with open(path_db, "r") as f: lines = f.readlines()
        with open(path_db, "w") as f:
            for line in lines:
                d = line.strip().split("|")
                if d[0] == str(id_daftar):
                    d[9] = "Terverifikasi"; d[10] = nama_penghulu
                    f.write("|".join(d) + "\n")
                else: f.write(line)
        messagebox.showinfo("Sukses", f"Pendaftaran {id_daftar} diverifikasi!\nPenghulu: {nama_penghulu}")
        muat()

    def batalkan():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih data di tabel dulu!"); return
        vals = tree.item(sel)['values']
        id_daftar, status_skrg = vals[0], vals[9]
        if status_skrg == "Dibatalkan":
            messagebox.showinfo("Info", "Sudah dibatalkan."); return
        if status_skrg in ("Selesai", "Terverifikasi"):
            messagebox.showerror("Tidak Bisa",
                f"Pendaftaran dengan status '{status_skrg}' tidak bisa dibatalkan oleh admin.\n"
                "Hanya pendaftaran berstatus 'Menunggu' yang bisa dibatalkan."); return

        top = parent.winfo_toplevel()
        dialog = ctk.CTkToplevel(top)
        dialog.title("Batalkan Pendaftaran")
        dialog.geometry("500x280")
        dialog.grab_set(); dialog.lift()
        ctk.CTkLabel(dialog, text="Batalkan Pendaftaran",
                     font=("Segoe UI", 16, "bold")).pack(pady=(20,5))
        ctk.CTkLabel(dialog, text=f"ID: {id_daftar}  |  {vals[2]} & {vals[4]}",
                     font=("Segoe UI", 12), text_color="gray").pack(pady=(0,10))
        ctk.CTkLabel(dialog, text="Alasan Pembatalan (opsional):",
                     font=("Segoe UI", 13)).pack(anchor="w", padx=30)
        alasan_box = ctk.CTkTextbox(dialog, width=440, height=90)
        alasan_box.pack(padx=30, pady=8)

        def konfirmasi():
            alasan = alasan_box.get("1.0","end").strip() or "Dibatalkan oleh Admin"
            with open(path_db, "r") as f: lines = f.readlines()
            with open(path_db, "w") as f:
                for line in lines:
                    d = line.strip().split("|")
                    if d[0] == str(id_daftar):
                        d[9] = "Dibatalkan"; d[10] = "-"
                        while len(d) < 11: d.append("-")
                        if len(d) > 11: d[11] = alasan
                        else: d.append(alasan)
                        f.write("|".join(d) + "\n")
                    else: f.write(line)
            messagebox.showinfo("Sukses", f"Pendaftaran {id_daftar} berhasil dibatalkan.")
            dialog.destroy(); muat()

        br = ctk.CTkFrame(dialog, fg_color="transparent"); br.pack(pady=10)
        ctk.CTkButton(br, text="Ya, Batalkan", fg_color="#D32F2F",
                      command=konfirmasi).pack(side="left", padx=8)
        ctk.CTkButton(br, text="Tidak", fg_color="gray",
                      command=dialog.destroy).pack(side="left", padx=8)

    muat()


# ─────────────────────────────────────────────────────────────
#  Panel: Kelola Penghulu  (UI baru)
# ─────────────────────────────────────────────────────────────
def _panel_penghulu(parent, username):
    import tkinter as tk
    from tkinter import ttk as tkttk

    _header(parent, "Data Penghulu", "Kelola data penghulu aktif")

    PATH_P  = "database/penghulu.txt"
    PATH_DB = "database/pendaftaran.txt"

    def status_penghulu(nama_p):
        if os.path.exists(PATH_DB):
            with open(PATH_DB, "r") as f:
                for line in f:
                    d = line.strip().split("|")
                    if len(d) >= 11 and d[10] == nama_p and d[9] == "Terverifikasi":
                        return "Sedang Tugas"
        return "Tersedia"

    def hitung_stats():
        total = aktif = tugas = 0
        if os.path.exists(PATH_P):
            with open(PATH_P, "r") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) < 2: continue
                    total += 1
                    st = status_penghulu(p[1])
                    if st == "Tersedia":   aktif += 1
                    else:                  tugas += 1
        return total, aktif, tugas

    # ── AREA KONTEN utama (scrollable) ────────────────────────
    outer = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    outer.pack(expand=True, fill="both", padx=24, pady=12)

    # ── CARDS statistik ───────────────────────────────────────
    cards_frame = ctk.CTkFrame(outer, fg_color="transparent")
    cards_frame.pack(fill="x", pady=(0, 16))

    card_data = [
        ("Total Penghulu", "#064E3B",  "#FDFFFE"),
        ("Penghulu Aktif", "#059669",  "#FDFFFE"),
        ("Sedang Tugas",   "#D97706",  "#FDFFFE"),
    ]
    stat_labels = []

    total_v, aktif_v, tugas_v = hitung_stats()
    stat_values = [total_v, aktif_v, tugas_v]

    for i, ((lbl, fg, bg), val) in enumerate(zip(card_data, stat_values)):
        card = ctk.CTkFrame(cards_frame, fg_color=bg, corner_radius=12,
                            border_width=1, border_color=fg, width=200, height=90)
        card.grid(row=0, column=i, padx=10, sticky="ew")
        card.grid_propagate(False)
        cards_frame.grid_columnconfigure(i, weight=1)

        lbl_num = ctk.CTkLabel(card, text=str(val),
                                font=("Segoe UI", 30, "bold"), text_color=fg)
        lbl_num.place(relx=0.5, rely=0.38, anchor="center")
        ctk.CTkLabel(card, text=lbl, font=("Segoe UI", 11, "bold"),
                     text_color=fg).place(relx=0.5, rely=0.76, anchor="center")
        stat_labels.append(lbl_num)

    def refresh_stats():
        t, a, tu = hitung_stats()
        for lbl_w, v in zip(stat_labels, [t, a, tu]):
            lbl_w.configure(text=str(v))

    # ── TOOLBAR ───────────────────────────────────────────────
    toolbar = ctk.CTkFrame(outer, fg_color="transparent")
    toolbar.pack(fill="x", pady=(0, 10))

    btn_tambah = ctk.CTkButton(toolbar, text="+ Tambah Penghulu",
                                height=40, font=("Segoe UI", 13, "bold"),
                                fg_color=PRIMARY, hover_color=SECONDARY,
                                command=lambda: buka_form_tambah())
    btn_tambah.pack(side="left", padx=(0, 8))

    btn_edit = ctk.CTkButton(toolbar, text="✏️Edit Terpilih",
                              height=40, font=("Segoe UI", 13, "bold"),
                              fg_color="#185FA5", hover_color="#0C447C",
                              command=lambda: edit_terpilih())
    btn_edit.pack(side="left", padx=(0, 8))

    btn_hapus = ctk.CTkButton(toolbar, text="- Hapus Terpilih",
                               height=40, font=("Segoe UI", 13, "bold"),
                               fg_color="#D32F2F", hover_color="#B71C1C",
                               command=lambda: hapus_terpilih())
    btn_hapus.pack(side="left", padx=(0, 16))

    # Search & filter di sisi kanan toolbar
    filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
    filter_frame.pack(side="right")

    filter_cb = ctk.CTkComboBox(filter_frame,
                                 values=["Semua Status", "Tersedia", "Sedang Tugas"],
                                 width=150, height=38)
    filter_cb.set("Semua Status")
    filter_cb.pack(side="right", padx=(6, 0))

    search_e = ctk.CTkEntry(filter_frame, placeholder_text="🔍 Cari nama atau ID...",
                             width=220, height=38,
                             border_color="#D1D5DB", border_width=1)
    search_e.pack(side="right", padx=(0, 6))

    # ── TABEL ─────────────────────────────────────────────────
    tbl_card = ctk.CTkFrame(outer, fg_color="#F9FAFB", corner_radius=10,
                             border_width=1, border_color="#E5E7EB")
    tbl_card.pack(fill="both", expand=True)

    style_ph = tkttk.Style()
    style_ph.configure("PH2.Treeview",
                        rowheight=46, font=("Segoe UI", 13),
                        background="white", fieldbackground="white")
    style_ph.configure("PH2.Treeview.Heading",
                        font=("Segoe UI", 13, "bold"),
                        background="#064E3B", foreground="Black", relief="flat")
    style_ph.map("PH2.Treeview",
                 background=[("selected", "#D1FAE5")],
                 foreground=[("selected", "#064E3B")])

    cols       = ("id", "nama", "hp", "status")
    col_labels = ("ID Penghulu", "Nama Penghulu", "Nomor HP/WA", "Status")
    col_widths = [110, 250, 180, 130]

    tbl_wrap = ctk.CTkFrame(tbl_card, fg_color="transparent")
    tbl_wrap.pack(expand=True, fill="both", padx=12, pady=12)

    tree = tkttk.Treeview(tbl_wrap, columns=cols, show="headings",
                           style="PH2.Treeview", selectmode="browse")
    for col, lbl, w in zip(cols, col_labels, col_widths):
        tree.heading(col, text=lbl)
        tree.column(col, width=w, anchor="center")
    tree.column("nama", anchor="w")

    tree.tag_configure("tersedia",     foreground="#059669", background="#F0FFF4")
    tree.tag_configure("sedang_tugas", foreground="#B45309", background="#FFFBEB")

    sb_y = tkttk.Scrollbar(tbl_wrap, orient="vertical", command=tree.yview)
    tree.configure(yscroll=sb_y.set)
    sb_y.pack(side="right", fill="y")
    tree.pack(expand=True, fill="both")

    # ── Fungsi ─────────────────────────────────────────────────
    def muat():
        for i in tree.get_children(): tree.delete(i)
        if not os.path.exists(PATH_P): return
        q        = search_e.get().strip().lower()
        f_status = filter_cb.get()
        with open(PATH_P, "r") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) < 3: continue
                id_p, nama_p, hp_p = p[0], p[1], p[2]
                st  = status_penghulu(nama_p)
                if q and q not in id_p.lower() and q not in nama_p.lower(): continue
                if f_status != "Semua Status" and st != f_status: continue
                tag = "tersedia" if st == "Tersedia" else "sedang_tugas"
                tree.insert("", "end", values=(id_p, nama_p, hp_p, st), tags=(tag,))
        refresh_stats()

    def buka_form_tambah():
        _form_dialog(parent, PATH_P, muat, mode="tambah")

    def edit_terpilih():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih penghulu yang ingin diedit!")
            return
        vals = tree.item(sel)["values"]
        _form_dialog(parent, PATH_P, muat, mode="edit",
                     id_lama=str(vals[0]), nama_lama=str(vals[1]), hp_lama=str(vals[2]))

    def hapus_terpilih():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih penghulu yang ingin dihapus!")
            return
        vals = tree.item(sel)["values"]
        if messagebox.askyesno("Konfirmasi", f"Hapus penghulu {vals[1]}?"):
            with open(PATH_P, "r") as f: lines = f.readlines()
            with open(PATH_P, "w") as f:
                for line in lines:
                    if line.strip().split("|")[0] != str(vals[0]): f.write(line)
            muat()

    # Bind filter & search
    search_e.bind("<Return>", lambda e: muat())
    filter_cb.configure(command=lambda v: muat())
    muat()


def _form_dialog(parent, PATH_P, on_save, mode="tambah",
                 id_lama="", nama_lama="", hp_lama=""):
    """Dialog form tambah / edit penghulu."""
    top_win = parent.winfo_toplevel()
    d = ctk.CTkToplevel(top_win)
    judul = "Tambah Penghulu Baru" if mode == "tambah" else "Edit Data Penghulu"
    d.title(judul)
    d.geometry("440x320")
    d.grab_set(); d.lift()

    ctk.CTkLabel(d, text=judul, font=("Segoe UI", 17, "bold"),
                 text_color="#064E3B").pack(pady=(20, 14))

    form = ctk.CTkFrame(d, fg_color="transparent")
    form.pack(padx=30, fill="x")

    def field(label, ph, val="", disabled=False):
        r = ctk.CTkFrame(form, fg_color="transparent"); r.pack(fill="x", pady=6)
        ctk.CTkLabel(r, text=label, font=("Segoe UI", 12, "bold"),
                     width=120, anchor="w").pack(side="left")
        e = ctk.CTkEntry(r, placeholder_text=ph, height=38, width=260,
                         border_color="#2E7D32", border_width=2)
        if val:
            e.insert(0, val)
        if disabled:
            e.configure(state="disabled")
        e.pack(side="left")
        return e

    id_e   = field("ID Penghulu",  "Contoh: P001", id_lama,   disabled=(mode=="edit"))
    nama_e = field("Nama Lengkap", "Nama penghulu", nama_lama)
    hp_e   = field("Nomor HP/WA",  "08xxxxxxxxxx",  hp_lama)

    def simpan():
        idx  = id_lama if mode == "edit" else id_e.get().strip()
        nama = nama_e.get().strip()
        hp   = hp_e.get().strip()
        if not all([idx, nama, hp]):
            messagebox.showerror("Error", "Isi semua data!", parent=d); return
        if mode == "tambah":
            if os.path.exists(PATH_P):
                with open(PATH_P, "r") as f:
                    for line in f:
                        if line.strip().split("|")[0] == idx:
                            messagebox.showerror("Error", f"ID {idx} sudah ada!", parent=d)
                            return
            with open(PATH_P, "a") as f: f.write(f"{idx}|{nama}|{hp}\n")
            messagebox.showinfo("Sukses", "Data penghulu berhasil ditambah!")
        else:
            with open(PATH_P, "r") as f: lines = f.readlines()
            with open(PATH_P, "w") as f:
                for line in lines:
                    p = line.strip().split("|")
                    f.write(f"{idx}|{nama}|{hp}\n" if p[0]==idx else line)
            messagebox.showinfo("Sukses", "Data penghulu berhasil diperbarui!")
        d.destroy()
        on_save()

    br = ctk.CTkFrame(d, fg_color="transparent"); br.pack(pady=16)
    ctk.CTkButton(br, text="💾 Simpan", fg_color="#064E3B", hover_color="#149060",
                  font=("Segoe UI", 13, "bold"), height=40,
                  command=simpan).pack(side="left", padx=8)
    ctk.CTkButton(br, text="Batal", fg_color="#6B7280",
                  font=("Segoe UI", 13), height=40,
                  command=d.destroy).pack(side="left", padx=8)


# ─────────────────────────────────────────────────────────────
#  Panel: Kelola Informasi Layanan
# ─────────────────────────────────────────────────────────────
def _panel_info(parent, username):
    from layanan.informasi_layanan import baca_konten, simpan_konten
    _header(parent, "Kelola Informasi", "Edit informasi layanan yang tampil ke pengantin")

    konten = baca_konten()
    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(expand=True, fill="both", padx=30, pady=10)

    def seksi(title, key):
        frame = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=8,
                             border_width=1, border_color="#E5E7EB")
        frame.pack(fill="x", pady=8)
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(10,4))
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 14, "bold"),
                     text_color=PRIMARY).pack(side="left")

        isi_lbl = ctk.CTkLabel(frame, text=konten.get(key,""),
                                justify="left", font=("Segoe UI", 12),
                                anchor="w", wraplength=800)
        isi_lbl.pack(anchor="w", padx=20, pady=(0,12))

        def buka_edit():
            top_win = parent.winfo_toplevel()
            d = ctk.CTkToplevel(top_win)
            d.title(f"Edit: {title}")
            d.geometry("640x380")
            d.grab_set(); d.lift()
            ctk.CTkLabel(d, text=f"Edit: {title}",
                         font=("Segoe UI", 15,"bold")).pack(pady=15)
            tb = ctk.CTkTextbox(d, width=580, height=220, font=("Segoe UI",12))
            tb.pack(padx=30)
            tb.insert("1.0", konten.get(key,""))
            def simpan():
                konten[key] = tb.get("1.0","end").strip()
                simpan_konten(konten)
                isi_lbl.configure(text=konten[key])
                d.destroy()
            br = ctk.CTkFrame(d, fg_color="transparent"); br.pack(pady=12)
            ctk.CTkButton(br, text="Simpan", fg_color=PRIMARY,
                          command=simpan).pack(side="left", padx=8)
            ctk.CTkButton(br, text="Batal", fg_color="gray",
                          command=d.destroy).pack(side="left", padx=8)

        ctk.CTkButton(top, text="✏️ Edit", width=80, height=28,
                      fg_color="#185FA5", hover_color="#0C447C",
                      font=("Segoe UI",11),
                      command=buka_edit).pack(side="right")

    seksi("📋 Dokumen Persyaratan", "syarat")
    seksi("💰 Informasi Biaya", "biaya")
    seksi("🕐 Jam Operasional KUA", "jam_ops")
    seksi("📞 Kontak KUA", "kontak")


# ─────────────────────────────────────────────────────────────
#  Panel: Rekap Laporan
# ─────────────────────────────────────────────────────────────
def _panel_rekap(parent, username, path_db):
    _header(parent, "Laporan Statistik", "Rekapitulasi data pendaftaran nikah")

    counts = {"Menunggu":0,"Terverifikasi":0,"Selesai":0,"Dibatalkan":0}
    semua_data = []
    if os.path.exists(path_db):
        with open(path_db,"r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 10:
                    if d[9] in counts: counts[d[9]] += 1
                if len(d) >= 11: semua_data.append(d)

    warna = {"Menunggu":"#F59E0B","Terverifikasi":"#3B82F6",
             "Selesai":"#10B981","Dibatalkan":"#EF4444"}

    stat = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=10)
    stat.pack(fill="x", padx=30, pady=12)
    inner = ctk.CTkFrame(stat, fg_color="transparent")
    inner.pack(pady=12)
    total = sum(counts.values())
    for i,(lbl,val) in enumerate(list(counts.items())+[("Total",total)]):
        w = warna.get(lbl,"#149060")
        box = ctk.CTkFrame(inner, fg_color="white", corner_radius=8, width=120, height=65)
        box.grid(row=0,column=i,padx=10); box.grid_propagate(False)
        ctk.CTkLabel(box, text=str(val), font=("Segoe UI",22,"bold"),
                     text_color=w).place(relx=0.5,rely=0.38,anchor="center")
        ctk.CTkLabel(box, text=lbl, font=("Segoe UI",10),
                     text_color="#6B7280").place(relx=0.5,rely=0.78,anchor="center")

    tbl = ctk.CTkFrame(parent, corner_radius=8)
    tbl.pack(expand=True, fill="both", padx=30, pady=6)

    cols = ("id","nik_suami","nama_suami","nama_istri","wali","tanggal","jam","lokasi","status","penghulu")
    col_labels = ("ID","NIK Suami","Nama Suami","Nama Istri","Wali","Tanggal","Jam","Lokasi","Status","Penghulu")
    tree2 = ttk.Treeview(tbl, columns=cols, show="headings")
    cw = [70,120,130,130,120,90,60,130,100,120]
    for col,lbl,w in zip(cols,col_labels,cw):
        tree2.heading(col,text=lbl); tree2.column(col,width=w,anchor="center")
    sb = ttk.Scrollbar(tbl,orient="vertical",command=tree2.yview)
    tree2.configure(yscroll=sb.set)
    tree2.pack(side="left",expand=True,fill="both"); sb.pack(side="right",fill="y")

    for d in semua_data:
        if len(d)>=11:
            tree2.insert("","end",values=(d[0],d[1],d[2],d[4],d[5],d[6],d[7],d[8],d[9],d[10]))

    def ekspor_pdf():
        if not semua_data:
            messagebox.showwarning("Kosong","Tidak ada data untuk diekspor."); return
        from tkinter import filedialog
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = filedialog.asksaveasfilename(
            title="Simpan Laporan",
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf"),("All Files","*.*")],
            initialfile=f"Rekap_Nikah_{now}.pdf"
        )
        if not save_path: return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer,HRFlowable
            from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            doc = SimpleDocTemplate(save_path,pagesize=landscape(A4),
                                    topMargin=1.5*cm,bottomMargin=1.5*cm,
                                    leftMargin=1.5*cm,rightMargin=1.5*cm)
            hijau_tua = colors.HexColor("#064E3B")
            hijau_muda= colors.HexColor("#D1FAE5")
            abu       = colors.HexColor("#6B7280")
            styles    = getSampleStyleSheet()
            s_j = ParagraphStyle("j",parent=styles["Normal"],fontSize=16,
                                  fontName="Helvetica-Bold",textColor=hijau_tua,alignment=TA_CENTER,spaceAfter=4)
            s_s = ParagraphStyle("s",parent=styles["Normal"],fontSize=10,
                                  fontName="Helvetica",textColor=abu,alignment=TA_CENTER,spaceAfter=2)
            story=[
                Paragraph("LAPORAN REKAPITULASI PENDAFTARAN NIKAH",s_j),
                Paragraph(f"Dicetak oleh: {username}  |  {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",s_s),
                Spacer(1,0.3*cm), HRFlowable(width="100%",thickness=2,color=hijau_tua), Spacer(1,0.3*cm)
            ]
            stat_data=[["Status","Jumlah"]]+[[lbl,str(val)] for lbl,val in list(counts.items())+[("Total",total)]]
            st_tbl=Table(stat_data,colWidths=[5*cm,3*cm])
            st_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),hijau_tua),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#E5E7EB")),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("BACKGROUND",(0,-1),(-1,-1),hijau_muda),
            ]))
            story.append(st_tbl); story.append(Spacer(1,0.4*cm))
            header_row=["ID","NIK Suami","Nama Suami","Nama Istri","Wali","Tanggal","Jam","Lokasi","Status","Penghulu"]
            tbl_data=[header_row]
            for d in semua_data:
                if len(d)>=11: tbl_data.append([d[0],d[1],d[2],d[4],d[5],d[6],d[7],d[8],d[9],d[10]])
            col_w=[1.8*cm,3.2*cm,3.5*cm,3.5*cm,3*cm,2.4*cm,1.5*cm,3.5*cm,2.5*cm,3*cm]
            d_tbl=Table(tbl_data,colWidths=col_w,repeatRows=1)
            d_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),hijau_tua),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#E5E7EB")),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ]))
            story.append(d_tbl)
            doc.build(story)
            messagebox.showinfo("Sukses",f"PDF tersimpan:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error PDF",f"Gagal:\n{e}")

    ctk.CTkButton(parent, text="📄 Ekspor Laporan PDF", height=40,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI",13,"bold"),
                  command=ekspor_pdf).pack(padx=30, pady=10, anchor="w")


# ─────────────────────────────────────────────────────────────
#  MAIN: dashboard_admin — single window + sidebar
# ─────────────────────────────────────────────────────────────
def dashboard_admin(username="admin"):
    from assets.sidebar import buat_sidebar

    app = ctk.CTk()
    app.after(0, lambda: app.state("zoomed"))
    app.title("Sistem Layanan Administrasi Nikah KUA")

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    path_db = "database/pendaftaran.txt"

    MENU = [
        ("dashboard",  "Dashboard"),
        ("layanan",    "Kelola Layanan"),
        ("penghulu",   "Data Penghulu"),
        ("info",       "Kelola Informasi"),
        ("rekap",      "Laporan Statistik"),
    ]

    # State aktif
    active = {"key": "dashboard"}
    content_ref = {"frame": None}
    btn_refs_ref = {"refs": {}}

    def tampil_konten(key):
        # Hapus frame lama
        if content_ref["frame"]:
            content_ref["frame"].destroy()

        cf = ctk.CTkFrame(main_area, fg_color="white", corner_radius=0)
        cf.pack(expand=True, fill="both")
        content_ref["frame"] = cf

        # Perbarui highlight tombol sidebar
        for k, btn in btn_refs_ref["refs"].items():
            is_act = (k == key)
            btn.configure(
                fg_color="white" if is_act else "transparent",
                text_color=PRIMARY if is_act else "white",
                font=("Segoe UI", 13, "bold" if is_act else "normal"),
                hover_color="#e8f5f0" if is_act else "#0D6342",
            )

        if key == "dashboard":     _panel_dashboard(cf, username, path_db)
        elif key == "layanan":     _panel_verifikasi(cf, username, path_db)
        elif key == "penghulu":    _panel_penghulu(cf, username)
        elif key == "info":        _panel_info(cf, username)
        elif key == "rekap":       _panel_rekap(cf, username, path_db)

    def logout():
        if messagebox.askyesno("Logout","Apakah Anda ingin keluar?"):
            app.destroy()
            from login import login_page
            login_page()

    # Layout utama
    outer = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
    outer.pack(expand=True, fill="both")

    sidebar, btn_refs = buat_sidebar(outer, "admin", username, MENU, "dashboard",
                                     on_select=tampil_konten, on_logout=logout)
    btn_refs_ref["refs"] = btn_refs

    main_area = ctk.CTkFrame(outer, fg_color="white", corner_radius=0)
    main_area.pack(side="left", expand=True, fill="both")

    tampil_konten("dashboard")
    app.mainloop()
