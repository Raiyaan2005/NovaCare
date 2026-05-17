import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib

# ── Appearance ───────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design tokens – identical to hospital.py ─────────────────────────────────
BG_ROOT      = "#07070f"
BG_PANEL     = "#0b0b19"
BG_FRAME     = "#111122"
BORDER_COLOR = "#1a1a35"
ACCENT       = "#5b6cf9"
ACCENT_DARK  = "#4a5be0"
TEXT_PRIMARY = "#dce4f0"
TEXT_MUTED   = "#4c5580"
TEXT_BRIGHT  = "#ffffff"
BTN_FG       = "#5b6cf9"
BTN_HOVER    = "#4a5be0"

_FF       = "Helvetica Neue"
FONT_BTN  = (_FF, 13, "bold")
FONT_LABEL = (_FF, 13)
FONT_ENTRY = (_FF, 13)
FONT_SMALL = (_FF, 11)

DB_CONFIG = dict(host="localhost", user="root", password="moRRison@123", database="hospital")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _connect():
    return mysql.connector.connect(**DB_CONFIG)


class AuthApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("NovaCare")
        self.geometry("460x520+530+150")
        self.configure(fg_color=BG_ROOT)
        self.resizable(False, False)

        self._ensure_users_table()
        self._build_header()
        self._build_card()
        self._show_mode("login")

    # ── Database setup ────────────────────────────────────────────────────────
    def _ensure_users_table(self):
        try:
            conn = _connect()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INT AUTO_INCREMENT PRIMARY KEY,
                    username      VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(64)  NOT NULL,
                    full_name     VARCHAR(100) DEFAULT ''
                )
            """)
            # Add user_id column to appointments if it doesn't already exist
            try:
                cur.execute("ALTER TABLE appointments ADD COLUMN user_id INT NULL")
            except mysql.connector.Error:
                pass  # column already exists
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Cannot connect to database:\n{e}")

    # ── Header (mirrors hospital.py) ──────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=80)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        ctk.CTkFrame(header, fg_color=ACCENT, height=3, corner_radius=0).pack(side="top", fill="x")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        ctk.CTkLabel(
            left, text="+",
            font=("Segoe UI", 36, "bold"), text_color=ACCENT,
        ).pack(side="left", padx=(0, 12))

        title_block = ctk.CTkFrame(left, fg_color="transparent")
        title_block.pack(side="left", fill="y", anchor="center")

        ctk.CTkLabel(
            title_block, text="NOVACARE",
            font=(_FF, 22, "bold"), text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(12, 0))

        ctk.CTkLabel(
            title_block, text="Patient Management System",
            font=(_FF, 11), text_color=TEXT_MUTED,
        ).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=BORDER_COLOR, height=1, corner_radius=0).pack(fill="x")

    # ── Auth card ─────────────────────────────────────────────────────────────
    def _build_card(self):
        wrapper = ctk.CTkFrame(self, fg_color=BG_ROOT)
        wrapper.pack(fill="both", expand=True, padx=40, pady=28)

        self.card = ctk.CTkFrame(
            wrapper, fg_color=BG_PANEL, corner_radius=14,
            border_width=1, border_color=BORDER_COLOR,
        )
        self.card.pack(fill="both", expand=True)

        # Login / Sign Up toggle
        toggle = ctk.CTkFrame(self.card, fg_color=BG_FRAME, corner_radius=8)
        toggle.pack(fill="x", padx=24, pady=(24, 0))

        self.login_tab = ctk.CTkButton(
            toggle, text="Login",
            font=FONT_BTN, corner_radius=6, height=36,
            command=lambda: self._show_mode("login"),
        )
        self.login_tab.pack(side="left", fill="x", expand=True, padx=4, pady=4)

        self.signup_tab = ctk.CTkButton(
            toggle, text="Sign Up",
            font=FONT_BTN, corner_radius=6, height=36,
            command=lambda: self._show_mode("signup"),
        )
        self.signup_tab.pack(side="left", fill="x", expand=True, padx=4, pady=4)

        # Section accent line + mode title
        mode_row = ctk.CTkFrame(self.card, fg_color="transparent")
        mode_row.pack(anchor="w", padx=24, pady=(20, 0))

        ctk.CTkFrame(mode_row, fg_color=ACCENT, width=4, height=22, corner_radius=2).pack(
            side="left", padx=(0, 10)
        )
        self.mode_label = ctk.CTkLabel(
            mode_row, text="",
            font=(_FF, 13, "bold"), text_color=TEXT_PRIMARY,
        )
        self.mode_label.pack(side="left")

        # Dynamic content area
        self.content = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=24, pady=(10, 24))

    # ── Mode switching ────────────────────────────────────────────────────────
    def _show_mode(self, mode: str):
        for w in self.content.winfo_children():
            w.destroy()

        self.content.columnconfigure(0, weight=1)

        if mode == "login":
            self.geometry("460x520")
            self.mode_label.configure(text="Welcome back")
            self._set_tab_active("login")
            self.login_user = self._field("Username", row=0)
            self.login_pass = self._field("Password", row=1, show="•")
            ctk.CTkButton(
                self.content, text="Login",
                font=FONT_BTN, fg_color=BTN_FG, hover_color=BTN_HOVER,
                text_color=TEXT_BRIGHT, corner_radius=8, height=42,
                command=self._do_login,
            ).grid(row=4, column=0, sticky="ew", pady=(22, 0))
            ctk.CTkLabel(
                self.content, text="Don't have an account? Click Sign Up above.",
                font=FONT_SMALL, text_color=TEXT_MUTED,
            ).grid(row=5, column=0, pady=(10, 0))

        else:
            self.geometry("460x660")
            self.mode_label.configure(text="Create your account")
            self._set_tab_active("signup")
            self.signup_name    = self._field("Full Name",        row=0)
            self.signup_user    = self._field("Username",         row=1)
            self.signup_pass    = self._field("Password",         row=2, show="•")
            self.signup_confirm = self._field("Confirm Password", row=3, show="•")
            ctk.CTkButton(
                self.content, text="Create Account",
                font=FONT_BTN, fg_color=BTN_FG, hover_color=BTN_HOVER,
                text_color=TEXT_BRIGHT, corner_radius=8, height=42,
                command=self._do_signup,
            ).grid(row=8, column=0, sticky="ew", pady=(22, 0))
            ctk.CTkLabel(
                self.content, text="Already have an account? Click Login above.",
                font=FONT_SMALL, text_color=TEXT_MUTED,
            ).grid(row=9, column=0, pady=(10, 0))

    def _field(self, label: str, row: int, show: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(
            self.content, text=label,
            font=FONT_LABEL, text_color=TEXT_MUTED, anchor="w",
        ).grid(row=row * 2, column=0, sticky="w", pady=(10, 2))

        entry = ctk.CTkEntry(
            self.content,
            font=FONT_ENTRY, fg_color=BG_FRAME,
            border_color=BORDER_COLOR, border_width=1,
            text_color=TEXT_PRIMARY, height=38, show=show,
        )
        entry.grid(row=row * 2 + 1, column=0, sticky="ew")
        return entry

    def _set_tab_active(self, active: str):
        on  = dict(fg_color=BTN_FG,    hover_color=BTN_HOVER,   text_color=TEXT_BRIGHT)
        off = dict(fg_color=BG_FRAME,  hover_color=BORDER_COLOR, text_color=TEXT_MUTED)
        self.login_tab.configure(**(on  if active == "login"  else off))
        self.signup_tab.configure(**(on if active == "signup" else off))

    # ── Actions ───────────────────────────────────────────────────────────────
    def _do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        if not username or not password:
            messagebox.showerror("Login", "Please enter both username and password.")
            return

        try:
            conn = _connect()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id FROM users WHERE username=%s AND password_hash=%s",
                (username, _hash(password)),
            )
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Login failed:\n{e}")
            return

        if row:
            self._launch_main(row[0])
        else:
            messagebox.showerror("Login", "Incorrect username or password.")

    def _do_signup(self):
        full_name = self.signup_name.get().strip()
        username  = self.signup_user.get().strip()
        password  = self.signup_pass.get()
        confirm   = self.signup_confirm.get()

        if not username or not password:
            messagebox.showerror("Sign Up", "Username and password are required.")
            return
        if password != confirm:
            messagebox.showerror("Sign Up", "Passwords do not match.")
            return
        if len(password) < 6:
            messagebox.showerror("Sign Up", "Password must be at least 6 characters.")
            return

        try:
            conn = _connect()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name) VALUES (%s, %s, %s)",
                (username, _hash(password), full_name),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Sign Up", "Account created! Please log in.")
            self._show_mode("login")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Sign Up", "That username is already taken.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Sign up failed:\n{e}")

    def _launch_main(self, user_id: int):
        self.destroy()
        from hospital import HospitalApp
        app = HospitalApp(user_id=user_id)
        app.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()
