import tkinter as tk
from tkinter import ttk, messagebox
import json, os, hashlib
from datetime import datetime, timedelta

APP_TITLE = "PerBENROY.COM"
BASE = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE, "users.json")
BOOKS_FILE = os.path.join(BASE, "books.json")
BORROWINGS_FILE = os.path.join(BASE, "borrowings.json")

NAVY="#0B1F3A"; NAVY2="#102A4C"; BLUE="#1565C0"; BLUE2="#1976D2"
BG="#F4F7FB"; WHITE="#FFFFFF"; TEXT="#172B4D"; MUTED="#6B7A90"
SUCCESS="#168A5B"; DANGER="#C0392B"; WARNING="#D68910"; BORDER="#D9E2EF"
FONT="Segoe UI"

DEFAULT_BOOKS=[
 {"id":1,"judul":"Laskar Pelangi","penulis":"Andrea Hirata","tahun":"2005","stok":5},
 {"id":2,"judul":"Bumi","penulis":"Tere Liye","tahun":"2014","stok":3},
 {"id":3,"judul":"Atomic Habits","penulis":"James Clear","tahun":"2018","stok":4},
 {"id":4,"judul":"Bumi Manusia","penulis":"Pramoedya Ananta Toer","tahun":"1980","stok":2},
 {"id":5,"judul":"Filosofi Teras","penulis":"Henry Manampiring","tahun":"2018","stok":4},
]

def read_json(path, default):
    try:
        if not os.path.exists(path):
            write_json(path, default)
            return default.copy() if isinstance(default,dict) else list(default)
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except (OSError,json.JSONDecodeError):
        return default.copy() if isinstance(default,dict) else list(default)

def write_json(path,data):
    with open(path,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)

_CACHE = {"users": None, "books": None, "borrows": None}

def users():
    if _CACHE["users"] is None:
        _CACHE["users"] = read_json(USERS_FILE, {})
    return _CACHE["users"]

def books():
    if _CACHE["books"] is None:
        _CACHE["books"] = read_json(BOOKS_FILE, DEFAULT_BOOKS)
    return _CACHE["books"]

def borrows():
    if _CACHE["borrows"] is None:
        _CACHE["borrows"] = read_json(BORROWINGS_FILE, [])
    return _CACHE["borrows"]

def save_users(x):
    _CACHE["users"] = x
    write_json(USERS_FILE, x)

def save_books(x):
    _CACHE["books"] = x
    write_json(BOOKS_FILE, x)

def save_borrows(x):
    _CACHE["borrows"] = x
    write_json(BORROWINGS_FILE, x)
def phash(p): return hashlib.sha256(p.encode()).hexdigest()
def nid(items): return max([int(x.get("id",0)) for x in items] or [0])+1

def button(parent,text,command,bg=BLUE):
    b=tk.Button(parent,text=text,command=command,bg=bg,fg=WHITE,
        activebackground=BLUE2,activeforeground=WHITE,bd=0,relief="flat",
        font=(FONT,10,"bold"),cursor="hand2",padx=14,pady=9)
    b.bind("<Enter>",lambda e:b.config(bg=BLUE2 if bg!=DANGER else "#A93226"))
    b.bind("<Leave>",lambda e:b.config(bg=bg))
    return b

def panel(parent):
    return tk.Frame(parent,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE); self.geometry("1280x760"); self.minsize(1050,650); self.configure(bg=BG)
        self.current_user=None; self.page="main"
        self._after_jobs=[]
        self._anim_token=0
        s=ttk.Style(self)
        try:s.theme_use("clam")
        except tk.TclError:pass
        s.configure("Treeview",background=WHITE,foreground=TEXT,rowheight=34,fieldbackground=WHITE,font=(FONT,10))
        s.configure("Treeview.Heading",background=NAVY2,foreground=WHITE,font=(FONT,10,"bold"),padding=8)
        self.main_page()

    def stop_animations(self):
        self._anim_token += 1
        for job in self._after_jobs:
            try: self.after_cancel(job)
            except (tk.TclError, ValueError): pass
        self._after_jobs.clear()
        self._anim_running = False

    def schedule(self, ms, callback):
        token = self._anim_token
        job_box = [None]
        def runner():
            job = job_box[0]
            if job in self._after_jobs:
                self._after_jobs.remove(job)
            if token != self._anim_token:
                return
            callback()
        job_box[0] = self.after(ms, runner)
        self._after_jobs.append(job_box[0])
        return job_box[0]

    def _run_scheduled(self, token, callback):
        if token == self._anim_token:
            callback()

    def clear(self):
        self.stop_animations()
        for w in self.winfo_children(): w.destroy()

    def login(self):
        self.clear(); self.current_user=None
        self._anim_running = True
        root=tk.Frame(self,bg=NAVY); root.pack(fill="both",expand=True)
        left=tk.Frame(root,bg=NAVY); left.place(relwidth=.52,relheight=1)
        tk.Label(left,text="BENROY",bg=NAVY,fg=WHITE,font=(FONT,38,"bold")).pack(pady=(130,5))
        tk.Label(left,text="PerBENROY.COM",bg=NAVY,fg="#E53935",font=(FONT,12,"bold")).pack()
        tk.Frame(left,bg=BLUE2,width=90,height=4).pack(pady=25)
        tk.Label(left,text="Kelola koleksi buku,\npeminjaman, dan anggota\ndalam satu aplikasi.",
                 bg=NAVY,fg="#DCE7F5",font=(FONT,16),justify="center").pack()
        right=tk.Frame(root,bg=BG); right.place(relx=.52,relwidth=.48,relheight=1)
        box=panel(right); box.place(relx=.5,rely=.5,anchor="center",width=420,height=440)
        tk.Label(box,text="Selamat Datang",bg=WHITE,fg=TEXT,font=(FONT,25,"bold")).pack(pady=(45,5))
        tk.Label(box,text="Masuk ke dashboard perpustakaan",bg=WHITE,fg=MUTED,font=(FONT,10)).pack(pady=(0,30))
        form=tk.Frame(box,bg=WHITE); form.pack(fill="x",padx=45)
        tk.Label(form,text="Username",bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
        u=tk.Entry(form,font=(FONT,11),bg="#F8FAFD",relief="solid",bd=1); u.pack(fill="x",ipady=9,pady=(6,16))
        tk.Label(form,text="Password",bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
        p=tk.Entry(form,show="•",font=(FONT,11),bg="#F8FAFD",relief="solid",bd=1); p.pack(fill="x",ipady=9,pady=(6,22))
        def masuk():
            data=users(); name=u.get().strip()
            if not name or not p.get(): messagebox.showwarning("Login","Username dan password wajib diisi."); return
            if name not in data or data[name].get("password")!=phash(p.get()):
                messagebox.showerror("Login Gagal","Username atau password salah."); return
            self.current_user=name; self.dashboard()
        button(form,"MASUK",masuk).pack(fill="x")
        button(form,"Buat Akun Baru",self.signup,NAVY2).pack(fill="x",pady=10)
        p.bind("<Return>",lambda e:masuk()); u.focus_set()
        self._start_login_animation(left)

    def _start_login_animation(self, parent):
        """Animasi login kontinu, ringan, dan aman dibatalkan saat pindah halaman."""
        canvas = tk.Canvas(parent, bg=NAVY, bd=0, highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Konten login tetap berada di atas canvas karena canvas dibuat lebih dulu.
        particles = []
        specs = [(0.12,0.18,3,0.45),(0.26,0.31,5,0.32),(0.41,0.17,3,0.58),
                 (0.68,0.28,4,0.37),(0.82,0.13,3,0.52),(0.90,0.48,5,0.29),
                 (0.17,0.72,4,0.41),(0.73,0.76,3,0.62),(0.48,0.87,4,0.35)]
        for rx, ry, r, speed in specs:
            item=canvas.create_oval(0,0,r*2,r*2,fill="#1C4E7A",outline="")
            particles.append([item,rx,ry,r,speed])
        ring=canvas.create_oval(0,0,170,170,outline="#174777",width=2)
        glow=canvas.create_oval(0,0,90,90,fill="#12365D",outline="")
        line=canvas.create_rectangle(0,0,180,3,fill=BLUE2,outline="")
        self._login_anim_state=(canvas,particles,ring,glow,line,0.0)
        self.schedule(40, self._login_animation_tick)

    def _login_animation_tick(self):
        if not self._anim_running or not hasattr(self,'_login_anim_state'):
            return
        try:
            canvas,particles,ring,glow,line,t=self._login_anim_state
            if not canvas.winfo_exists(): return
            w=max(canvas.winfo_width(),1); h=max(canvas.winfo_height(),1)
            t += 0.055
            for i,(item,rx,ry,r,speed) in enumerate(particles):
                x=(rx*w + __import__('math').sin(t*speed + i)*28)
                y=(ry*h + __import__('math').cos(t*speed*0.8 + i)*22)
                canvas.coords(item,x-r,y-r,x+r,y+r)
            cx=w*0.72; cy=h*0.62
            pulse=8+__import__('math').sin(t*1.8)*6
            canvas.coords(glow,cx-pulse,cy-pulse,cx+pulse,cy+pulse)
            size=150+__import__('math').sin(t*0.9)*12
            canvas.coords(ring,cx-size/2,cy-size/2,cx+size/2,cy+size/2)
            lx=(w*0.18)+(w*0.58)*((__import__('math').sin(t*0.75)+1)/2)
            canvas.coords(line,lx,h*0.77,lx+180,h*0.77+3)
            self._login_anim_state=(canvas,particles,ring,glow,line,t)
            self.schedule(40,self._login_animation_tick)
        except tk.TclError:
            return

    def signup(self):
        self.clear()
        root=tk.Frame(self,bg=NAVY); root.pack(fill="both",expand=True)
        box=panel(root); box.place(relx=.5,rely=.5,anchor="center",width=480,height=520)
        tk.Label(box,text="Buat Akun",bg=WHITE,fg=TEXT,font=(FONT,26,"bold")).pack(pady=(32,4))
        tk.Label(box,text="Daftarkan anggota baru perpustakaan",bg=WHITE,fg=MUTED,font=(FONT,10)).pack(pady=(0,25))
        form=tk.Frame(box,bg=WHITE); form.pack(fill="x",padx=48); es={}
        for label,key,show in [("Username","u",None),("Email","e",None),("Password","p","•"),("Konfirmasi Password","c","•")]:
            tk.Label(form,text=label,bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
            e=tk.Entry(form,show=show,bg="#F8FAFD",font=(FONT,10),relief="solid",bd=1)
            e.pack(fill="x",ipady=8,pady=(4,13)); es[key]=e
        def daftar():
            u,e,p,c=es["u"].get().strip(),es["e"].get().strip(),es["p"].get(),es["c"].get()
            data=users()
            if not u or not e or not p: messagebox.showwarning("Pendaftaran","Semua field wajib diisi."); return
            if p!=c: messagebox.showerror("Pendaftaran","Konfirmasi password tidak sama."); return
            if u in data: messagebox.showerror("Pendaftaran","Username sudah digunakan."); return
            if any(v.get("email","").lower()==e.lower() for v in data.values()):
                messagebox.showerror("Pendaftaran","Email sudah digunakan."); return
            data[u]={"email":e,"password":phash(p)}; save_users(data)
            messagebox.showinfo("Berhasil","Akun berhasil dibuat."); self.login()
        button(form,"DAFTAR",daftar).pack(fill="x")
        button(form,"Kembali ke Login",self.login,NAVY2).pack(fill="x",pady=10)

    def dashboard(self):
        self._anim_running = False
        self.page="dashboard"; self.clear()
        side=tk.Frame(self,bg=NAVY,width=235); side.pack(side="left",fill="y"); side.pack_propagate(False)
        tk.Label(side,text="PerBENROY.COM",bg=NAVY,fg="#E53935",font=(FONT,19,"bold")).pack(pady=(28,3))
        tk.Label(side,text="DIGITAL LIBRARY",bg=NAVY,fg="#9DB7D8",font=(FONT,9,"bold")).pack(pady=(0,35))
        nav=tk.Frame(side,bg=NAVY); nav.pack(fill="x",padx=12)
        self.nav_buttons={}
        self._nav_pages=[("⌂","Beranda","main"),("▣","Dashboard","dashboard"),("▤","Manajemen Buku","books"),("↔","Peminjaman","borrowings"),("♙","Users","users")]
        for icon,text,page in self._nav_pages:
            active=page==self.page
            b=tk.Button(nav,text=icon+"   "+text,bg=BLUE if active else NAVY,fg=WHITE,
                activebackground=BLUE2,activeforeground=WHITE,bd=0,anchor="w",padx=17,pady=12,font=(FONT,10,"bold"),
                command=lambda x=page:self.show(x),cursor="hand2")
            b.pack(fill="x",pady=3)
            self.nav_buttons[page]=b
        # Simpan warna awal agar indikator aktif dapat berpindah dengan halus.
        self._active_nav_page=self.page
        bot=tk.Frame(side,bg=NAVY); bot.pack(side="bottom",fill="x",padx=15,pady=20)
        tk.Frame(bot,bg="#28466A",height=1).pack(fill="x",pady=(0,15))
        tk.Label(bot,text="●  "+str(self.current_user),bg=NAVY,fg=WHITE,font=(FONT,10,"bold"),anchor="w").pack(fill="x",pady=(0,10))
        button(bot,"↪  Keluar",self.logout,DANGER).pack(fill="x")
        self.content=tk.Frame(self,bg=BG); self.content.pack(side="left",fill="both",expand=True)
        self.render_dashboard()

    def _hex_rgb(self, value):
        value=value.lstrip("#")
        return tuple(int(value[i:i+2],16) for i in (0,2,4))

    def _rgb_hex(self, rgb):
        return "#%02x%02x%02x" % tuple(max(0,min(255,int(v))) for v in rgb)

    def _animate_nav_color(self, old_page, new_page, step=0):
        if not hasattr(self,"nav_buttons"): return
        old_btn=self.nav_buttons.get(old_page)
        new_btn=self.nav_buttons.get(new_page)
        if not old_btn or not new_btn: return

        steps=7
        t=min(1.0,step/steps)
        # Smooth ease-in-out agar perpindahan warna terasa lembut.
        ease=t*t*(3-2*t)
        old_a=self._hex_rgb(BLUE); old_b=self._hex_rgb(NAVY)
        new_a=self._hex_rgb(NAVY); new_b=self._hex_rgb(BLUE)
        old_color=tuple(old_a[i]+(old_b[i]-old_a[i])*ease for i in range(3))
        new_color=tuple(new_a[i]+(new_b[i]-new_a[i])*ease for i in range(3))
        try:
            old_btn.configure(bg=self._rgb_hex(old_color))
            new_btn.configure(bg=self._rgb_hex(new_color))
        except tk.TclError:
            return
        if step < steps:
            self.schedule(18,lambda:self._animate_nav_color(old_page,new_page,step+1))
        else:
            self._active_nav_page=new_page

    def _update_nav_active(self,page,animate=True):
        if not hasattr(self,"nav_buttons"): return
        previous=getattr(self,"_active_nav_page",None)
        if page not in self.nav_buttons: return
        if previous==page:
            for p,b in self.nav_buttons.items():
                b.configure(bg=BLUE if p==page else NAVY)
            return
        if not animate or previous not in self.nav_buttons:
            for p,b in self.nav_buttons.items():
                b.configure(bg=BLUE if p==page else NAVY)
            self._active_nav_page=page
            return
        # Pastikan semua tombol selain pasangan transisi kembali ke warna normal.
        for p,b in self.nav_buttons.items():
            if p not in (previous,page): b.configure(bg=NAVY)
        self._animate_nav_color(previous,page,0)

    def show(self,page):
        # Navigasi tidak boleh memanggil dashboard() lagi dari dalam dashboard().
        # Cukup render isi halaman pada content yang sudah dibuat.
        self.stop_animations()
        self.page = page
        if page=="main":
            self.main_page()
        elif page=="dashboard":
            self._update_nav_active(page)
            self.render_dashboard()
        elif page=="books":
            self._update_nav_active(page)
            self.render_books()
        elif page=="borrowings":
            self._update_nav_active(page)
            self.render_borrowings()
        elif page=="users":
            self._update_nav_active(page)
            self.render_users()

    def main_page(self):
        """Beranda publik PerBENROY.COM dengan layout dua kolom yang rapi."""
        self._anim_running = True
        self.clear()
        self.page = "main"

        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)

        # ==================== NAVBAR ====================
        nav = tk.Frame(root, bg=NAVY, height=70)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        brand = tk.Frame(nav, bg=NAVY)
        brand.pack(side="left", padx=34)
        tk.Label(brand, text="PerBENROY.COM", bg=NAVY, fg="#E53935",
                 font=(FONT, 20, "bold")).pack(side="left")
        tk.Label(brand, text="PERPUSTAKAAN DIGITAL", bg=NAVY, fg="#8FA9C9",
                 font=(FONT, 8, "bold")).pack(side="left", padx=(12, 0), pady=(6, 0))

        nav_right = tk.Frame(nav, bg=NAVY)
        nav_right.pack(side="right", padx=30)
        if self.current_user:
            tk.Label(nav_right, text=f"●  {self.current_user}", bg=NAVY,
                     fg="#DCE7F5", font=(FONT, 10, "bold")).pack(side="left", padx=(0, 14))
            button(nav_right, "Dashboard  →", self.dashboard, BLUE).pack(side="left", padx=4)
            button(nav_right, "Keluar", self.logout, DANGER).pack(side="left", padx=4)
        else:
            button(nav_right, "Masuk", self.login, NAVY2).pack(side="left", padx=4)
            button(nav_right, "Daftar", self.signup, BLUE).pack(side="left", padx=4)

        # ==================== HERO AREA ====================
        hero = tk.Frame(root, bg=BG)
        hero.pack(fill="both", expand=True, padx=38, pady=(26, 18))

        # Kolom kiri: headline dan CTA.
        left = tk.Frame(hero, bg=BG)
        left.place(relx=0.00, rely=0.03, relwidth=0.51, relheight=0.94)

        badge = tk.Label(left, text="✦  SMART LIBRARY SYSTEM", bg="#E7F0FB", fg=BLUE,
                         font=(FONT, 9, "bold"), padx=12, pady=6)
        badge.pack(anchor="w", pady=(8, 18))

        tk.Label(left, text="Kelola Perpustakaan", bg=BG, fg=TEXT,
                 font=(FONT, 34, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text="Dengan Lebih Mudah.", bg=BG, fg="#D93636",
                 font=(FONT, 34, "bold"), anchor="w").pack(anchor="w")

        tk.Label(left,
                 text="Satu aplikasi untuk mengelola koleksi buku, peminjaman,\n"
                      "dan anggota PerBENROY.COM secara cepat, sederhana, dan tertata.",
                 bg=BG, fg=MUTED, font=(FONT, 11), justify="left",
                 anchor="w").pack(anchor="w", pady=(16, 22))

        actions = tk.Frame(left, bg=BG)
        actions.pack(anchor="w", pady=(0, 22))
        button(actions, "Mulai Sekarang  →",
               self.login if not self.current_user else self.dashboard, BLUE).pack(side="left", padx=(0, 10))
        button(actions, "Buat Akun", self.signup, NAVY2).pack(side="left")

        # Statistik ringkas di bawah CTA agar area kiri tidak kosong.
        quick = tk.Frame(left, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        quick.pack(fill="x", padx=(0, 28), pady=(2, 0))
        bs, us, br = books(), users(), borrows()
        active = len([x for x in br if x.get("status") == "Dipinjam"])
        quick_data = [("KOLEKSI", len(bs), BLUE), ("ANGGOTA", len(us), SUCCESS),
                      ("SEDANG DIPINJAM", active, WARNING)]
        for i, (label, value, color) in enumerate(quick_data):
            cell = tk.Frame(quick, bg=WHITE)
            cell.pack(side="left", fill="both", expand=True, padx=(16 if i == 0 else 8, 8), pady=13)
            tk.Label(cell, text="●", bg=WHITE, fg=color, font=(FONT, 9, "bold")).pack(anchor="w")
            value_label = tk.Label(cell, text="0", bg=WHITE, fg=TEXT, font=(FONT, 19, "bold"))
            value_label.pack(anchor="w")
            tk.Label(cell, text=label, bg=WHITE, fg=MUTED, font=(FONT, 7, "bold")).pack(anchor="w")
            self.schedule(250 + i * 80, lambda lbl=value_label, target=value: self._animate_number(lbl, target))

        tk.Label(left, text="✓  Data tersimpan otomatis    ✓  Antarmuka sederhana & responsif",
                 bg=BG, fg=MUTED, font=(FONT, 8, "bold"), anchor="w").pack(anchor="w", pady=(13, 0))

        # Kolom kanan: satu showcase panel agar semua elemen visual berada pada satu grid.
        right = tk.Frame(hero, bg=BG)
        right.place(relx=0.54, rely=0.00, relwidth=0.46, relheight=1.0)

        showcase = tk.Frame(right, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        showcase.place(relx=0.02, rely=0.03, relwidth=0.95, relheight=0.90)

        tk.Label(showcase, text="KOLEKSI UNGGULAN", bg=WHITE, fg=MUTED,
                 font=(FONT, 8, "bold")).place(relx=0.08, rely=0.07, anchor="w")
        tk.Label(showcase, text="Perpustakaan dalam satu tampilan",
                 bg=WHITE, fg=TEXT, font=(FONT, 15, "bold")).place(relx=0.08, rely=0.13, anchor="w")
        tk.Label(showcase, text="Visual, ringkas, dan mudah dipantau.",
                 bg=WHITE, fg=MUTED, font=(FONT, 9)).place(relx=0.08, rely=0.19, anchor="w")

        # Canvas animasi berada di area kosong kanan panel, bukan menutupi teks utama.
        anim_canvas = tk.Canvas(showcase, bg=WHITE, bd=0, highlightthickness=0)
        anim_canvas.place(relx=0.04, rely=0.25, relwidth=0.92, relheight=0.52)

        # Footer kecil pada panel kanan.
        status = tk.Frame(showcase, bg="#F7FAFE", highlightbackground="#E4EBF4", highlightthickness=1)
        status.place(relx=0.08, rely=0.82, relwidth=0.84, relheight=0.11)
        tk.Label(status, text="●", bg="#F7FAFE", fg=SUCCESS, font=(FONT, 9, "bold")).pack(side="left", padx=(12, 6))
        tk.Label(status, text="Sistem siap digunakan", bg="#F7FAFE", fg=TEXT,
                 font=(FONT, 9, "bold")).pack(side="left")
        tk.Label(status, text="PerBENROY.COM", bg="#F7FAFE", fg=MUTED,
                 font=(FONT, 8)).pack(side="right", padx=12)

        # ==================== FEATURE BAR ====================
        features = tk.Frame(root, bg=WHITE, height=112, highlightbackground=BORDER, highlightthickness=1)
        features.pack(fill="x", side="bottom")
        features.pack_propagate(False)

        feature_data = [
            ("▤", "Koleksi Buku", "Kelola judul, penulis, tahun, dan stok.", BLUE),
            ("↔", "Peminjaman", "Catat proses pinjam dan pengembalian.", SUCCESS),
            ("♙", "Anggota", "Kelola pengguna dan akses perpustakaan.", NAVY2),
        ]
        for i, (icon, title_text, desc, color) in enumerate(feature_data):
            card = tk.Frame(features, bg=WHITE)
            card.pack(side="left", fill="both", expand=True, padx=(38 if i == 0 else 18, 18), pady=18)
            tk.Label(card, text=icon, bg="#F1F6FC", fg=color, font=(FONT, 18, "bold"),
                     width=3, pady=6).pack(side="left", padx=(0, 12))
            info = tk.Frame(card, bg=WHITE)
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=title_text, bg=WHITE, fg=TEXT,
                     font=(FONT, 10, "bold")).pack(anchor="w", pady=(5, 2))
            tk.Label(info, text=desc, bg=WHITE, fg=MUTED, font=(FONT, 8),
                     wraplength=230, justify="left").pack(anchor="w")

        # Animasi tetap berjalan terus selama Beranda aktif.
        self._start_landing_animation(anim_canvas)

    def _start_landing_animation(self, canvas):
        import math
        # Semua elemen animasi berada di satu Canvas agar CPU usage tetap rendah.
        particles=[]
        for i in range(18):
            x=35+(i*67)%430; y=35+(i*91)%390
            r=2+(i%3)
            item=canvas.create_oval(x-r,y-r,x+r,y+r,fill="#C7DDF4",outline="")
            particles.append([item,float(x),float(y),r,0.35+(i%5)*0.08,i*0.7])
        # Dua orb utama dan orbit ring.
        orb=canvas.create_oval(0,0,180,180,fill="#E6F0FC",outline="")
        orb2=canvas.create_oval(0,0,92,92,fill="#D7E8FA",outline="")
        ring1=canvas.create_oval(0,0,250,250,outline="#C5DDF5",width=2)
        ring2=canvas.create_oval(0,0,180,180,outline="#D7E8FA",width=2)
        # Kartu buku mengambang.
        cards=[]
        for i,(title,color) in enumerate([("BENROY",BLUE),("BOOK",NAVY2),("READ",SUCCESS)]):
            x=70+i*125; y=150+(i%2)*105
            shadow=canvas.create_rectangle(x+5,y+7,x+92,y+125,fill="#D8E5F3",outline="")
            card=canvas.create_rectangle(x,y,x+87,y+118,fill=color,outline="")
            stripe=canvas.create_rectangle(x+10,y+14,x+77,y+20,fill="#FFFFFF",outline="")
            txt=canvas.create_text(x+43,y+64,text=title,fill=WHITE,font=(FONT,10,"bold"))
            cards.append([shadow,card,stripe,txt,float(x),float(y),i*2.0])
        self._landing_anim_state=(canvas,particles,orb,orb2,ring1,ring2,cards,0.0)
        self.schedule(35,self._landing_animation_tick)

    def _landing_animation_tick(self):
        import math
        if not self._anim_running or not hasattr(self,'_landing_anim_state'):
            return
        try:
            canvas,particles,orb,orb2,ring1,ring2,cards,t=self._landing_anim_state
            if not canvas.winfo_exists(): return
            w=max(canvas.winfo_width(),500); h=max(canvas.winfo_height(),420)
            t += 0.045
            cx=w*0.57; cy=h*0.46
            pulse=95+math.sin(t*1.25)*13
            canvas.coords(orb,cx-pulse,cy-pulse,cx+pulse,cy+pulse)
            pulse2=46+math.sin(t*1.7+1)*8
            canvas.coords(orb2,cx+125-pulse2,cy+90-pulse2,cx+125+pulse2,cy+90+pulse2)
            r1=125+math.sin(t*0.65)*18
            canvas.coords(ring1,cx-r1,cy-r1,cx+r1,cy+r1)
            r2=90+math.cos(t*0.9)*13
            canvas.coords(ring2,cx+120-r2,cy+85-r2,cx+120+r2,cy+85+r2)
            for item,x,y,r,speed,phase in particles:
                nx=x+math.sin(t*speed+phase)*25
                ny=y+math.cos(t*speed*0.75+phase)*18
                canvas.coords(item,nx-r,ny-r,nx+r,ny+r)
            for shadow,card,stripe,txt,x,y,phase in cards:
                yy=y+math.sin(t*1.35+phase)*16
                xx=x+math.cos(t*0.65+phase)*7
                for obj in (shadow,card,stripe):
                    pass
                canvas.coords(shadow,xx+5,yy+7,xx+92,yy+125)
                canvas.coords(card,xx,yy,xx+87,yy+118)
                canvas.coords(stripe,xx+10,yy+14,xx+77,yy+20)
                canvas.coords(txt,xx+43,yy+64)
            self._landing_anim_state=(canvas,particles,orb,orb2,ring1,ring2,cards,t)
            self.schedule(35,self._landing_animation_tick)
        except tk.TclError:
            return

    def header(self,title,sub):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content,text=title,bg=BG,fg=TEXT,font=(FONT,24,"bold")).pack(anchor="w",padx=28,pady=(25,3))
        tk.Label(self.content,text=sub,bg=BG,fg=MUTED,font=(FONT,10)).pack(anchor="w",padx=28,pady=(0,15))

    def stat(self,parent,title,value,icon,color):
        c=panel(parent); box=tk.Frame(c,bg=color,width=48,height=48); box.pack(side="left",padx=14,pady=14); box.pack_propagate(False)
        tk.Label(box,text=icon,bg=color,fg=WHITE,font=(FONT,18,"bold")).pack(expand=True)
        f=tk.Frame(c,bg=WHITE); f.pack(side="left",pady=10)
        tk.Label(f,text=title,bg=WHITE,fg=MUTED,font=(FONT,9)).pack(anchor="w")
        tk.Label(f,text=str(value),bg=WHITE,fg=TEXT,font=(FONT,19,"bold")).pack(anchor="w")
        return c

    def render_dashboard(self):
        self.header("Dashboard","Ringkasan aktivitas PerBENROY.COM.")
        bs,us,br=books(),users(),borrows()
        active=[x for x in br if x.get("status")=="Dipinjam"]
        row=tk.Frame(self.content,bg=BG); row.pack(fill="x",padx=28)
        vals=[("Total Buku",len(bs),"▤",BLUE),("Stok Tersedia",sum(int(x.get("stok",0)) for x in bs),"◈",SUCCESS),
              ("Sedang Dipinjam",len(active),"↔",WARNING),("Total Anggota",len(us),"♙",NAVY2)]
        for i,v in enumerate(vals):
            row.grid_columnconfigure(i,weight=1); self.stat(row,*v).grid(row=0,column=i,sticky="ew",padx=(0 if i==0 else 6,6 if i<3 else 0))
        # ---------- Koleksi buku visual ----------
        collection_title = tk.Frame(self.content, bg=BG)
        collection_title.pack(fill="x", padx=28, pady=(18, 0))
        tk.Label(collection_title, text="Koleksi Buku", bg=BG, fg=TEXT,
                 font=(FONT, 15, "bold")).pack(side="left")
        tk.Label(collection_title, text="Koleksi terbaru dan stok saat ini", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side="left", padx=12, pady=(4, 0))

        books_area = tk.Frame(self.content, bg=BG)
        books_area.pack(fill="x", padx=28, pady=(10, 0))
        visible_books = bs[:5]
        for i, book in enumerate(visible_books):
            books_area.grid_columnconfigure(i, weight=1)
            card = tk.Frame(books_area, bg=WHITE, highlightbackground=BORDER,
                            highlightthickness=1, cursor="hand2")
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 5, 5))
            cover = tk.Canvas(card, width=70, height=78, bg="#EAF2FC", highlightthickness=0)
            cover.pack(side="left", padx=12, pady=12)
            # Cover ilustratif dibuat dengan Canvas sehingga tidak membutuhkan file gambar eksternal.
            cover.create_rectangle(10, 8, 60, 70, fill=(BLUE if i % 2 == 0 else NAVY2), outline="")
            cover.create_rectangle(10, 8, 60, 17, fill=("#E53935" if i % 3 == 0 else "#4FA3FF"), outline="")
            cover.create_text(35, 39, text="BOOK", fill=WHITE, font=(FONT, 8, "bold"))
            info = tk.Frame(card, bg=WHITE)
            info.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 10))
            tk.Label(info, text=str(book.get("judul", "Tanpa Judul")), bg=WHITE, fg=TEXT,
                     font=(FONT, 9, "bold"), wraplength=120, justify="left", anchor="w").pack(anchor="w")
            tk.Label(info, text=str(book.get("penulis", "-")), bg=WHITE, fg=MUTED,
                     font=(FONT, 8), wraplength=120, justify="left").pack(anchor="w", pady=(3, 4))
            stok = int(book.get("stok", 0))
            stok_color = SUCCESS if stok > 0 else DANGER
            tk.Label(info, text=f"Stok: {stok}", bg=WHITE, fg=stok_color,
                     font=(FONT, 8, "bold")).pack(anchor="w")

        lower=tk.Frame(self.content,bg=BG); lower.pack(fill="both",expand=True,padx=28,pady=20)
        left=panel(lower); left.pack(side="left",fill="both",expand=True,padx=(0,8))
        tk.Label(left,text="Peminjaman Terbaru",bg=WHITE,fg=TEXT,font=(FONT,14,"bold")).pack(anchor="w",padx=18,pady=15)
        tree=ttk.Treeview(left,columns=("u","b","s"),show="headings",height=6)
        for c,h,w in [("u","Anggota",130),("b","Buku",260),("s","Status",100)]:
            tree.heading(c,text=h); tree.column(c,width=w,anchor="w")
        tree.tag_configure("odd", background="#F7FAFE")
        tree.tag_configure("even", background=WHITE)
        tree.pack(fill="both",expand=True,padx=15,pady=(0,15))
        for idx, x in enumerate(reversed(br[-8:])):
            tree.insert("",0,values=(x.get("username"),x.get("judul"),x.get("status")),tags=("odd" if idx % 2 else "even",))
        right=panel(lower); right.pack(side="left",fill="both",padx=(8,0),ipadx=10)
        tk.Label(right,text="Akses Cepat",bg=WHITE,fg=TEXT,font=(FONT,14,"bold")).pack(anchor="w",padx=20,pady=(18,12))
        button(right,"+  Tambah Buku",lambda:self.book_form()).pack(fill="x",padx=20,pady=5)
        button(right,"↔  Peminjaman Baru",lambda:self.borrow_form(),NAVY2).pack(fill="x",padx=20,pady=5)
        button(right,"♙  Kelola Users",lambda:self.show("users"),"#315B86").pack(fill="x",padx=20,pady=5)

    def render_books(self):
        self.header("Manajemen Buku","Tambah, ubah, hapus, dan cari koleksi buku.")
        top=tk.Frame(self.content,bg=BG); top.pack(fill="x",padx=28,pady=(0,12))
        q=tk.StringVar(); ent=tk.Entry(top,textvariable=q,bg=WHITE,fg=TEXT,relief="solid",bd=1); ent.pack(side="left",fill="x",expand=True,ipady=8)
        button(top,"+ Tambah Buku",self.book_form).pack(side="left",padx=(10,0))
        body=panel(self.content); body.pack(fill="both",expand=True,padx=28,pady=(0,12))
        tree=ttk.Treeview(body,columns=("id","j","p","t","s"),show="headings")
        for c,h,w in [("id","ID",50),("j","Judul Buku",300),("p","Penulis",230),("t","Tahun",90),("s","Stok",80)]:
            tree.heading(c,text=h); tree.column(c,width=w,anchor="w")
        tree.pack(fill="both",expand=True,padx=15,pady=15)
        def fill(*a):
            tree.delete(*tree.get_children()); query=q.get().lower()
            for b in books():
                if query in (str(b.get("judul",""))+" "+str(b.get("penulis",""))).lower():
                    tree.insert("", "end",values=(b["id"],b["judul"],b["penulis"],b["tahun"],b["stok"]))
        q.trace_add("write",fill); fill()
        actions=tk.Frame(self.content,bg=BG); actions.pack(fill="x",padx=28,pady=(0,18))
        def sel():
            s=tree.selection()
            if not s: messagebox.showwarning("Buku","Pilih buku terlebih dahulu."); return None
            return int(tree.item(s[0],"values")[0])
        button(actions,"Edit",lambda:self.book_form(sel())).pack(side="left")
        button(actions,"Hapus",lambda:self.del_book(sel()),DANGER).pack(side="left",padx=8)

    def book_form(self,bid=None):
        data=books(); old=next((x for x in data if int(x["id"])==int(bid)),None) if bid else None
        w=tk.Toplevel(self); w.title("Buku"); w.geometry("430x470"); w.configure(bg=WHITE); w.transient(self); w.grab_set()
        tk.Label(w,text="Edit Buku" if old else "Tambah Buku",bg=WHITE,fg=TEXT,font=(FONT,21,"bold")).pack(pady=(25,20))
        form=tk.Frame(w,bg=WHITE); form.pack(fill="x",padx=45); es={}
        for label,key in [("Judul","judul"),("Penulis","penulis"),("Tahun","tahun"),("Stok","stok")]:
            tk.Label(form,text=label,bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
            e=tk.Entry(form,bg="#F8FAFD",relief="solid",bd=1); e.insert(0,str(old.get(key,"") if old else "")); e.pack(fill="x",ipady=7,pady=(4,12)); es[key]=e
        def save():
            try: stock=int(es["stok"].get()); assert stock>=0
            except: messagebox.showerror("Buku","Stok harus angka >= 0.",parent=w); return
            if not all(es[k].get().strip() for k in ("judul","penulis","tahun")): messagebox.showwarning("Buku","Semua data wajib diisi.",parent=w); return
            if old: old.update(judul=es["judul"].get().strip(),penulis=es["penulis"].get().strip(),tahun=es["tahun"].get().strip(),stok=stock)
            else: data.append({"id":nid(data),"judul":es["judul"].get().strip(),"penulis":es["penulis"].get().strip(),"tahun":es["tahun"].get().strip(),"stok":stock})
            save_books(data); w.destroy(); self.render_books()
        button(w,"Simpan",save).pack(fill="x",padx=45,pady=(5,8)); button(w,"Batal",w.destroy,NAVY2).pack(fill="x",padx=45)

    def del_book(self,bid):
        if bid is None:return
        if any(int(x.get("book_id",0))==bid and x.get("status")=="Dipinjam" for x in borrows()):
            messagebox.showerror("Buku","Buku sedang dipinjam."); return
        if messagebox.askyesno("Konfirmasi","Hapus buku?"):
            save_books([x for x in books() if int(x["id"])!=bid]); self.render_books()

    def render_borrowings(self):
        self.header("Peminjaman","Kelola transaksi peminjaman dan pengembalian.")
        top=tk.Frame(self.content,bg=BG); top.pack(fill="x",padx=28,pady=(0,12)); button(top,"+ Peminjaman Baru",self.borrow_form).pack(side="left")
        body=panel(self.content); body.pack(fill="both",expand=True,padx=28,pady=(0,12))
        tree=ttk.Treeview(body,columns=("id","u","b","p","k","s"),show="headings")
        for c,h,w in [("id","ID",45),("u","Anggota",110),("b","Buku",230),("p","Pinjam",105),("k","Kembali",105),("s","Status",100)]:
            tree.heading(c,text=h); tree.column(c,width=w,anchor="w")
        tree.pack(fill="both",expand=True,padx=15,pady=15)
        for x in borrows(): tree.insert("", "end",values=(x["id"],x["username"],x["judul"],x["tanggal_pinjam"],x["tanggal_kembali"],x["status"]))
        act=tk.Frame(self.content,bg=BG); act.pack(fill="x",padx=28,pady=(0,18))
        def sel():
            s=tree.selection()
            if not s: messagebox.showwarning("Peminjaman","Pilih transaksi."); return None
            return int(tree.item(s[0],"values")[0])
        button(act,"Edit",lambda:self.borrow_form(sel())).pack(side="left"); button(act,"Hapus",lambda:self.del_borrow(sel()),DANGER).pack(side="left",padx=8)

    def borrow_form(self,bid=None):
        data=borrows(); old=next((x for x in data if int(x["id"])==int(bid)),None) if bid else None
        bs=books(); us=list(users())
        w=tk.Toplevel(self); w.title("Peminjaman"); w.geometry("460x540"); w.configure(bg=WHITE); w.transient(self); w.grab_set()
        tk.Label(w,text="Edit Peminjaman" if old else "Peminjaman Baru",bg=WHITE,fg=TEXT,font=(FONT,21,"bold")).pack(pady=(25,18))
        f=tk.Frame(w,bg=WHITE); f.pack(fill="x",padx=45)
        uv=tk.StringVar(value=old["username"] if old else (us[0] if us else "")); choices=[f'{b["id"]} - {b["judul"]}' for b in bs]
        bv=tk.StringVar(value=next((f'{b["id"]} - {b["judul"]}' for b in bs if old and int(b["id"])==int(old["book_id"])),choices[0] if choices else ""))
        sv=tk.StringVar(value=old["status"] if old else "Dipinjam"); es={}
        for lab,var,vals in [("Anggota",uv,us),("Buku",bv,choices),("Status",sv,["Dipinjam","Kembali"])]:
            tk.Label(f,text=lab,bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
            c=ttk.Combobox(f,textvariable=var,values=vals,state="readonly"); c.pack(fill="x",ipady=5,pady=(4,12))
        for lab,key,default in [("Tanggal Pinjam","p",old["tanggal_pinjam"] if old else datetime.now().strftime("%Y-%m-%d")),("Tanggal Kembali","k",old["tanggal_kembali"] if old else (datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d"))]:
            tk.Label(f,text=lab,bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
            e=tk.Entry(f,bg="#F8FAFD",relief="solid",bd=1); e.insert(0,default); e.pack(fill="x",ipady=7,pady=(4,12)); es[key]=e
        def save():
            if not us or not bs:
                messagebox.showerror("Peminjaman","User dan buku harus tersedia.",parent=w); return
            try:
                bookid=int(bv.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Peminjaman","Buku tidak valid.",parent=w); return
            chosen=next((x for x in bs if int(x["id"])==bookid),None)
            if chosen is None:
                messagebox.showerror("Peminjaman","Buku tidak ditemukan.",parent=w); return
            status=sv.get()
            if old:
                oldstatus=old["status"]; oldbid=int(old["book_id"])
                oldbook=next((x for x in bs if int(x["id"])==oldbid),None)
                # Validasi stok buku tujuan sebelum mengubah stok buku lama.
                same_book = oldbook is not None and int(oldbook["id"]) == bookid
                if status=="Dipinjam" and not same_book and chosen["stok"]<=0:
                    messagebox.showerror("Peminjaman","Stok buku tujuan habis.",parent=w)
                    return
                # Kembalikan stok buku lama bila transaksi sebelumnya aktif.
                if oldstatus=="Dipinjam" and oldbook is not None:
                    oldbook["stok"] += 1
                # Jika hasil akhirnya masih dipinjam, ambil satu stok dari buku tujuan.
                if status=="Dipinjam":
                    chosen["stok"] -= 1
                old.update(username=uv.get(),book_id=bookid,judul=chosen["judul"],
                           tanggal_pinjam=es["p"].get().strip(),tanggal_kembali=es["k"].get().strip(),status=status)
            else:
                if status=="Dipinjam":
                    if chosen["stok"]<=0:
                        messagebox.showerror("Peminjaman","Stok habis.",parent=w); return
                    chosen["stok"]-=1
                data.append({"id":nid(data),"username":uv.get(),"book_id":bookid,"judul":chosen["judul"],
                             "tanggal_pinjam":es["p"].get().strip(),"tanggal_kembali":es["k"].get().strip(),"status":status})
            save_books(bs); save_borrows(data); w.destroy(); self.render_borrowings()
        button(w,"Simpan",save).pack(fill="x",padx=45,pady=(5,8)); button(w,"Batal",w.destroy,NAVY2).pack(fill="x",padx=45)

    def del_borrow(self,bid):
        if bid is None:return
        data=borrows(); old=next((x for x in data if int(x["id"])==bid),None)
        if not old:return
        if not messagebox.askyesno("Konfirmasi","Hapus transaksi?"):return
        if old["status"]=="Dipinjam":
            bs=books()
            for b in bs:
                if int(b["id"])==int(old["book_id"]):b["stok"]+=1
            save_books(bs)
        save_borrows([x for x in data if int(x["id"])!=bid]); self.render_borrowings()

    def render_users(self):
        self.header("Users / Anggota","Kelola akun pengguna perpustakaan.")
        body=panel(self.content); body.pack(fill="both",expand=True,padx=28,pady=(0,12))
        tree=ttk.Treeview(body,columns=("u","e"),show="headings"); tree.heading("u",text="Username"); tree.heading("e",text="Email")
        tree.column("u",width=250); tree.column("e",width=450); tree.pack(fill="both",expand=True,padx=15,pady=15)
        for u,d in users().items():tree.insert("", "end",values=(u,d.get("email","")))
        act=tk.Frame(self.content,bg=BG); act.pack(fill="x",padx=28,pady=(0,18))
        def sel():
            s=tree.selection()
            if not s:messagebox.showwarning("Users","Pilih user.");return None
            return tree.item(s[0],"values")[0]
        button(act,"Edit User",lambda:self.user_form(sel())).pack(side="left");button(act,"Hapus User",lambda:self.del_user(sel()),DANGER).pack(side="left",padx=8)

    def user_form(self,name):
        if not name:return
        data=users(); rec=data.get(name)
        if not rec:return
        w=tk.Toplevel(self);w.title("Edit User");w.geometry("430x390");w.configure(bg=WHITE);w.transient(self);w.grab_set()
        tk.Label(w,text="Edit User",bg=WHITE,fg=TEXT,font=(FONT,22,"bold")).pack(pady=(28,20))
        f=tk.Frame(w,bg=WHITE);f.pack(fill="x",padx=45)
        fields=[]
        for lab,val,show in [("Username",name,None),("Email",rec.get("email",""),None),("Password baru (opsional)","", "•")]:
            tk.Label(f,text=lab,bg=WHITE,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
            e=tk.Entry(f,show=show,bg="#F8FAFD",relief="solid",bd=1);e.insert(0,val);e.pack(fill="x",ipady=7,pady=(4,12));fields.append(e)
        def save():
            nu,em,np=fields[0].get().strip(),fields[1].get().strip(),fields[2].get()
            if not nu or not em:return
            if nu!=name and nu in data:messagebox.showerror("Users","Username sudah dipakai.",parent=w);return
            data.pop(name);rec["email"]=em
            if np:rec["password"]=phash(np)
            data[nu]=rec;save_users(data)
            if self.current_user==name:self.current_user=nu
            w.destroy();self.dashboard()
        button(w,"Simpan",save).pack(fill="x",padx=45,pady=(5,8));button(w,"Batal",w.destroy,NAVY2).pack(fill="x",padx=45)

    def del_user(self,name):
        if not name:return
        if name==self.current_user:messagebox.showwarning("Users","User yang sedang login tidak dapat dihapus.");return
        if messagebox.askyesno("Konfirmasi","Hapus user?"):
            d=users();d.pop(name,None);save_users(d);self.render_users()

    def logout(self):
        if messagebox.askyesno("Logout","Yakin ingin keluar?"):self.login()

if __name__=="__main__":
    App().mainloop()
