import customtkinter as ctk
from tkinter import messagebox, ttk
import os
from datetime import datetime

PRIMARY   = "#064E3B"
SECONDARY = "#149060"

def _header(parent, title, subtitle=""):
    h = ctk.CTkFrame(parent, fg_color="transparent")
    h.pack(fill="x", padx=30, pady=(20, 4))
    ctk.CTkLabel(h, text=title, font=("Segoe UI", 22, "bold"), text_color="#111827").pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(h, text=subtitle, font=("Segoe UI", 12), text_color="#6B7280").pack(anchor="w")
    ctk.CTkFrame(parent, height=1, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(6,0))


# ── Panel: Dashboard ──────────────────────────────────────────
def _panel_dashboard(parent, username, path_db):
    _header(parent, "Dashboard", "Jadwal & tugas akad nikah Anda")
    jadwal = []
    if os.path.exists(path_db):
        with open(path_db, "r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 11 and d[10] == username and d[9] in ("Terverifikasi", "Selesai"):
                    jadwal.append(d)

    counts = {"Terverifikasi": 0, "Selesai": 0}
    for d in jadwal:
        if d[9] in counts: counts[d[9]] += 1

    stat = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=10)
    stat.pack(fill="x", padx=30, pady=12)
    inner = ctk.CTkFrame(stat, fg_color="transparent"); inner.pack(pady=12)
    warna = {"Terverifikasi": "#3B82F6", "Selesai": "#10B981"}
    for i, (lbl, val) in enumerate(counts.items()):
        box = ctk.CTkFrame(inner, fg_color="white", corner_radius=8, width=140, height=70)
        box.grid(row=0, column=i, padx=12); box.grid_propagate(False)
        ctk.CTkLabel(box, text=str(val), font=("Segoe UI", 26, "bold"),
                     text_color=warna[lbl]).place(relx=0.5, rely=0.38, anchor="center")
        ctk.CTkLabel(box, text=lbl, font=("Segoe UI", 11),
                     text_color="#6B7280").place(relx=0.5, rely=0.78, anchor="center")

    info = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=10,
                        border_width=1, border_color="#E5E7EB")
    info.pack(fill="x", padx=30, pady=8)
    ctk.CTkLabel(info, text=f"👋  Selamat datang, {username}!",
                 font=("Segoe UI", 14, "bold"), text_color=PRIMARY).pack(anchor="w", padx=20, pady=(14,4))
    ctk.CTkLabel(info,
                 text="Gunakan menu Jadwal Tugas untuk melihat daftar akad, konfirmasi pelaksanaan & tambah catatan.",
                 font=("Segoe UI", 12), text_color="#374151").pack(anchor="w", padx=20, pady=(0,14))


# ── Panel: Jadwal Tugas ───────────────────────────────────────
def _panel_jadwal(parent, username, path_db):
    _header(parent, "Jadwal Tugas", "Daftar akad nikah yang Anda tangani")

    tbl_frame = ctk.CTkFrame(parent, corner_radius=8)
    tbl_frame.pack(expand=True, fill="both", padx=30, pady=10)

    cols = ("id","nama_suami","nama_istri","tanggal","jam","lokasi","status","catatan")
    col_labels = ("ID","Nama Suami","Nama Istri","Tgl Nikah","Jam","Lokasi","Status","Catatan")
    tree = ttk.Treeview(tbl_frame, columns=cols, show="headings")
    tree.tag_configure("selesai",      foreground="#149060")
    tree.tag_configure("terverifikasi",foreground="#185FA5")
    col_widths = [70,140,140,100,60,120,110,200]
    for col, lbl, w in zip(cols, col_labels, col_widths):
        tree.heading(col, text=lbl); tree.column(col, width=w, anchor="center")
    sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y"); tree.pack(expand=True, fill="both")

    def muat():
        for i in tree.get_children(): tree.delete(i)
        if not os.path.exists(path_db): return
        with open(path_db, "r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 11 and d[10] == username and d[9] in ("Terverifikasi","Selesai"):
                    catatan = d[11] if len(d) > 11 else "-"
                    tag = "selesai" if d[9]=="Selesai" else "terverifikasi"
                    tree.insert("","end",
                                values=(d[0],d[2],d[4],d[6],d[7],d[8],d[9],catatan),
                                tags=(tag,))

    # Action bar konfirmasi selesai
    act = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=8,
                       border_width=1, border_color="#E5E7EB")
    act.pack(fill="x", padx=30, pady=(0,12))
    act_inner = ctk.CTkFrame(act, fg_color="transparent")
    act_inner.pack(side="left", padx=12, pady=10)

    def konfirmasi_selesai():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan","Pilih akad yang ingin dikonfirmasi!"); return
        vals = tree.item(sel)['values']
        id_reg, status_skrg = vals[0], vals[6]
        if status_skrg == "Selesai":
            messagebox.showinfo("Info","Akad ini sudah ditandai selesai."); return
        with open(path_db,"r") as f: lines = f.readlines()
        with open(path_db,"w") as f:
            for line in lines:
                d = line.strip().split("|")
                if d[0] == str(id_reg):
                    d[9] = "Selesai"
                    while len(d) < 12: d.append("-")
                    f.write("|".join(d)+"\n")
                else: f.write(line)
        messagebox.showinfo("Sukses",f"Akad {id_reg} berhasil dikonfirmasi selesai!")
        muat()

    ctk.CTkButton(act_inner, text="✅ Konfirmasi Selesai", height=36,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI",12,"bold"),
                  command=konfirmasi_selesai).pack(side="left", padx=4)
    muat()


# ── Panel: Catatan Tugas ──────────────────────────────────────
def _panel_catatan(parent, username, path_db):
    _header(parent, "Catatan Tugas", "Tambah atau edit catatan berdasarkan ID Registrasi")

    main = ctk.CTkFrame(parent, fg_color="transparent")
    main.pack(expand=True, fill="both", padx=30, pady=10)
    main.grid_columnconfigure(0, weight=1)
    main.grid_rowconfigure(1, weight=1)

    # ── Pilih ID Reg ───────────────────────────────────────────
    top = ctk.CTkFrame(main, fg_color="#F9FAFB", corner_radius=10,
                       border_width=1, border_color="#E5E7EB")
    top.grid(row=0, column=0, sticky="ew", pady=(0,12))

    top_inner = ctk.CTkFrame(top, fg_color="transparent")
    top_inner.pack(fill="x", padx=20, pady=14)

    ctk.CTkLabel(top_inner, text="Pilih ID Registrasi:",
                 font=("Segoe UI",13,"bold")).pack(side="left", padx=(0,10))

    # Buat list ID reg tugas penghulu ini
    def ambil_id_list():
        ids = []
        if os.path.exists(path_db):
            with open(path_db,"r") as f:
                for line in f:
                    d = line.strip().split("|")
                    if len(d) >= 11 and d[10] == username and d[9] in ("Terverifikasi","Selesai"):
                        label = f"{d[0]}  —  {d[2]} & {d[4]}  ({d[9]})"
                        ids.append((d[0], label))
        return ids

    id_list = ambil_id_list()
    id_labels = [x[1] for x in id_list] if id_list else ["Tidak ada tugas aktif"]
    id_map = {x[1]: x[0] for x in id_list}

    id_cb = ctk.CTkComboBox(top_inner, values=id_labels, width=500, height=38)
    id_cb.set(id_labels[0] if id_labels else "")
    id_cb.pack(side="left", padx=(0,12))

    lbl_status_catatan = ctk.CTkLabel(top_inner, text="", font=("Segoe UI",11),
                                       text_color="#149060")
    lbl_status_catatan.pack(side="left")

    # ── Form catatan ───────────────────────────────────────────
    form = ctk.CTkFrame(main, fg_color="#F9FAFB", corner_radius=10,
                        border_width=1, border_color="#E5E7EB")
    form.grid(row=1, column=0, sticky="nsew")

    ctk.CTkLabel(form, text="Catatan / Kendala:",
                 font=("Segoe UI",13,"bold")).pack(anchor="w", padx=20, pady=(16,6))

    catatan_box = ctk.CTkTextbox(form, font=("Segoe UI",12), corner_radius=8,
                                  border_width=2, border_color="#2E7D32")
    catatan_box.pack(expand=True, fill="both", padx=20, pady=(0,12))

    def muat_catatan(event=None):
        pilih = id_cb.get()
        id_reg = id_map.get(pilih)
        if not id_reg: return
        catatan_box.delete("1.0","end")
        if os.path.exists(path_db):
            with open(path_db,"r") as f:
                for line in f:
                    d = line.strip().split("|")
                    if d[0] == id_reg:
                        catatan = d[11] if len(d) > 11 else ""
                        if catatan and catatan != "-":
                            catatan_box.insert("1.0", catatan)
                        break
        lbl_status_catatan.configure(text="")

    def simpan_catatan():
        pilih = id_cb.get()
        id_reg = id_map.get(pilih)
        if not id_reg:
            messagebox.showwarning("Peringatan","Pilih ID Registrasi terlebih dahulu!"); return
        catatan = catatan_box.get("1.0","end").strip()
        if not catatan:
            messagebox.showwarning("Peringatan","Catatan tidak boleh kosong!"); return

        with open(path_db,"r") as f: lines = f.readlines()
        with open(path_db,"w") as f:
            for line in lines:
                d = line.strip().split("|")
                if d[0] == id_reg:
                    while len(d) < 12: d.append("-")
                    d[11] = catatan
                    f.write("|".join(d)+"\n")
                else: f.write(line)
        lbl_status_catatan.configure(text="✅ Catatan berhasil disimpan!", text_color="#149060")

    id_cb.configure(command=lambda v: muat_catatan())

    btn_bar = ctk.CTkFrame(form, fg_color="transparent")
    btn_bar.pack(fill="x", padx=20, pady=(0,16))
    ctk.CTkButton(btn_bar, text="💾 Simpan Catatan", height=40,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI",13,"bold"),
                  command=simpan_catatan).pack(side="left", padx=(0,10))
    ctk.CTkButton(btn_bar, text="Bersihkan", height=40,
                  fg_color="#6B7280",
                  command=lambda: catatan_box.delete("1.0","end")).pack(side="left")

    # Muat catatan default (ID pertama)
    muat_catatan()


# ── Panel: Rekap Statistik ────────────────────────────────────
def _panel_rekap(parent, username, path_db):
    _header(parent, "Rekap Statistik", f"Statistik tugas akad — {username}")

    # Kumpulkan data
    semua = []
    if os.path.exists(path_db):
        with open(path_db,"r") as f:
            for line in f:
                d = line.strip().split("|")
                if len(d) >= 11 and d[10] == username and d[9] in ("Terverifikasi","Selesai"):
                    semua.append(d)

    total      = len(semua)
    selesai    = sum(1 for d in semua if d[9]=="Selesai")
    menunggu   = sum(1 for d in semua if d[9]=="Terverifikasi")

    # Rekap per bulan
    per_bulan = {}
    for d in semua:
        try:
            bulan = "-".join(d[6].split("-")[1:]) if d[6] != "-" else "?"  # MM-YYYY
        except: bulan = "?"
        if bulan not in per_bulan: per_bulan[bulan] = {"Terverifikasi":0,"Selesai":0}
        per_bulan[bulan][d[9]] = per_bulan[bulan].get(d[9],0)+1

    # ── Kartu statistik
    warna = {"Total":"#064E3B","Selesai":"#10B981","Aktif":"#3B82F6"}
    stat = ctk.CTkFrame(parent, fg_color="#F0FDF4", corner_radius=10)
    stat.pack(fill="x", padx=30, pady=12)
    inner = ctk.CTkFrame(stat, fg_color="transparent"); inner.pack(pady=14)
    for i,(lbl,val,w) in enumerate([("Total Tugas",total,"#064E3B"),
                                     ("Selesai",selesai,"#10B981"),
                                     ("Aktif / Terjadwal",menunggu,"#3B82F6")]):
        box = ctk.CTkFrame(inner, fg_color="white", corner_radius=8, width=160, height=75)
        box.grid(row=0,column=i,padx=14); box.grid_propagate(False)
        ctk.CTkLabel(box, text=str(val), font=("Segoe UI",28,"bold"),
                     text_color=w).place(relx=0.5,rely=0.38,anchor="center")
        ctk.CTkLabel(box, text=lbl, font=("Segoe UI",11),
                     text_color="#6B7280").place(relx=0.5,rely=0.8,anchor="center")

    # ── Tabel detail
    ctk.CTkLabel(parent, text="Detail Semua Tugas",
                 font=("Segoe UI",13,"bold"), text_color=PRIMARY).pack(anchor="w", padx=30, pady=(8,2))
    tbl_f = ctk.CTkFrame(parent, corner_radius=8)
    tbl_f.pack(expand=True, fill="both", padx=30, pady=(0,8))

    cols = ("id","nama_suami","nama_istri","tanggal","jam","lokasi","status","catatan")
    col_labels = ("ID","Nama Suami","Nama Istri","Tgl Nikah","Jam","Lokasi","Status","Catatan")
    tree = ttk.Treeview(tbl_f, columns=cols, show="headings")
    tree.tag_configure("selesai",       foreground="#149060")
    tree.tag_configure("terverifikasi", foreground="#185FA5")
    cw = [70,140,140,100,60,130,110,200]
    for col,lbl,w in zip(cols,col_labels,cw):
        tree.heading(col,text=lbl); tree.column(col,width=w,anchor="center")
    sbx = ttk.Scrollbar(tbl_f,orient="horizontal",command=tree.xview)
    tree.configure(xscroll=sbx.set)
    sbx.pack(side="bottom",fill="x"); tree.pack(expand=True,fill="both")

    for d in semua:
        catatan = d[11] if len(d)>11 else "-"
        tag = "selesai" if d[9]=="Selesai" else "terverifikasi"
        tree.insert("","end",values=(d[0],d[2],d[4],d[6],d[7],d[8],d[9],catatan),tags=(tag,))

    # ── Ekspor PDF
    def ekspor_pdf():
        if not semua:
            messagebox.showwarning("Kosong","Tidak ada data untuk diekspor."); return
        from tkinter import filedialog
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = filedialog.asksaveasfilename(
            title="Simpan Rekap PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf"),("All Files","*.*")],
            initialfile=f"Rekap_Penghulu_{username.replace(' ','_')}_{now}.pdf"
        )
        if not save_path: return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer,HRFlowable
            from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            doc = SimpleDocTemplate(save_path, pagesize=landscape(A4),
                                    topMargin=1.5*cm, bottomMargin=1.5*cm,
                                    leftMargin=1.5*cm, rightMargin=1.5*cm)
            hijau_tua  = colors.HexColor("#064E3B")
            hijau_muda = colors.HexColor("#D1FAE5")
            abu        = colors.HexColor("#6B7280")
            styles     = getSampleStyleSheet()
            s_j = ParagraphStyle("j",parent=styles["Normal"],fontSize=16,
                                  fontName="Helvetica-Bold",textColor=hijau_tua,alignment=TA_CENTER,spaceAfter=4)
            s_s = ParagraphStyle("s",parent=styles["Normal"],fontSize=10,
                                  fontName="Helvetica",textColor=abu,alignment=TA_CENTER,spaceAfter=2)

            story = [
                Paragraph(f"REKAP STATISTIK PENGHULU", s_j),
                Paragraph(f"Penghulu: {username}  |  Dicetak: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", s_s),
                Spacer(1,0.3*cm), HRFlowable(width="100%",thickness=2,color=hijau_tua), Spacer(1,0.3*cm)
            ]

            # Tabel ringkasan
            sum_data = [["Keterangan","Jumlah"],
                        ["Total Tugas", str(total)],
                        ["Selesai", str(selesai)],
                        ["Aktif / Terjadwal", str(menunggu)]]
            s_tbl = Table(sum_data, colWidths=[6*cm,3*cm])
            s_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),hijau_tua),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#E5E7EB")),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ]))
            story += [s_tbl, Spacer(1,0.4*cm)]

            # Tabel detail
            header_row = ["ID","Nama Suami","Nama Istri","Tgl Nikah","Jam","Lokasi","Status","Catatan"]
            tbl_data   = [header_row]
            for d in semua:
                catatan = d[11] if len(d)>11 else "-"
                tbl_data.append([d[0],d[2],d[4],d[6],d[7],d[8],d[9],catatan])

            col_w = [1.8*cm,3.5*cm,3.5*cm,2.4*cm,1.5*cm,3.5*cm,2.8*cm,4*cm]
            d_tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
            d_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),hijau_tua),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#E5E7EB")),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,hijau_muda]),
            ]))
            story.append(d_tbl)
            doc.build(story)
            messagebox.showinfo("Sukses",f"PDF berhasil disimpan:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error PDF",f"Gagal membuat PDF:\n{e}")

    ctk.CTkButton(parent, text="📄 Ekspor Rekap PDF", height=40,
                  fg_color=PRIMARY, hover_color=SECONDARY,
                  font=("Segoe UI",13,"bold"),
                  command=ekspor_pdf).pack(padx=30, pady=(0,12), anchor="w")


# ── MAIN: dashboard_penghulu ──────────────────────────────────
def dashboard_penghulu(username="penghulu"):
    from assets.sidebar import buat_sidebar

    app = ctk.CTk()
    app.after(0, lambda: app.state("zoomed"))
    app.title("Sistem Layanan Administrasi Nikah KUA")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    path_db = "database/pendaftaran.txt"
    MENU = [
        ("dashboard", "Dashboard"),
        ("jadwal",    "Jadwal Tugas"),
        ("catatan",   "Catatan Tugas"),
        ("rekap",     "Rekap Statistik"),
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
                font=("Segoe UI", 13, "bold" if is_act else "normal"),
                hover_color="#e8f5f0" if is_act else "#0D6342",
            )
        if key == "dashboard": _panel_dashboard(cf, username, path_db)
        elif key == "jadwal":  _panel_jadwal(cf, username, path_db)
        elif key == "catatan": _panel_catatan(cf, username, path_db)
        elif key == "rekap":   _panel_rekap(cf, username, path_db)

    def logout():
        if messagebox.askyesno("Logout","Apakah Anda ingin keluar?"):
            app.destroy()
            from login import login_page
            login_page()

    outer = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
    outer.pack(expand=True, fill="both")
    sidebar, btn_refs = buat_sidebar(outer, "penghulu", username, MENU,
                                     "dashboard", on_select=tampil_konten, on_logout=logout)
    btn_refs_ref["refs"] = btn_refs
    main_area = ctk.CTkFrame(outer, fg_color="white", corner_radius=0)
    main_area.pack(side="left", expand=True, fill="both")
    tampil_konten("dashboard")
    app.mainloop()
