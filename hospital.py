import csv
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, StringVar, END, INSERT
from datetime import datetime
from db import get_connection
from validate import validate_patient_fields
from records import sort_rows

# ── Appearance ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design tokens – "Refined Dark" palette ───────────────────────────────────
BG_ROOT      = "#07070f"   # near-black with deep blue tint
BG_PANEL     = "#0b0b19"   # card background
BG_FRAME     = "#111122"   # inner panel / input background
BORDER_COLOR = "#1a1a35"   # subtle border
BORDER_GLOW  = "#5b6cf9"   # indigo accent

ACCENT       = "#5b6cf9"   # modern indigo-blue
ACCENT_DARK  = "#4a5be0"   # darker indigo for hover
ACCENT_MINT  = "#5b6cf9"   # alias — consistent accent

TEXT_PRIMARY = "#dce4f0"   # clean near-white
TEXT_MUTED   = "#4c5580"   # muted blue-grey
TEXT_BRIGHT  = "#ffffff"

BTN_FG    = "#5b6cf9"   # all buttons — unified accent
BTN_HOVER = "#4a5be0"

_FF          = "Helvetica Neue"
FONT_TITLE   = (_FF, 28, "bold")
FONT_SECTION = (_FF, 13, "bold")
FONT_LABEL   = (_FF, 13)
FONT_ENTRY   = (_FF, 13)
FONT_BTN     = (_FF, 13, "bold")
FONT_TABLE   = (_FF, 12)
FONT_STATUS  = (_FF, 11)

PLACEHOLDER = "YYYY-MM-DD"

_COLUMNS = (
    "Patient ID", "Name of Doctor", "Department", "Patient Name",
    "Gender", "Patient Address", "Patient Age",
    "Insurance Provider", "Blood Group", "Phone Number",
    "Blood Pressure", "Date of Appointment",
)


# ── Date-field placeholder helpers ───────────────────────────────────────────
def on_entry_click(event, entry_widget):
    inner = entry_widget._entry
    if inner.get() == PLACEHOLDER:
        inner.delete(0, END)
        inner.configure(fg=TEXT_PRIMARY)

def on_focus_out(event, entry_widget):
    inner = entry_widget._entry
    if inner.get() == "":
        inner.insert(0, PLACEHOLDER)
        inner.configure(fg=TEXT_MUTED)


# ── Application ───────────────────────────────────────────────────────────────
class HospitalApp(ctk.CTk):

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.title("NovaCare")
        self.geometry("1490x960+0+0")
        self.configure(fg_color=BG_ROOT)
        self.resizable(True, True)

        self._init_vars()
        self._build_header()
        self._build_main_frame()
        self._build_button_frame()
        self._build_details_frame()
        self._build_status_bar()
        self._style_treeview()
        self.fetch_data()

    # ── String variables ──────────────────────────────────────────────────────
    def _init_vars(self):
        self._all_rows    = []
        self._total_count = 0
        self._sort_col    = None
        self._sort_asc    = True
        self._selected_patient_id = None
        self._search_var = StringVar()
        self.doctorid       = StringVar()
        self.nameofdoctor   = StringVar()
        self.department     = StringVar()
        self.gender         = StringVar()
        self.patage         = StringVar()
        self.insurance      = StringVar()
        self.bloodgrp       = StringVar()
        self.nationality    = StringVar()
        self.bloodpressure  = StringVar()
        self.number         = StringVar()
        self.furtherinfo    = StringVar()
        self.email          = StringVar()
        self.patientid      = StringVar()
        self.medication     = StringVar()
        self.patientname    = StringVar()
        self.dateofbirth    = StringVar()
        self.patientaddress = StringVar()
        self.dateofapp      = StringVar()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=100)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Thin top accent line
        ctk.CTkFrame(header, fg_color=ACCENT, height=3, corner_radius=0).pack(
            side="top", fill="x"
        )

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=0)

        # Left: cross icon + title block
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        ctk.CTkLabel(
            left,
            text="+",
            font=("Segoe UI", 44, "bold"),
            text_color=ACCENT,
        ).pack(side="left", padx=(0, 14))

        title_block = ctk.CTkFrame(left, fg_color="transparent")
        title_block.pack(side="left", fill="y", anchor="center")

        ctk.CTkLabel(
            title_block,
            text="NOVACARE",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(14, 0))

        ctk.CTkLabel(
            title_block,
            text="Patient Records  ·  Appointments  ·  Doctor Directory",
            font=(_FF, 12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # Right: live clock
        self.clock_label = ctk.CTkLabel(
            inner,
            text="",
            font=(_FF, 13),
            text_color=TEXT_MUTED,
        )
        self.clock_label.pack(side="right", padx=8)
        self._tick_clock()

        # Bottom separator
        ctk.CTkFrame(self, fg_color=BORDER_COLOR, height=1, corner_radius=0).pack(fill="x")

    def _tick_clock(self):
        now = datetime.now().strftime("%A, %d %B %Y   %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self._tick_clock)

    # ── Main (top) frame ──────────────────────────────────────────────────────
    def _build_main_frame(self):
        outer = ctk.CTkFrame(self, fg_color=BG_ROOT, corner_radius=0)
        outer.pack(fill="x", padx=14, pady=(12, 0))

        # ── Left panel – input form ────────────────────────────────────────
        left_card = ctk.CTkFrame(
            outer, fg_color=BG_PANEL, corner_radius=12,
            border_width=1, border_color=BORDER_COLOR,
        )
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=4)

        # Section header row
        sec_row = ctk.CTkFrame(left_card, fg_color="transparent")
        sec_row.grid(row=0, column=0, columnspan=5, sticky="ew", padx=16, pady=(14, 6))

        ctk.CTkFrame(sec_row, fg_color=ACCENT, width=4, height=22, corner_radius=2).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkLabel(
            sec_row,
            text="Patient & Doctor Information",
            font=FONT_SECTION,
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        # cols: 0=left labels, 1=left entries, 2=divider (fixed), 3=right labels, 4=right entries
        for c, w in enumerate([0, 1, 0, 0, 1]):
            left_card.columnconfigure(c, weight=w, uniform="col")

        fields_left = [
            (1,  "Doctor ID:",         self.doctorid),
            (2,  "Name of Doctor:",    self.nameofdoctor),
            (3,  "Department:",        self.department),
            (4,  "Patient ID:",        self.patientid),
            (5,  "Patient Name:",      self.patientname),
            (6,  "Date of Birth:",     None),
            (7,  "Gender:",            self.gender),
            (8,  "Patient Age:",       self.patage),
            (9,  "Blood Group:",       self.bloodgrp),
        ]
        fields_right = [
            (1,  "Insurance Provider:",  self.insurance),
            (2,  "Nationality:",         self.nationality),
            (3,  "Phone Number:",        self.number),
            (4,  "Email Address:",       self.email),
            (5,  "Patient Address:",     self.patientaddress),
            (6,  "Further Information:", self.furtherinfo),
            (7,  "Blood Pressure:",      self.bloodpressure),
            (8,  "Medication:",          self.medication),
            (9,  "Date of Appointment:", None),
        ]

        def make_label(parent, text, row, col):
            ctk.CTkLabel(
                parent, text=text,
                font=FONT_LABEL, text_color=TEXT_MUTED, anchor="w",
            ).grid(row=row, column=col, sticky="w", padx=(18, 4), pady=5)

        def make_entry(parent, textvariable, row, col):
            e = ctk.CTkEntry(
                parent, textvariable=textvariable,
                font=FONT_ENTRY, fg_color=BG_FRAME,
                border_color=BORDER_COLOR, border_width=1,
                text_color=TEXT_PRIMARY, height=34,
            )
            e.grid(row=row, column=col, sticky="ew", padx=(0, 18), pady=5)
            return e

        for row, lbl, tvar in fields_left:
            make_label(left_card, lbl, row, 0)
            if tvar is not None:
                make_entry(left_card, tvar, row, 1)

        # Date of Birth – placeholder entry
        self.txtdob = ctk.CTkEntry(
            left_card, textvariable=self.dateofbirth,
            font=FONT_ENTRY, fg_color=BG_FRAME,
            border_color=BORDER_COLOR, border_width=1,
            text_color=TEXT_MUTED, height=34, placeholder_text=PLACEHOLDER,
        )
        self.txtdob.grid(row=6, column=1, sticky="ew", padx=(0, 18), pady=5)
        self.txtdob._entry.insert(0, PLACEHOLDER)
        self.txtdob._entry.configure(fg=TEXT_MUTED)
        self.txtdob.bind("<FocusIn>",  lambda e: on_entry_click(e, self.txtdob))
        self.txtdob.bind("<FocusOut>", lambda e: on_focus_out(e, self.txtdob))

        # Vertical divider between left and right columns
        ctk.CTkFrame(
            left_card, fg_color=BORDER_COLOR, width=1, corner_radius=0
        ).grid(row=1, column=2, rowspan=9, sticky="ns", pady=4, padx=4)

        for row, lbl, tvar in fields_right:
            make_label(left_card, lbl, row, 3)
            if tvar is not None:
                make_entry(left_card, tvar, row, 4)

        # Date of Appointment – placeholder entry
        self.txtdateofapp = ctk.CTkEntry(
            left_card, textvariable=self.dateofapp,
            font=FONT_ENTRY, fg_color=BG_FRAME,
            border_color=BORDER_COLOR, border_width=1,
            text_color=TEXT_MUTED, height=34, placeholder_text=PLACEHOLDER,
        )
        self.txtdateofapp.grid(row=9, column=4, sticky="ew", padx=(0, 18), pady=5)
        self.txtdateofapp._entry.insert(0, PLACEHOLDER)
        self.txtdateofapp._entry.configure(fg=TEXT_MUTED)
        self.txtdateofapp.bind("<FocusIn>",  lambda e: on_entry_click(e, self.txtdateofapp))
        self.txtdateofapp.bind("<FocusOut>", lambda e: on_focus_out(e, self.txtdateofapp))

        # ── Right panel – display area ─────────────────────────────────────
        right_card = ctk.CTkFrame(
            outer, fg_color=BG_PANEL, corner_radius=12,
            border_width=1, border_color=BORDER_COLOR, width=460,
        )
        right_card.pack(side="left", fill="both", padx=(8, 0), pady=4)
        right_card.pack_propagate(False)

        sec_row2 = ctk.CTkFrame(right_card, fg_color="transparent")
        sec_row2.pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkFrame(sec_row2, fg_color=ACCENT_MINT, width=4, height=22, corner_radius=2).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkLabel(
            sec_row2,
            text="Patient Summary",
            font=FONT_SECTION,
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        self.txtdisplay = ctk.CTkTextbox(
            right_card,
            font=("Menlo", 15),
            fg_color=BG_FRAME,
            border_color=BORDER_COLOR,
            border_width=1,
            text_color=TEXT_PRIMARY,
            state="disabled",
            wrap="none",
        )
        self.txtdisplay.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    # ── Button row ────────────────────────────────────────────────────────────
    def _build_button_frame(self):
        btn_outer = ctk.CTkFrame(
            self, fg_color=BG_PANEL, corner_radius=0, height=80,
            border_width=1, border_color=BORDER_COLOR,
        )
        btn_outer.pack(fill="x", padx=14, pady=(10, 0))
        btn_outer.pack_propagate(False)

        specs = [
            ("Display",     self.display),
            ("Data Insert", self.input_data),
            ("Update",      self.update_display),
            ("Delete",      self.delete),
            ("Export CSV",  self.export_csv),
            ("Clear",       self.clear),
            ("Exit",        self.exit),
        ]
        btn_outer.columnconfigure(list(range(len(specs) + 1)), weight=1)

        for col, (label, cmd) in enumerate(specs):
            ctk.CTkButton(
                btn_outer,
                text=label,
                font=FONT_BTN,
                fg_color=BTN_FG,
                hover_color=BTN_HOVER,
                text_color=TEXT_BRIGHT,
                corner_radius=8,
                height=44,
                command=cmd,
            ).grid(row=0, column=col, padx=10, pady=18, sticky="ew")

        ctk.CTkButton(
            btn_outer,
            text="Delete Account",
            font=FONT_BTN,
            fg_color=BTN_FG,
            hover_color=BTN_HOVER,
            text_color="#e05555",
            corner_radius=8,
            height=44,
            command=self.delete_account,
        ).grid(row=0, column=len(specs), padx=10, pady=18, sticky="ew")

    # ── Bottom details / treeview ─────────────────────────────────────────────
    def _build_details_frame(self):
        details_outer = ctk.CTkFrame(
            self, fg_color=BG_PANEL, corner_radius=12,
            border_width=1, border_color=BORDER_COLOR,
        )
        details_outer.pack(fill="both", expand=True, padx=14, pady=(10, 4))

        # Section header + search bar on the same row
        header_row = ctk.CTkFrame(details_outer, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(10, 6))

        sec_left = ctk.CTkFrame(header_row, fg_color="transparent")
        sec_left.pack(side="left", fill="y")

        ctk.CTkFrame(sec_left, fg_color=ACCENT, width=4, height=22, corner_radius=2).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkLabel(
            sec_left,
            text="Appointment Records",
            font=FONT_SECTION,
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        # Search bar (right side of header row)
        search_frame = ctk.CTkFrame(header_row, fg_color="transparent")
        search_frame.pack(side="right", fill="y")

        ctk.CTkLabel(
            search_frame, text="Search:",
            font=FONT_STATUS, text_color=TEXT_MUTED,
        ).pack(side="left", padx=(0, 6))

        search_entry = ctk.CTkEntry(
            search_frame, textvariable=self._search_var,
            font=FONT_ENTRY, fg_color=BG_FRAME,
            border_color=BORDER_COLOR, border_width=1,
            text_color=TEXT_PRIMARY, height=30, width=220,
            placeholder_text="Filter by any field…",
        )
        search_entry.pack(side="left")

        ctk.CTkButton(
            search_frame, text="✕", width=30, height=30,
            font=(_FF, 11), fg_color=BG_FRAME, hover_color=BORDER_COLOR,
            text_color=TEXT_MUTED, border_width=1, border_color=BORDER_COLOR,
            command=lambda: self._search_var.set(""),
        ).pack(side="left", padx=(4, 0))

        self._search_var.trace_add("write", self._apply_filter)

        col_widths = [60, 130, 90, 125, 55, 170, 40, 110, 70, 100, 140, 120]

        tree_frame = ctk.CTkFrame(details_outer, fg_color=BG_FRAME, corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.hospital_table = ttk.Treeview(
            tree_frame,
            columns=_COLUMNS,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )
        vsb.configure(command=self.hospital_table.yview)
        hsb.configure(command=self.hospital_table.xview)

        for i, (col, width) in enumerate(zip(_COLUMNS, col_widths)):
            self.hospital_table.heading(
                col, text=col,
                command=lambda c=i: self._sort_by(c),
            )
            self.hospital_table.column(col, width=width, anchor="center", minwidth=40)

        self.hospital_table.pack(fill="both", expand=True)
        self.hospital_table.bind("<ButtonRelease-1>", self.get_cursor)

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_PANEL, height=30, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        ctk.CTkFrame(bar, fg_color=BORDER_COLOR, height=1, corner_radius=0).pack(
            fill="x", side="top"
        )

        self.status_label = ctk.CTkLabel(
            bar,
            text="  Ready",
            font=FONT_STATUS,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.status_label.pack(side="left", padx=12)

        self.record_count_label = ctk.CTkLabel(
            bar,
            text="Records: 0",
            font=FONT_STATUS,
            text_color=TEXT_MUTED,
        )
        self.record_count_label.pack(side="right", padx=16)

        ctk.CTkLabel(
            bar,
            text="NovaCare  v1.0  ·  Patient Management",
            font=FONT_STATUS,
            text_color=BORDER_COLOR,
        ).pack(side="right", padx=8)

    def _update_status(self, message, count=None):
        self.status_label.configure(text=f"  {message}")
        if count is not None:
            self.record_count_label.configure(text=f"Records: {count}")

    # ── Treeview dark-theme styling ───────────────────────────────────────────
    def _style_treeview(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=BG_FRAME,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_FRAME,
            rowheight=28,
            font=FONT_TABLE,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#0b0b1e",
            foreground=ACCENT,
            font=(_FF, 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", "#1c2270")],
            foreground=[("selected", "#ffffff")],
        )
        style.map("Treeview.Heading", background=[("active", "#141432")])

        self.hospital_table.tag_configure("odd",  background="#0e0e1e")
        self.hospital_table.tag_configure("even", background=BG_FRAME)

        style.configure(
            "Vertical.TScrollbar",
            background=BORDER_COLOR, troughcolor=BG_FRAME,
            bordercolor=BG_FRAME, arrowcolor=TEXT_MUTED,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=BORDER_COLOR, troughcolor=BG_FRAME,
            bordercolor=BG_FRAME, arrowcolor=TEXT_MUTED,
        )

    # ─────────────────────────── Business Logic ──────────────────────────────

    def display(self):
        fields = [
            ("Patient ID",          self.patientid.get()),
            ("Patient Name",        self.patientname.get()),
            ("Date of Birth",       self.dateofbirth.get()),
            ("Gender",              self.gender.get()),
            ("Patient Age",         self.patage.get()),
            ("Patient Address",     self.patientaddress.get()),
            ("Nationality",         self.nationality.get()),
            ("Phone Number",        self.number.get()),
            ("Email Address",       self.email.get()),
            ("Blood Group",         self.bloodgrp.get()),
            ("Blood Pressure",      self.bloodpressure.get()),
            ("Insurance Provider",  self.insurance.get()),
            ("Medication",          self.medication.get()),
            ("Further Information", self.furtherinfo.get()),
            ("Doctor ID",           self.doctorid.get()),
            ("Name of Doctor",      self.nameofdoctor.get()),
            ("Department",          self.department.get()),
            ("Date of Appointment", self.dateofapp.get()),
        ]
        col_width = max(len(lbl) for lbl, _ in fields) + 2
        text = "\n".join(f"{(lbl + ':'):<{col_width}}{val}" for lbl, val in fields)
        self.txtdisplay.configure(state="normal")
        self.txtdisplay.delete("1.0", END)
        self.txtdisplay.insert(INSERT, text)
        self.txtdisplay.configure(state="disabled")
        self._update_status(f"Displaying patient: {self.patientname.get()}")

    def input_data(self):
        patient_id = self.patientid.get()
        dob        = self.dateofbirth.get()
        doa        = self.dateofapp.get()
        num        = self.number.get()

        error = validate_patient_fields(patient_id, dob, doa, num)
        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("NovaCare", "Reminder! Dates must be in the format 'YYYY-MM-DD'")

        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute(
                "SELECT PatientID FROM appointments WHERE PatientID = %s AND user_id = %s",
                (patient_id, self.user_id)
            )
            if my_cursor.fetchone():
                messagebox.showerror(
                    "Error",
                    f"Patient with ID {patient_id} already exists. Use Update to modify."
                )
                conn.close()
                return
            my_cursor.execute(
                "INSERT INTO appointments "
                "(PatientID, NameofDoctor, Department, PatientName, PatientDateOfBirth, "
                "Gender, PatientAddress, PatientAge, InsuranceProvider, BloodGroup, "
                "PhoneNumber, BloodPressure, DateOfAppointment, "
                "DoctorID, Nationality, Email, Medication, FurtherInfo, user_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    self.patientid.get(), self.nameofdoctor.get(),
                    self.department.get(), self.patientname.get(),
                    self.dateofbirth.get(), self.gender.get(),
                    self.patientaddress.get(), self.patage.get(),
                    self.insurance.get(), self.bloodgrp.get(),
                    self.number.get(), self.bloodpressure.get(),
                    self.dateofapp.get(), self.doctorid.get(),
                    self.nationality.get(), self.email.get(),
                    self.medication.get(), self.furtherinfo.get(),
                    self.user_id,
                ),
            )
            conn.commit()
            conn.close()
            self.fetch_data()
            messagebox.showinfo("Success", "Record inserted successfully")
            self._update_status(f"Record inserted for patient: {self.patientname.get()}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to insert record:\n{e}")

    def fetch_data(self, term=""):
        try:
            conn = get_connection()
            cur = conn.cursor()
            if term:
                like = f"%{term}%"
                cur.execute(
                    "SELECT PatientID, NameofDoctor, Department, PatientName, "
                    "Gender, PatientAddress, PatientAge, InsuranceProvider, "
                    "BloodGroup, PhoneNumber, BloodPressure, DateOfAppointment "
                    "FROM appointments WHERE user_id = %s AND ("
                    "PatientID LIKE %s OR NameofDoctor LIKE %s OR Department LIKE %s OR "
                    "PatientName LIKE %s OR Gender LIKE %s OR PatientAddress LIKE %s OR "
                    "CAST(PatientAge AS CHAR) LIKE %s OR InsuranceProvider LIKE %s OR "
                    "BloodGroup LIKE %s OR PhoneNumber LIKE %s OR BloodPressure LIKE %s OR "
                    "CAST(DateOfAppointment AS CHAR) LIKE %s)",
                    (self.user_id, like, like, like, like, like, like,
                     like, like, like, like, like, like)
                )
                self._all_rows = cur.fetchall()
                cur.execute(
                    "SELECT COUNT(*) FROM appointments WHERE user_id = %s",
                    (self.user_id,)
                )
                self._total_count = cur.fetchone()[0]
            else:
                cur.execute(
                    "SELECT PatientID, NameofDoctor, Department, PatientName, "
                    "Gender, PatientAddress, PatientAge, InsuranceProvider, "
                    "BloodGroup, PhoneNumber, BloodPressure, DateOfAppointment "
                    "FROM appointments WHERE user_id = %s",
                    (self.user_id,)
                )
                self._all_rows = cur.fetchall()
                self._total_count = len(self._all_rows)
            conn.close()
            self._render_rows()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch data:\n{e}")

    def get_cursor(self, event=""):
        cursor_row = self.hospital_table.focus()
        content    = self.hospital_table.item(cursor_row)
        treerow    = content["values"]
        if not treerow:
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT PatientID, NameofDoctor, Department, PatientName, "
                "PatientDateOfBirth, Gender, PatientAddress, PatientAge, "
                "InsuranceProvider, BloodGroup, PhoneNumber, BloodPressure, "
                "DateOfAppointment, DoctorID, Nationality, Email, Medication, FurtherInfo "
                "FROM appointments WHERE PatientID = %s AND user_id = %s",
                (treerow[0], self.user_id)
            )
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch record:\n{e}")
            return

        if not row:
            return

        self._selected_patient_id = str(row[0])
        self.patientid.set(row[0] or "")
        self.nameofdoctor.set(row[1] or "")
        self.department.set(row[2] or "")
        self.patientname.set(row[3] or "")
        self.dateofbirth.set(row[4] or "")
        self.gender.set(row[5] or "")
        self.patientaddress.set(row[6] or "")
        self.patage.set(row[7] or "")
        self.insurance.set(row[8] or "")
        self.bloodgrp.set(row[9] or "")
        self.number.set(row[10] or "")
        self.bloodpressure.set(row[11] or "")
        self.dateofapp.set(row[12] or "")
        self.doctorid.set(row[13] or "")
        self.nationality.set(row[14] or "")
        self.email.set(row[15] or "")
        self.medication.set(row[16] or "")
        self.furtherinfo.set(row[17] or "")

        for entry_widget in (self.txtdob, self.txtdateofapp):
            entry_widget._entry.configure(fg=TEXT_PRIMARY)

        self._update_status(f"Selected: {row[3]}  (Patient ID {row[0]})")

    def update_display(self):
        patient_id = self.patientid.get()
        doa        = self.dateofapp.get()
        dob        = self.dateofbirth.get()
        num        = self.number.get()

        if not patient_id:
            messagebox.showerror("Error", "Please select a Patient ID to update")
            return
        error = validate_patient_fields(patient_id, dob, doa, num)
        if error:
            messagebox.showerror("Error", error)
            return

        if not self._selected_patient_id:
            messagebox.showerror("Error", "Please select a record from the table to update")
            return

        new_id = self.patientid.get()
        if new_id != self._selected_patient_id:
            try:
                conn = get_connection()
                cur  = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM appointments WHERE PatientID=%s AND user_id=%s",
                    (new_id, self.user_id),
                )
                exists = cur.fetchone()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to validate Patient ID:\n{e}")
                return
            if exists:
                messagebox.showerror("Error", f"Patient ID {new_id} already exists.")
                return

        choice = messagebox.askyesno("NovaCare", "Confirm you want to update this record?")
        if choice:
            try:
                conn = get_connection()
                my_cursor = conn.cursor()
                my_cursor.execute(
                    "UPDATE appointments SET PatientID=%s, NameofDoctor=%s, Department=%s, "
                    "PatientName=%s, PatientDateOfBirth=%s, PatientAddress=%s, PatientAge=%s, "
                    "Gender=%s, InsuranceProvider=%s, BloodGroup=%s, PhoneNumber=%s, "
                    "BloodPressure=%s, DateOfAppointment=%s, "
                    "DoctorID=%s, Nationality=%s, Email=%s, Medication=%s, FurtherInfo=%s "
                    "WHERE PatientID=%s AND user_id=%s",
                    (
                        new_id, self.nameofdoctor.get(),
                        self.department.get(), self.patientname.get(),
                        self.dateofbirth.get(), self.patientaddress.get(),
                        self.patage.get(), self.gender.get(),
                        self.insurance.get(), self.bloodgrp.get(),
                        self.number.get(), self.bloodpressure.get(),
                        self.dateofapp.get(), self.doctorid.get(),
                        self.nationality.get(), self.email.get(),
                        self.medication.get(), self.furtherinfo.get(),
                        self._selected_patient_id, self.user_id,
                    ),
                )
                conn.commit()
                conn.close()
                self._selected_patient_id = new_id
                self._update_status(f"Record updated for patient: {self.patientname.get()}")
                self.fetch_data()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update record:\n{e}")

    def delete(self):
        choice = messagebox.askyesno(
            "NovaCare",
            "Confirm you want to delete this record?"
        )
        if choice:
            if self.patientid.get() == "":
                messagebox.showerror("Error", "Please select a Patient ID to delete")
            else:
                try:
                    conn = get_connection()
                    my_cursor = conn.cursor()
                    my_cursor.execute(
                        "DELETE FROM appointments WHERE PatientID=%s AND user_id=%s",
                        (self.patientid.get(), self.user_id)
                    )
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Delete", "Patient deleted successfully")
                    self.fetch_data()
                    self._update_status("Record deleted")
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to delete record:\n{e}")
        self.clear()

    # ── Filter / sort / render ────────────────────────────────────────────────

    def _render_rows(self):
        rows = self._all_rows
        if self._sort_col is not None:
            rows = sort_rows(rows, self._sort_col, ascending=self._sort_asc)

        self.hospital_table.delete(*self.hospital_table.get_children())
        for idx, row in enumerate(rows):
            tag = "odd" if idx % 2 else "even"
            self.hospital_table.insert("", END, values=row, tags=(tag,))

        shown = len(rows)
        if self._search_var.get():
            self._update_status(f"Showing {shown} of {self._total_count} records", count=shown)
        else:
            self._update_status("Data loaded", count=shown)

    def _apply_filter(self, *_):
        self.fetch_data(self._search_var.get())

    def _sort_by(self, col_idx):
        if self._sort_col == col_idx:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col_idx
            self._sort_asc = True

        for i, col in enumerate(_COLUMNS):
            if i == self._sort_col:
                arrow = " ▲" if self._sort_asc else " ▼"
                self.hospital_table.heading(col, text=col + arrow)
            else:
                self.hospital_table.heading(col, text=col)

        self._render_rows()

    def export_csv(self):
        rows = [
            self.hospital_table.item(child)["values"]
            for child in self.hospital_table.get_children()
        ]
        if not rows:
            messagebox.showinfo("Export CSV", "No records to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Records as CSV",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_COLUMNS)
            writer.writerows(rows)

        messagebox.showinfo("Export CSV", f"Exported {len(rows)} records to:\n{path}")
        self._update_status(f"Exported {len(rows)} records to CSV")

    def delete_account(self):
        if not messagebox.askyesno(
            "Delete Account",
            "This will permanently delete your account and ALL your patient records.\n\nThis cannot be undone. Continue?",
        ):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM appointments WHERE user_id=%s", (self.user_id,))
            cur.execute("DELETE FROM users WHERE id=%s", (self.user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete account:\n{e}")
            return
        messagebox.showinfo("Account Deleted", "Your account has been deleted.")
        self.destroy()
        from auth import AuthApp
        AuthApp().mainloop()

    def clear(self):
        self._selected_patient_id = None
        for var in (
            self.doctorid, self.nameofdoctor, self.department, self.gender,
            self.patage, self.insurance, self.bloodgrp, self.nationality,
            self.number, self.furtherinfo, self.email, self.bloodpressure,
            self.medication, self.patientid, self.patientname,
            self.dateofbirth, self.patientaddress, self.dateofapp,
        ):
            var.set("")

        for entry_widget in (self.txtdob, self.txtdateofapp):
            inner = entry_widget._entry
            inner.delete(0, END)
            inner.insert(0, PLACEHOLDER)
            inner.configure(fg=TEXT_MUTED)

        self.txtdisplay.configure(state="normal")
        self.txtdisplay.delete("1.0", END)
        self.txtdisplay.configure(state="disabled")

        for item in self.hospital_table.selection():
            self.hospital_table.selection_remove(item)

        self._update_status("Fields cleared")

    def exit(self):
        if messagebox.askyesno("NovaCare", "Confirm you want to exit?"):
            self.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    print("Error: hospital.py cannot be run directly. Please run auth.py to launch NovaCare.")
    sys.exit(1)
