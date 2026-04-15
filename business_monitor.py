import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime
import pytesseract
from PIL import Image
import re
import openpyxl
import os
import platform
import subprocess
import json
import bcrypt

# ─────────────────────────────────────────────
#  Tesseract Path (Windows default)
# ─────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ─────────────────────────────────────────────
#  Theme
# ─────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ═════════════════════════════════════════════
#  LAYER 1 ─ Domain / Model
# ═════════════════════════════════════════════

class Transaction:
    """
    Abstract base for all financial transactions.
    Encapsulates amount + date; subclasses add type-specific behaviour.
    """

    DISPLAY_ICON = "💱"

    def __init__(self, amount: float, date: datetime | None = None):
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")
        self._amount = amount
        self._date: datetime = date if date else datetime.now()

    # ── Properties (encapsulation) ──────────────
    @property
    def amount(self) -> float:
        return self._amount

    @property
    def date(self) -> datetime:
        return self._date

    # ── Polymorphic helpers ──────────────────────
    def display_amount(self, currency: str = "$") -> str:
        """Overridable formatted amount string."""
        return f"{currency}{self._amount:,.2f}"

    def summary_row(self, currency: str = "$") -> list:
        """Returns a list suitable for CSV/Excel rows – overridden by subclasses."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__} amount={self._amount} date={self._date.date()}>"


class Income(Transaction):
    """Represents a single income entry."""

    DISPLAY_ICON = "💰"

    def __init__(self, amount: float, date: datetime | None = None):
        super().__init__(amount, date)

    def summary_row(self, currency: str = "$") -> list:
        return [
            "Income",
            self.display_amount(currency),
            "-",
            "-",
            self._date.strftime("%Y-%m-%d %H:%M:%S"),
        ]

    def to_dict(self) -> dict:
        return {
            "type": "income",
            "amount": self._amount,
            "date": self._date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def from_dict(data: dict) -> "Income":
        return Income(
            amount=data["amount"],
            date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
        )


class Expense(Transaction):
    """Represents a single expense entry with category and optional bill number."""

    DISPLAY_ICON = "💸"

    CATEGORIES = [
        "Rent", "Salaries", "Supplies", "Marketing",
        "Utilities", "Transport", "Maintenance", "Other",
    ]

    def __init__(
        self,
        amount: float,
        category: str,
        bill_number: str | None = None,
        date: datetime | None = None,
    ):
        super().__init__(amount, date)
        if category not in self.CATEGORIES:
            category = "Other"
        self._category = category
        self._bill_number = bill_number

    # ── Extra properties ─────────────────────────
    @property
    def category(self) -> str:
        return self._category

    @property
    def bill_number(self) -> str | None:
        return self._bill_number

    # ── Polymorphic overrides ────────────────────
    def display_amount(self, currency: str = "$") -> str:
        return f"-{currency}{self._amount:,.2f}"

    def summary_row(self, currency: str = "$") -> list:
        return [
            "Expense",
            f"{currency}{self._amount:,.2f}",
            self._category,
            self._bill_number or "",
            self._date.strftime("%Y-%m-%d %H:%M:%S"),
        ]

    def to_dict(self) -> dict:
        return {
            "type": "expense",
            "amount": self._amount,
            "category": self._category,
            "bill_number": self._bill_number,
            "date": self._date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def from_dict(data: dict) -> "Expense":
        return Expense(
            amount=data["amount"],
            category=data["category"],
            bill_number=data.get("bill_number"),
            date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
        )


# ─────────────────────────────────────────────

class Business:
    """
    Core domain object.
    Encapsulates all financial data for a single business entity.
    """

    PERIODS = ["Daily", "Weekly", "Monthly"]
    CURRENCIES = {"$ US Dollar": "$", "₺ Turkish Lira": "₺"}

    def __init__(
        self,
        name: str,
        budget: float,
        period: str = "Monthly",
        currency: str = "$",
    ):
        self._name = name
        self._budget = budget
        self._period = period if period in self.PERIODS else "Monthly"
        self._currency = currency
        self._transactions: list[Transaction] = []
        self._notes: str = ""

    # ── Properties ───────────────────────────────
    @property
    def name(self) -> str:
        return self._name

    @property
    def budget(self) -> float:
        return self._budget

    @property
    def period(self) -> str:
        return self._period

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str):
        self._notes = value

    @property
    def incomes(self) -> list[Income]:
        return [t for t in self._transactions if isinstance(t, Income)]

    @property
    def expenses(self) -> list[Expense]:
        return [t for t in self._transactions if isinstance(t, Expense)]

    # ── Mutation methods ─────────────────────────
    def add_income(self, amount: float, date: datetime | None = None) -> Income:
        income = Income(amount, date)
        self._transactions.append(income)
        return income

    def add_expense(
        self,
        amount: float,
        category: str,
        bill_number: str | None = None,
        date: datetime | None = None,
    ) -> Expense:
        expense = Expense(amount, category, bill_number, date)
        self._transactions.append(expense)
        return expense

    # ── Computed financials ──────────────────────
    def total_income(self) -> float:
        return sum(i.amount for i in self.incomes)

    def total_expense(self) -> float:
        return sum(e.amount for e in self.expenses)

    def net_profit(self) -> float:
        return self.total_income() - self.total_expense()

    def expense_by_category(self) -> list[float]:
        return [
            sum(e.amount for e in self.expenses if e.category == cat)
            for cat in Expense.CATEGORIES
        ]

    def alerts(self) -> list[str]:
        alerts = []
        if self.total_expense() > self._budget:
            alerts.append("⚠ Budget exceeded!")
        if self.net_profit() < 0:
            alerts.append("⚠ Business running at a loss!")
        return alerts

    # ── Serialisation ────────────────────────────
    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "budget": self._budget,
            "period": self._period,
            "currency": self._currency,
            "notes": self._notes,
            "transactions": [t.to_dict() for t in self._transactions],
        }

    @staticmethod
    def from_dict(data: dict) -> "Business":
        b = Business(
            name=data["name"],
            budget=data["budget"],
            period=data.get("period", "Monthly"),
            currency=data.get("currency", "$"),
        )
        b._notes = data.get("notes", "")
        for td in data.get("transactions", []):
            if td["type"] == "income":
                b._transactions.append(Income.from_dict(td))
            elif td["type"] == "expense":
                b._transactions.append(Expense.from_dict(td))
        # Legacy support for old separate income/expense lists
        for i in data.get("incomes", []):
            b._transactions.append(Income.from_dict({**i, "type": "income"}))
        for e in data.get("expenses", []):
            b._transactions.append(Expense.from_dict({**e, "type": "expense"}))
        return b

    def __repr__(self):
        return f"<Business '{self._name}' budget={self._budget} currency={self._currency}>"


# ═════════════════════════════════════════════
#  LAYER 2 ─ User / Auth
# ═════════════════════════════════════════════

class User:
    """
    Base user class — encapsulates credentials and basic identity.
    """

    USERS_FILE = "users.json"

    def __init__(self, username: str):
        self._username = username

    @property
    def username(self) -> str:
        return self._username

    # ── Class-level helpers ──────────────────────
    @classmethod
    def _load_all(cls) -> dict:
        try:
            with open(cls.USERS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def _save_all(cls, users: dict):
        with open(cls.USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

    @classmethod
    def register(cls, username: str, password: str) -> "User | None":
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty!")
            return None
        users = cls._load_all()
        if username in users:
            messagebox.showerror("Error", "User already exists!")
            return None
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        users[username] = hashed.decode()
        cls._save_all(users)
        messagebox.showinfo("Success", f"User '{username}' registered successfully!")
        return cls(username)

    @classmethod
    def authenticate(cls, username: str, password: str) -> "User | None":
        users = cls._load_all()
        hashed = users.get(username)
        if hashed and bcrypt.checkpw(password.encode(), hashed.encode()):
            return cls(username)
        return None

    def __repr__(self):
        return f"<User '{self._username}'>"


class AdminUser(User):
    """
    Inherits from User; adds admin-specific capabilities (extensible).
    Demonstrates inheritance.
    """

    def __init__(self, username: str):
        super().__init__(username)
        self._is_admin = True

    @property
    def is_admin(self) -> bool:
        return self._is_admin

    def list_all_users(self) -> list[str]:
        return list(self._load_all().keys())


# ═════════════════════════════════════════════
#  LAYER 3 ─ Exporters  (Polymorphism)
# ═════════════════════════════════════════════

class BaseExporter:
    """
    Abstract exporter — defines the interface.
    Subclasses override export() and _write().
    """

    def __init__(self, business: Business):
        self._business = business

    def _header_rows(self) -> list[list]:
        b = self._business
        return [
            ["Business Name", b.name],
            ["Period", b.period],
            ["Budget", f"{b.currency}{b.budget:,.2f}"],
            ["Total Income", f"{b.currency}{b.total_income():,.2f}"],
            ["Total Expense", f"{b.currency}{b.total_expense():,.2f}"],
            ["Net Profit", f"{b.currency}{b.net_profit():,.2f}"],
            [],
            ["Type", "Amount", "Category", "Bill Number", "Date"],
        ]

    def _transaction_rows(self) -> list[list]:
        rows = []
        for idx, inc in enumerate(self._business.incomes, 1):
            row = inc.summary_row(self._business.currency)
            row[3] = f"INC-{idx:03}"
            rows.append(row)
        for exp in self._business.expenses:
            rows.append(exp.summary_row(self._business.currency))
        return rows

    def export(self, file_path: str):
        """Template method — calls _write() which subclasses implement."""
        all_rows = self._header_rows() + self._transaction_rows()
        self._write(file_path, all_rows)
        return file_path

    def _write(self, file_path: str, rows: list[list]):
        raise NotImplementedError


class CSVExporter(BaseExporter):
    """Exports to CSV — overrides _write()."""

    def _write(self, file_path: str, rows: list[list]):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)


class ExcelExporter(BaseExporter):
    """Exports to .xlsx — overrides _write(); also auto-opens the file."""

    def _write(self, file_path: str, rows: list[list]):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Financial Report"
        for row in rows:
            ws.append(row)
        wb.save(file_path)

    def export_and_open(self) -> str:
        b = self._business
        folder = os.path.join("Reports", b.name, b.period)
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(
            folder,
            f"{b.name}Report{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        )
        self.export(filename)
        try:
            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin":
                subprocess.call(("open", filename))
            else:
                subprocess.call(("xdg-open", filename))
        except Exception:
            pass
        return filename


# ═════════════════════════════════════════════
#  LAYER 4 ─ Data Repository
# ═════════════════════════════════════════════

class BusinessRepository:
    """
    Handles persistence of all Business objects.
    Encapsulates file I/O so the rest of the app is decoupled from storage.
    """

    DATA_FILE = "business_data.json"
    SUMMARY_FILE = "business_summary.csv"

    def __init__(self):
        self._businesses: list[Business] = []

    @property
    def businesses(self) -> list[Business]:
        return self._businesses

    def load(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._businesses = [Business.from_dict(b) for b in data]

    def save(self):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self._businesses], f, ensure_ascii=False, indent=4)

    def save_summary(self):
        with open(self.SUMMARY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Business", "Budget", "Income", "Expense", "Profit"])
            for b in self._businesses:
                writer.writerow([b.name, b.budget, b.total_income(), b.total_expense(), b.net_profit()])

    def add(self, business: Business):
        self._businesses.append(business)
        self.save()

    def find_by_name(self, name: str) -> Business | None:
        return next((b for b in self._businesses if b.name == name), None)


# ═════════════════════════════════════════════
#  LAYER 5 ─ UI Helpers
# ═════════════════════════════════════════════

class ToolTip:
    """Lightweight hover tooltip."""

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tip_window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self._tip_window:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + 20
        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(
            tw, text=self._text, justify="left",
            background="#111", foreground="#027070",
            relief="solid", borderwidth=1,
            font=("Segoe UI", 10, "normal"),
        ).pack(ipadx=5, ipady=2)

    def _hide(self, _event=None):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# ═════════════════════════════════════════════
#  LAYER 6 ─ Application Controller
# ═════════════════════════════════════════════

class AppController:
    """
    Central controller — wires together the UI, repository, and domain.
    Keeps business logic out of UI callbacks.
    """

    def __init__(self, app: ctk.CTk):
        self._app = app
        self._repo = BusinessRepository()
        self._repo.load()
        self._current_user: User | None = None
        self._current_business: Business | None = None

    # ── Accessors ────────────────────────────────
    @property
    def current_business(self) -> Business | None:
        return self._current_business

    @property
    def current_user(self) -> User | None:
        return self._current_user

    @property
    def businesses(self) -> list[Business]:
        return self._repo.businesses

    # ── Auth ─────────────────────────────────────
    def login(self, username: str, password: str) -> User | None:
        user = User.authenticate(username, password)
        if user:
            self._current_user = user
        return user

    def register(self, username: str, password: str) -> User | None:
        return User.register(username, password)

    # ── Business management ──────────────────────
    def select_business(self, name: str):
        self._current_business = self._repo.find_by_name(name)

    def create_business(self, name: str, budget: float, period: str, currency: str) -> Business:
        b = Business(name, budget, period, currency)
        self._repo.add(b)
        self._current_business = b
        return b

    # ── Transactions ─────────────────────────────
    def record_income(self, amount: float):
        if not self._current_business:
            return
        self._current_business.add_income(amount)
        self._repo.save()

    def record_expense(self, amount: float, category: str, bill_number: str | None = None):
        if not self._current_business:
            return
        self._current_business.add_expense(amount, category, bill_number)
        self._repo.save()

    def process_ocr_bill(self, file_path: str) -> float | None:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        numbers = re.findall(r"\d+\.\d{2}", text)
        return float(numbers[-1]) if numbers else None

    # ── Exports ──────────────────────────────────
    def export_csv(self, file_path: str):
        if not self._current_business:
            return
        CSVExporter(self._current_business).export(file_path)

    def export_excel(self) -> str | None:
        if not self._current_business:
            return None
        return ExcelExporter(self._current_business).export_and_open()

    def save_notes(self, notes: str):
        if self._current_business:
            self._current_business.notes = notes
            self._repo.save()

    def refresh_summary(self):
        self._repo.save_summary()


# ═════════════════════════════════════════════
#  LAYER 7 ─ UI Frames
# ═════════════════════════════════════════════

class LoginFrame(ctk.CTkFrame):
    """Login / Register screen."""

    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self._on_success = on_login_success
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="Business Financial Monitoring",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#00f5ff",
        ).pack(pady=40)

        self._username = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self._username.pack(pady=10)
        self._password = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self._password.pack(pady=10)

        ctk.CTkButton(
            self, text="Login", command=self._login,
            width=200, fg_color="#334647", hover_color="#00ff9c",
        ).pack(pady=10)
        ctk.CTkButton(
            self, text="Register", command=self._register,
            width=200, fg_color="#65500A", hover_color="#00ff9c",
        ).pack()

    def _login(self):
        self._on_success("login", self._username.get(), self._password.get())

    def _register(self):
        self._on_success("register", self._username.get(), self._password.get())


class DashboardFrame(ctk.CTkFrame):
    """Main dashboard — charts, summaries, actions."""

    BTN_STYLE = dict(width=160, height=50, fg_color="#11583f",
                     hover_color="#9ea5a3", corner_radius=20,
                     font=ctk.CTkFont(size=12, weight="bold"))

    def __init__(self, parent, controller: AppController):
        super().__init__(parent)
        self._ctrl = controller
        self._build()

    # ── Build layout ─────────────────────────────
    def _build(self):
        self._build_header()
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)
        self._build_sidebar(main)
        self._build_content(main)

    def _build_header(self):
        hf = ctk.CTkFrame(self, height=80)
        hf.pack(fill="x")
        self._header_lbl = ctk.CTkLabel(hf, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self._header_lbl.pack(side="left", padx=20)
        self._budget_lbl = ctk.CTkLabel(hf, text="", font=ctk.CTkFont(size=16))
        self._budget_lbl.pack(side="right", padx=20)

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=250)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self._biz_list = tk.Listbox(sidebar)
        self._biz_list.pack(fill="both", expand=True)
        self._biz_list.bind("<<ListboxSelect>>", self._on_select_business)

        ctk.CTkButton(
            sidebar, text="➕ Add Business", command=self._add_business,
            width=220, height=50, fg_color="#00f5ff", hover_color="#00ff9c",
            corner_radius=20, font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=10)

        for b in self._ctrl.businesses:
            self._biz_list.insert(tk.END, b.name)

    def _build_content(self, parent):
        content = ctk.CTkFrame(parent)
        content.pack(side="right", fill="both", expand=True)

        # Summary labels
        summary = ctk.CTkFrame(content)
        summary.pack(fill="x", pady=20)
        self._income_lbl = ctk.CTkLabel(summary, text="Total Income\n—", font=ctk.CTkFont(size=14))
        self._income_lbl.pack(side="left", expand=True)
        self._expense_lbl = ctk.CTkLabel(summary, text="Total Expense\n—", font=ctk.CTkFont(size=14))
        self._expense_lbl.pack(side="left", expand=True)
        self._profit_lbl = ctk.CTkLabel(summary, text="Net Profit\n—", font=ctk.CTkFont(size=14))
        self._profit_lbl.pack(side="left", expand=True)

        # Action buttons
        bf = ctk.CTkFrame(content)
        bf.pack(fill="x", pady=10)
        buttons = [
            ("💰 Add Income",    self._add_income),
            ("💸 Add Expense",   self._add_expense),
            ("📄 Upload Bill",   self._upload_bill),
            ("📁 Export CSV",    self._export_csv),
            ("📊 Export Excel",  self._export_excel),
            ("🗂 Open Archive",  self._open_archive),
        ]
        for label, cmd in buttons:
            btn = ctk.CTkButton(bf, text=label, command=cmd, **self.BTN_STYLE)
            btn.pack(side="left", padx=10)
            if label == "🗂 Open Archive":
                ToolTip(btn, "View past reports and add notes")

        self._alerts_lbl = ctk.CTkLabel(content, text="", fg_color="transparent",
                                        text_color="red", font=ctk.CTkFont(size=14))
        self._alerts_lbl.pack(pady=10)

        # Charts
        self._fig_pie, self._ax_pie = plt.subplots(figsize=(5, 4))
        self._canvas_pie = FigureCanvasTkAgg(self._fig_pie, master=content)
        self._canvas_pie.get_tk_widget().pack(side="left", fill="both", expand=True)

        self._fig_line, self._ax_line = plt.subplots(figsize=(5, 4))
        self._canvas_line = FigureCanvasTkAgg(self._fig_line, master=content)
        self._canvas_line.get_tk_widget().pack(side="right", fill="both", expand=True)

    # ── Refresh ──────────────────────────────────
    def refresh(self):
        b = self._ctrl.current_business
        u = self._ctrl.current_user
        if not b or not u:
            return

        self._header_lbl.configure(text=f"Welcome {u.username} | {b.name} | {b.period}")
        self._budget_lbl.configure(text=f"Budget: {b.currency}{b.budget:,.2f}")
        self._income_lbl.configure(text=f"Total Income\n{b.currency}{b.total_income():,.2f}")
        self._expense_lbl.configure(text=f"Total Expense\n{b.currency}{b.total_expense():,.2f}")
        self._profit_lbl.configure(text=f"Net Profit\n{b.currency}{b.net_profit():,.2f}")
        self._alerts_lbl.configure(text="\n".join(b.alerts()))

        # Pie chart
        self._ax_pie.clear()
        data = b.expense_by_category()
        non_zero = [(v, l) for v, l in zip(data, Expense.CATEGORIES) if v > 0]
        if non_zero:
            vals, labels = zip(*non_zero)
            self._ax_pie.pie(vals, labels=labels, autopct="%1.1f%%")
        self._ax_pie.set_title("Expenses by Category")
        self._canvas_pie.draw()

        # Line chart
        self._ax_line.clear()
        self._ax_line.plot(
            ["Income", "Expense", "Profit"],
            [b.total_income(), b.total_expense(), b.net_profit()],
            marker="o",
        )
        self._ax_line.set_title("Financial Overview")
        self._canvas_line.draw()

        self._ctrl.refresh_summary()

    # ── UI action handlers ───────────────────────
    def _on_select_business(self, _event=None):
        if not self._biz_list.curselection():
            return
        name = self._biz_list.get(self._biz_list.curselection())
        self._ctrl.select_business(name)
        self.refresh()

    def _add_business(self):
        name = simpledialog.askstring("Business Name", "Enter business name:")
        if not name:
            return

        win = tk.Toplevel()
        win.title("Business Settings")
        win.geometry("300x240")

        tk.Label(win, text="Choose currency:").pack(pady=8)
        cur_combo = ctk.CTkComboBox(win, values=list(Business.CURRENCIES.keys()))
        cur_combo.set("$ US Dollar")
        cur_combo.pack(pady=4)

        tk.Label(win, text="Select Period:").pack(pady=8)
        per_combo = ctk.CTkComboBox(win, values=Business.PERIODS)
        per_combo.set("Monthly")
        per_combo.pack(pady=4)

        def confirm():
            currency = Business.CURRENCIES.get(cur_combo.get(), "$")
            period = per_combo.get()
            win.destroy()
            budget = simpledialog.askfloat("Budget", "Enter budget amount:")
            if not budget:
                return
            b = self._ctrl.create_business(name, budget, period, currency)
            self._biz_list.insert(tk.END, b.name)
            self.refresh()

        ctk.CTkButton(win, text="OK", command=confirm).pack(pady=12)

    def _add_income(self):
        if not self._ctrl.current_business:
            return
        amount = simpledialog.askfloat("Income", "Enter income amount:")
        if amount:
            self._ctrl.record_income(amount)
            self.refresh()

    def _add_expense(self):
        if not self._ctrl.current_business:
            return
        amount = simpledialog.askfloat("Expense", "Enter expense amount:")
        if not amount:
            return
        self._category_picker(amount)

    def _category_picker(self, amount: float, bill_number: str | None = None):
        win = tk.Toplevel()
        win.title("Select Category")
        win.geometry("300x150")
        tk.Label(win, text="Select Category:").pack(pady=10)
        combo = ctk.CTkComboBox(win, values=Expense.CATEGORIES)
        combo.set(Expense.CATEGORIES[0])
        combo.pack(pady=10)

        def confirm():
            cat = combo.get()
            bn = bill_number or simpledialog.askstring("Bill Number", "Enter bill number (optional):")
            win.destroy()
            self._ctrl.record_expense(amount, cat, bn)
            self.refresh()

        ctk.CTkButton(win, text="OK", command=confirm).pack(pady=10)

    def _upload_bill(self):
        if not self._ctrl.current_business:
            messagebox.showerror("Error", "No business selected!")
            return
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not path:
            return
        amount = self._ctrl.process_ocr_bill(path)
        if amount is None:
            messagebox.showerror("Error", "Could not detect amount from bill!")
            return
        bill_number = "OCR-" + datetime.now().strftime("%H%M%S")
        self._category_picker(amount, bill_number)
        messagebox.showinfo("Success", f"Detected: {self._ctrl.current_business.currency}{amount:.2f}")

    def _export_csv(self):
        b = self._ctrl.current_business
        if not b:
            messagebox.showerror("Error", "No business selected!")
            return
        default = f"{b.name}{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            initialfile=default, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        self._ctrl.export_csv(path)
        messagebox.showinfo("Success", f"CSV exported:\n{path}")

    def _export_excel(self):
        if not self._ctrl.current_business:
            messagebox.showerror("Error", "No business selected!")
            return
        path = self._ctrl.export_excel()
        if path:
            messagebox.showinfo("Success", f"Excel exported and opened:\n{path}")

    def _open_archive(self):
        b = self._ctrl.current_business
        if not b:
            return
        folder = os.path.join("Reports", b.name, b.period)
        os.makedirs(folder, exist_ok=True)

        win = tk.Toplevel()
        win.title(f"{b.name} — Archive")
        listbox = tk.Listbox(win, width=80)
        listbox.pack(fill="both", expand=True)
        for f in sorted(os.listdir(folder)):
            listbox.insert(tk.END, f)

        ctk.CTkLabel(win, text="Notes:").pack(pady=5)
        notes_entry = ctk.CTkEntry(win, width=400)
        notes_entry.pack(pady=5)
        notes_entry.insert(0, b.notes)

        def save_notes():
            self._ctrl.save_notes(notes_entry.get())
            messagebox.showinfo("Saved", "Notes saved!")

        ctk.CTkButton(win, text="Save Notes", command=save_notes).pack(pady=5)

        def open_selected(_event=None):
            if listbox.curselection():
                os.startfile(os.path.join(folder, listbox.get(listbox.curselection())))

        listbox.bind("<Double-Button-1>", open_selected)


# ═════════════════════════════════════════════
#  LAYER 8 ─ Application Entry Point
# ═════════════════════════════════════════════

class App:
    """
    Root application — wires frames and controller together.
    """

    def __init__(self):
        self._root = ctk.CTk()
        self._root.title("Business Financial Monitoring System")
        self._root.geometry("1500x900")

        self._ctrl = AppController(self._root)

        self._login_frame = LoginFrame(self._root, self._handle_auth)
        self._login_frame.pack(fill="both", expand=True)

        self._dashboard_frame = DashboardFrame(self._root, self._ctrl)

    def _handle_auth(self, action: str, username: str, password: str):
        if action == "register":
            self._ctrl.register(username, password)
        elif action == "login":
            user = self._ctrl.login(username, password)
            if user:
                messagebox.showinfo("Success", f"Welcome, {user.username}!")
                self._login_frame.pack_forget()
                self._dashboard_frame.pack(fill="both", expand=True)
                self._dashboard_frame.refresh()
            else:
                messagebox.showerror("Error", "Invalid username or password.")

    def run(self):
        self._root.mainloop()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    App().run()
