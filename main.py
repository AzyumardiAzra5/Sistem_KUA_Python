import os

# Pastikan working directory selalu di folder project ini,
# supaya semua path relatif (assets/, database/) selalu ketemu
# walaupun program dijalankan dari folder lain.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from login import login_page

if __name__ == "__main__":
    login_page()