import os

PATH = "database/informasi_layanan.txt"

def baca_konten():
    konten = {"syarat":"","biaya":"","jam_ops":"","kontak":""}
    if not os.path.exists(PATH): return konten
    syarat=[]; biaya=[]; jam=[]; kontak=[]
    with open(PATH,"r") as f:
        for line in f:
            if "|" not in line: continue
            kat, isi = line.strip().split("|",1)
            if kat=="SYARAT": syarat.append(isi)
            elif kat=="BIAYA": biaya.append(isi)
            elif kat=="JAMKERJA": jam.append(isi)
            elif kat=="KONTAK": kontak.append(isi)
    konten["syarat"]  = "\n".join(syarat)
    konten["biaya"]   = "\n".join(biaya)
    konten["jam_ops"] = "\n".join(jam)
    konten["kontak"]  = "\n".join(kontak)
    return konten

def simpan_konten(konten):
    baris = []
    for line in konten.get("syarat","").splitlines():
        if line.strip(): baris.append(f"SYARAT|{line.strip()}")
    for line in konten.get("biaya","").splitlines():
        if line.strip(): baris.append(f"BIAYA|{line.strip()}")
    for line in konten.get("jam_ops","").splitlines():
        if line.strip(): baris.append(f"JAMKERJA|{line.strip()}")
    for line in konten.get("kontak","").splitlines():
        if line.strip(): baris.append(f"KONTAK|{line.strip()}")
    with open(PATH,"w") as f:
        f.write("\n".join(baris)+"\n")
