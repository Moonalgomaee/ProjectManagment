import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime
import pytesseract
from PIL import ImageTk, Image
import re
import openpyxl
import os
import platform
import subprocess
import json
import bcrypt

# ------------------ Tesseract Path ------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ------------------ Appearance ------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ------------------ Users File ------------------
users_file = "users.json"

# ------------------ Tooltip Helper ------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#111", foreground="#027070",
                         relief='solid', borderwidth=1,
                         font=("Segoe UI", 10, "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ------------------ Business Class ------------------
class Business:
    def __init__(self, name, budget, period="Monthly", currency="$"):
        self.name = name
        self.budget = budget
        self.period = period
        self.currency = currency
        self.incomes = []
        self.expenses = []
        self.categories = ["Rent", "Salaries", "Supplies", "Marketing",
                           "Utilities", "Transport", "Maintenance", "Other"]

    def add_income(self, amount, date=None):
        self.incomes.append({"amount": amount, "date": date if date else datetime.now()})

    def add_expense(self, amount, category, bill_number=None, date=None):
        self.expenses.append({"amount": amount, "category": category,
                              "bill_number": bill_number, "date": date if date else datetime.now()})

    def total_income(self):
        return sum(i["amount"] for i in self.incomes)

    def total_expense(self):
        return sum(e["amount"] for e in self.expenses)

    def net_profit(self):
        return self.total_income() - self.total_expense()

    def alerts(self):
        alerts = []
        if self.total_expense() > self.budget:
            alerts.append("⚠ Budget exceeded!")
        if self.net_profit() < 0:
            alerts.append("⚠ Business running at loss!")
        return alerts

    def expense_by_category(self):
        return [sum(e["amount"] for e in self.expenses if e["category"] == cat) for cat in self.categories]

    def to_dict(self):
        return {
            "name": self.name,
            "budget": self.budget,
            "period": self.period,
            "currency": self.currency,
            "incomes": [{"amount": i["amount"], "date": i["date"].strftime("%Y-%m-%d %H:%M:%S")} for i in self.incomes],
            "expenses": [{"amount": e["amount"], "category": e["category"], "bill_number": e.get("bill_number"),
                          "date": e["date"].strftime("%Y-%m-%d %H:%M:%S")} for e in self.expenses]
        }

    @staticmethod
    def from_dict(data):
        b = Business(data["name"], data["budget"], data.get("period", "Monthly"), data.get("currency", "$"))
        for i in data.get("incomes", []):
            b.add_income(i["amount"], datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S"))
        for e in data.get("expenses", []):
            b.add_expense(e["amount"], e["category"], e.get("bill_number"),
                          datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S"))
        return b

# ------------------ Global Data ------------------
businesses = []
current_business = None
current_user = None
DATA_FILE = "business_data.json"

# ------------------ Load / Save Data ------------------
def load_data():
    global businesses
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            businesses = [Business.from_dict(b) for b in data]

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([b.to_dict() for b in businesses], f, ensure_ascii=False, indent=4)

def save_summary():
    with open("business_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Business", "Budget", "Income", "Expense", "Profit"])
        for b in businesses:
            writer.writerow([b.name, b.budget, b.total_income(), b.total_expense(), b.net_profit()])

# ------------------ Users Functions ------------------
def load_users():
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    if not username or not password:
        messagebox.showerror("Error", "Username and password cannot be empty!")
        return
    users = load_users()
    if username in users:
        messagebox.showerror("Error", "User already exists!")
        return
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users[username] = hashed.decode()
    save_users(users)
    messagebox.showinfo("Success", f"User {username} registered successfully!")

def login_user(username, entered_password):
    users = load_users()
    hashed = users.get(username)
    if hashed and bcrypt.checkpw(entered_password.encode(), hashed.encode()):
        messagebox.showinfo("Success", f"Login successful! Welcome {username}")
        global current_user
        current_user = username
        login_frame.pack_forget()
        dashboard_frame.pack(fill="both", expand=True)
        refresh_dashboard()
    else:
        messagebox.showerror("Error", "Login failed! Incorrect username or password.")

def login_button_action():
    login_user(username_entry.get(), password_entry.get())

def register_button_action():
    register_user(username_entry.get(), password_entry.get())

# ------------------ Dashboard Functions ------------------
def clear_dashboard():
    income_label.configure(text="Total Income\n$0.00")
    expense_label.configure(text="Total Expense\n$0.00")
    profit_label.configure(text="Net Profit\n$0.00")
    alerts_label.configure(text="")
    header_label.configure(text="")
    budget_label.configure(text="")
    ax.clear()
    ax_line.clear()
    canvas.draw()
    canvas_line.draw()

def refresh_dashboard():
    if not current_business:
        return
    income_label.configure(text=f"Total Income\n{current_business.currency}{current_business.total_income():,.2f}")
    expense_label.configure(text=f"Total Expense\n{current_business.currency}{current_business.total_expense():,.2f}")
    profit_label.configure(text=f"Net Profit\n{current_business.currency}{current_business.net_profit():,.2f}")
    alerts_label.configure(text="\n".join(current_business.alerts()))
    header_label.configure(text=f"Welcome {current_user} | {current_business.name} | {current_business.period}")
    budget_label.configure(text=f"Budget: {current_business.currency}{current_business.budget:,.2f}")

    ax.clear()
    ax.pie(current_business.expense_by_category(), labels=current_business.categories, autopct='%1.1f%%')
    ax.set_title("Expenses by Category")
    canvas.draw()

    ax_line.clear()
    income = current_business.total_income()
    expense = current_business.total_expense()
    net = current_business.net_profit()
    ax_line.plot(["Income", "Expense", "Profit"], [income, expense, net], marker="o")
    ax_line.set_title("Financial Overview")
    canvas_line.draw()
    save_summary()

# ------------------ Add / Select Business ------------------
def add_business():
    global current_business
    name = simpledialog.askstring("Business Name", "Enter business name:")
    if not name:
        return
    currency_window = tk.Toplevel(app)
    currency_window.title("Choose Currency")
    currency_window.geometry("300x200")
    tk.Label(currency_window, text="Choose currency:").pack(pady=10)
    currency_combo = ctk.CTkComboBox(currency_window, values=["₺ Turkish Lira", "$ US Dollar"])
    currency_combo.pack(pady=10)
    currency_combo.set("$ US Dollar")
    tk.Label(currency_window, text="Select Period:").pack(pady=10)
    period_combo = ctk.CTkComboBox(currency_window, values=["Daily", "Weekly", "Monthly"])
    period_combo.pack(pady=10)
    period_combo.set("Monthly")

    def set_currency_period():
        choice = currency_combo.get()
        currency = "₺" if "₺" in choice else "$"
        period = period_combo.get()
        currency_window.destroy()
        budget = simpledialog.askfloat("Budget", "Enter budget amount:")
        if not budget:
            return
        b = Business(name, budget, period, currency)
        businesses.append(b)
        business_list.insert(tk.END, name)
        global current_business
        current_business = b
        clear_dashboard()
        refresh_dashboard()
        save_data()

    ctk.CTkButton(currency_window, text="OK", command=set_currency_period).pack(pady=10)

def select_business(event):
    global current_business
    if not business_list.curselection():
        return
    name = business_list.get(business_list.curselection())
    for b in businesses:
        if b.name == name:
            current_business = b
            break
    refresh_dashboard()

# ------------------ OCR Upload Bill ------------------
def upload_bill():
    if not current_business:
        messagebox.showerror("Error", "No business selected!")
        return
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not file_path:
        return
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    numbers = re.findall(r"\d+\.\d{2}", text)
    if not numbers:
        messagebox.showerror("Error", "Could not detect amount!")
        return
    amount = float(numbers[-1])
    category_window = tk.Toplevel(app)
    category_window.title("Select Category")
    category_window.geometry("300x150")
    tk.Label(category_window, text="Select Category:").pack(pady=10)
    category_combo = ctk.CTkComboBox(category_window, values=current_business.categories)
    category_combo.pack(pady=10)
    category_combo.set(current_business.categories[0])

    def set_category():
        category = category_combo.get()
        bill_number = "OCR-" + datetime.now().strftime("%H%M%S")
        current_business.add_expense(amount, category, bill_number)
        category_window.destroy()
        refresh_dashboard()
        save_data()
        messagebox.showinfo("Success", f"Detected Amount: {current_business.currency}{amount:.2f}")

    ctk.CTkButton(category_window, text="OK", command=set_category).pack(pady=10)

# ------------------ Manual Income/Expense ------------------
def add_income():
    if not current_business:
        return
    amount = simpledialog.askfloat("Income", "Enter income amount:")
    if amount:
        current_business.add_income(amount)
        refresh_dashboard()
        save_data()

def add_expense_manual():
    if not current_business:
        return
    amount = simpledialog.askfloat("Expense", "Enter expense amount:")
    if not amount:
        return
    category_window = tk.Toplevel(app)
    category_window.title("Select Category")
    category_window.geometry("300x150")
    tk.Label(category_window, text="Select Category:").pack(pady=10)
    category_combo = ctk.CTkComboBox(category_window, values=current_business.categories)
    category_combo.pack(pady=10)
    category_combo.set(current_business.categories[0])

    def set_category():
        category = category_combo.get()
        bill_number = simpledialog.askstring("Bill Number", "Enter bill number (optional):")
        current_business.add_expense(amount, category, bill_number)
        category_window.destroy()
        refresh_dashboard()
        save_data()

    ctk.CTkButton(category_window, text="OK", command=set_category).pack(pady=10)

# ------------------ Export CSV ------------------
def export_csv():
    if not current_business:
        messagebox.showerror("Error", "No business selected!")
        return
    default_filename = f"{current_business.name}{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = filedialog.asksaveasfilename(
        initialfile=default_filename,
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        return
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Business Name", current_business.name])
        writer.writerow(["Period", current_business.period])
        writer.writerow(["Budget", f"{current_business.currency}{current_business.budget:,.2f}"])
        writer.writerow(["Total Income", f"{current_business.currency}{current_business.total_income():,.2f}"])
        writer.writerow(["Total Expense", f"{current_business.currency}{current_business.total_expense():,.2f}"])
        writer.writerow(["Net Profit", f"{current_business.currency}{current_business.net_profit():,.2f}"])
        writer.writerow([])
        writer.writerow(["Type", "Amount", "Category", "Bill Number", "Date"])
        for idx, income in enumerate(current_business.incomes, 1):
            date_str = (income["date"].strftime("%Y-%m-%d %H:%M:%S")
                        if isinstance(income["date"], datetime) else str(income["date"]))
            writer.writerow(["Income", f"{current_business.currency}{income['amount']:,.2f}", "-",
                             f"INC-{idx:03}", date_str])
        for idx, expense in enumerate(current_business.expenses, 1):
            date_str = (expense["date"].strftime("%Y-%m-%d %H:%M:%S")
                        if isinstance(expense["date"], datetime) else str(expense["date"]))
            writer.writerow(["Expense", f"{current_business.currency}{expense['amount']:,.2f}",
                             expense["category"], expense.get("bill_number", f"EXP-{idx:03}"), date_str])
    messagebox.showinfo("Success", f"CSV exported successfully!\nFile: {file_path}")

# ------------------ Export Excel ------------------
def export_excel():
    if not current_business:
        messagebox.showerror("Error", "No business selected!")
        return
    folder = f"Reports/{current_business.name}/{current_business.period}"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{current_business.name}Report{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Report"
    ws.append(["Business Name", current_business.name])
    ws.append(["Period", current_business.period])
    ws.append(["Budget", current_business.currency + str(current_business.budget)])
    ws.append(["Total Income", current_business.currency + str(current_business.total_income())])
    ws.append(["Total Expense", current_business.currency + str(current_business.total_expense())])
    ws.append(["Net Profit", current_business.currency + str(current_business.net_profit())])
    ws.append([])
    ws.append(["TYPE", "Amount", "Category", "Bill Number", "Date"])
    for income in current_business.incomes:
        ws.append(["Income", current_business.currency + str(income["amount"]), "-", "-",
                   income["date"].strftime("%Y-%m-%d %H:%M:%S")])
    for expense in current_business.expenses:
        ws.append(["Expense", current_business.currency + str(expense["amount"]),
                   expense["category"], expense.get("bill_number", ""),
                   expense["date"].strftime("%Y-%m-%d %H:%M:%S")])
    wb.save(filename)
    try:
        if platform.system() == "Windows":
            os.startfile(filename)
        elif platform.system() == "Darwin":
            subprocess.call(("open", filename))
        else:
            subprocess.call(("xdg-open", filename))
    except:
        messagebox.showinfo("Saved", f"File saved at:\n{filename}")
        return
    messagebox.showinfo("Success", f"Excel exported and opened successfully!\nFile: {filename}")

# ------------------ Archive ------------------
def open_archive():
    if not current_business:
        return
    folder = f"Reports/{current_business.name}/{current_business.period}"
    os.makedirs(folder, exist_ok=True)
    archive = tk.Toplevel(app)
    archive.title(f"{current_business.name} Archive")
    listbox = tk.Listbox(archive, width=80)
    listbox.pack(fill="both", expand=True)
    files = sorted(os.listdir(folder))
    for f in files:
        listbox.insert(tk.END, f)
    notes_label = ctk.CTkLabel(archive, text="Notes:")
    notes_label.pack(pady=5)
    notes_entry = ctk.CTkEntry(archive, width=400)
    notes_entry.pack(pady=5)
    notes_entry.insert(0, getattr(current_business, "notes", ""))

    def save_notes():
        current_business.notes = notes_entry.get()
        save_data()
        messagebox.showinfo("Saved", "Notes saved successfully!")

    ctk.CTkButton(archive, text="Save Notes", command=save_notes).pack(pady=5)

    def open_selected(event=None):
        if not listbox.curselection():
            return
        selected = listbox.get(listbox.curselection())
        os.startfile(os.path.join(folder, selected))

    listbox.bind("<Double-Button-1>", open_selected)

# ------------------ UI Setup ------------------
app = ctk.CTk()
app.title("Business Financial Monitoring System")
app.geometry("1500x900")
load_data()

# ------------------ Login Frame ------------------
login_frame = ctk.CTkFrame(app)
login_frame.pack(fill="both", expand=True)

ctk.CTkLabel(login_frame, text="Business Financial Monitoring",
             font=ctk.CTkFont(size=28, weight="bold"), text_color="#00f5ff").pack(pady=40)
username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username", width=300)
username_entry.pack(pady=10)
password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=300)
password_entry.pack(pady=10)
ctk.CTkButton(login_frame, text="Login", command=login_button_action, width=200,
              fg_color="#334647", hover_color="#00ff9c").pack(pady=10)
ctk.CTkButton(login_frame, text="Register", command=register_button_action, width=200,
              fg_color="#65500A", hover_color="#00ff9c").pack()

# ------------------ Dashboard Frame ------------------
dashboard_frame = ctk.CTkFrame(app)

header_frame = ctk.CTkFrame(dashboard_frame, height=80)
header_frame.pack(fill="x")
header_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
header_label.pack(side="left", padx=20)
budget_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=16))
budget_label.pack(side="right", padx=20)

main_container = ctk.CTkFrame(dashboard_frame)
main_container.pack(fill="both", expand=True)

# ------------------ Sidebar ------------------
sidebar = ctk.CTkFrame(main_container, width=250)
sidebar.pack(side="left", fill="y", padx=10, pady=10)

business_list = tk.Listbox(sidebar)
business_list.pack(fill="both", expand=True)
business_list.bind("<<ListboxSelect>>", select_business)

add_business_btn = ctk.CTkButton(sidebar, text="➕ Add Business", command=add_business,
                                  width=220, height=50, fg_color="#00f5ff", hover_color="#00ff9c",
                                  corner_radius=20, font=ctk.CTkFont(size=14, weight="bold"))
add_business_btn.pack(pady=10)

for b in businesses:
    business_list.insert(tk.END, b.name)

# ------------------ Main Content ------------------
content = ctk.CTkFrame(main_container)
content.pack(side="right", fill="both", expand=True)

summary = ctk.CTkFrame(content)
summary.pack(fill="x", pady=20)
income_label = ctk.CTkLabel(summary, text="", font=ctk.CTkFont(size=14))
income_label.pack(side="left", expand=True)
expense_label = ctk.CTkLabel(summary, text="", font=ctk.CTkFont(size=14))
expense_label.pack(side="left", expand=True)
profit_label = ctk.CTkLabel(summary, text="", font=ctk.CTkFont(size=14))
profit_label.pack(side="left", expand=True)

# ------------------ Buttons ------------------
buttons_frame = ctk.CTkFrame(content)
buttons_frame.pack(fill="x", pady=10)

def styled_button(text, command):
    return ctk.CTkButton(buttons_frame, text=text, command=command, width=160, height=50,
                         fg_color="#11583f", hover_color="#9ea5a3", corner_radius=20,
                         font=ctk.CTkFont(size=12, weight="bold"))

add_income_btn = styled_button("💰 Add Income", add_income)
add_income_btn.pack(side="left", padx=10)
add_expense_btn = styled_button("💸 Add Expense", add_expense_manual)
add_expense_btn.pack(side="left", padx=10)
upload_bill_btn = styled_button("📄 Upload Bill", upload_bill)
upload_bill_btn.pack(side="left", padx=10)
export_csv_btn = styled_button("📁 Export CSV", export_csv)
export_csv_btn.pack(side="left", padx=10)
export_excel_btn = styled_button("📊 Export Excel", export_excel)
export_excel_btn.pack(side="left", padx=10)
archive_btn = styled_button("🗂 Open Archive", open_archive)
archive_btn.pack(side="left", padx=10)
ToolTip(archive_btn, "View past reports and add notes")

alerts_label = ctk.CTkLabel(content, text="", fg_color="transparent",
                             text_color="red", font=ctk.CTkFont(size=14))
alerts_label.pack(pady=10)

# ------------------ Matplotlib Plots ------------------
fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=content)
canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

fig_line, ax_line = plt.subplots(figsize=(5, 4))
canvas_line = FigureCanvasTkAgg(fig_line, master=content)
canvas_line.get_tk_widget().pack(side="right", fill="both", expand=True)

# ------------------ Start App ------------------
app.mainloop()
