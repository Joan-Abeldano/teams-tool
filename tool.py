import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

if getattr(sys, "frozen", False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(application_path, "f1_teams.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()

class F1DatabaseApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Teams Tool for the Italian🤌🤌🤌")
        self.root.geometry("400x390")

        init_db()

        self.create_add_team_section()
        self.create_filter_section()
        self.create_manage_section()

    def get_all_years(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(start_year), MAX(end_year) FROM teams")
        result = cursor.fetchone()
        conn.close()

        min_year, max_year = result
        if min_year is not None and max_year is not None:
            return [str(yr) for yr in range(min_year, max_year + 1)]
        return []

    def update_year_dropdown(self):
        years = self.get_all_years()
        self.year_dropdown["values"] = years
        if years:
            self.year_dropdown.current(0)
        else:
            self.year_dropdown.set("")

    def create_add_team_section(self):
        frame = ttk.LabelFrame(self.root, text="Add New Team", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Team Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(frame, width=25)
        self.name_entry.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="First Year:").grid(row=1, column=0, sticky="w", pady=2)
        self.start_entry = ttk.Entry(frame, width=25)
        self.start_entry.grid(row=1, column=1, pady=2)

        ttk.Label(frame, text="Last Year:").grid(row=2, column=0, sticky="w", pady=2)
        self.end_entry = ttk.Entry(frame, width=25)
        self.end_entry.grid(row=2, column=1, pady=2)

        self.name_entry.bind("<Return>", lambda event: self.add_team())
        self.start_entry.bind("<Return>", lambda event: self.add_team())
        self.end_entry.bind("<Return>", lambda event: self.add_team())

        add_btn = ttk.Button(frame, text="Add Team", command=self.add_team)
        add_btn.grid(row=3, column=0, columnspan=2, pady=5)

    def create_filter_section(self):
        frame = ttk.LabelFrame(self.root, text="Filter Teams by Year", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Select Year:").pack(side="left", padx=5)

        self.year_dropdown = ttk.Combobox(frame, width=12, state="readonly")
        self.year_dropdown.pack(side="left", padx=5)

        search_btn = ttk.Button(frame, text="Show Teams", command=self.show_teams_popup)
        search_btn.pack(side="left", padx=5)

        self.update_year_dropdown()

    def create_manage_section(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        manage_btn = ttk.Button(frame, text="Manage All Teams (Edit/Delete)", command=self.show_manage_popup)
        manage_btn.pack(fill="x")

    def add_team(self):
        name = self.name_entry.get().strip()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()

        if not name or not start or not end:
            messagebox.showwarning("Input Error", "Fill all inputs lol.")
            return

        try:
            start_yr = int(start)
            end_yr = int(end)
        except ValueError:
            messagebox.showwarning("Input Error", "Year has to be a number you idiot😭.")
            return

        if start_yr > end_yr:
            messagebox.showwarning("Input Error", "First year lower than last😭.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teams (name, start_year, end_year) VALUES (?, ?, ?)",
            (name, start_yr, end_yr),
        )
        conn.commit()
        conn.close()

        self.name_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.name_entry.focus()

        self.update_year_dropdown()

        messagebox.showinfo("Success", f"Added team '{name}' successfully.")

    def show_teams_popup(self):
        selected_year = self.year_dropdown.get()
        if not selected_year:
            messagebox.showwarning("Selection Error", "Input something first lmao😭.")
            return

        year = int(selected_year)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name
            FROM teams
            WHERE ? BETWEEN start_year AND end_year
            ORDER BY name ASC
        """,
            (year,),
        )
        rows = cursor.fetchall()
        conn.close()

        num_teams = len(rows)
        tree_height = max(4, min(num_teams, 20))
        popup_height = max(300, 200 + (num_teams * 22))

        popup = tk.Toplevel(self.root)
        popup.title(f"Teams in {year}")
        popup.geometry(f"500x{popup_height}")
        popup.grab_set()

        ttk.Label(
            popup,
            text=f"Teams in {year} ({num_teams})",
            font=("Helvetica", 11, "bold"),
        ).pack(pady=10)

        columns = ("name")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=tree_height)
        tree.heading("name", text="Team Name")

        tree.column("name", width=240)

        tree.pack(fill="both", expand=True, padx=10, pady=5)

        for row in rows:
            tree.insert("", tk.END, values=row)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def show_manage_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Manage Teams Database")
        popup.geometry("550x450")
        popup.grab_set()

        ttk.Label(
            popup,
            text="All Teams Database",
            font=("Helvetica", 11, "bold"),
        ).pack(pady=10)

        columns = ("id", "name", "start", "end")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=12)
        tree.heading("id", text="ID")
        tree.heading("name", text="Team Name")
        tree.heading("start", text="First Year")
        tree.heading("end", text="Last Year")

        tree.column("id", width=40, anchor="center")
        tree.column("name", width=230)
        tree.column("start", width=100, anchor="center")
        tree.column("end", width=100, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=5)

        def load_data():
            for item in tree.get_children():
                tree.delete(item)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, start_year, end_year FROM teams ORDER BY name ASC")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            conn.close()

        load_data()

        form_frame = ttk.LabelFrame(popup, text="Edit Selected Team", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=2)
        edit_name_entry = ttk.Entry(form_frame, width=20)
        edit_name_entry.grid(row=0, column=1, padx=2)

        ttk.Label(form_frame, text="First:").grid(row=0, column=2, sticky="w", padx=2)
        edit_start_entry = ttk.Entry(form_frame, width=10)
        edit_start_entry.grid(row=0, column=3, padx=2)

        ttk.Label(form_frame, text="Last:").grid(row=0, column=4, sticky="w", padx=2)
        edit_end_entry = ttk.Entry(form_frame, width=10)
        edit_end_entry.grid(row=0, column=5, padx=2)

        selected_id = tk.StringVar()

        def on_select(event):
            selected_items = tree.selection()
            if not selected_items:
                return
            item = tree.item(selected_items[0])
            values = item["values"]
            selected_id.set(values[0])
            edit_name_entry.delete(0, tk.END)
            edit_name_entry.insert(0, values[1])
            edit_start_entry.delete(0, tk.END)
            edit_start_entry.insert(0, values[2])
            edit_end_entry.delete(0, tk.END)
            edit_end_entry.insert(0, values[3])

        tree.bind("<<TreeviewSelect>>", on_select)

        def update_team():
            team_id = selected_id.get()
            if not team_id:
                messagebox.showwarning("Error", "Select a team first brotha.")
                return
            name = edit_name_entry.get().strip()
            start = edit_start_entry.get().strip()
            end = edit_end_entry.get().strip()

            if not name or not start or not end:
                messagebox.showwarning("Error", "Fill all fields.")
                return

            try:
                start_yr = int(start)
                end_yr = int(end)
            except ValueError:
                messagebox.showwarning("Error", "Year has to be a number you idiot😭.")
                return

            if start_yr > end_yr:
                messagebox.showwarning("Error", "First year lower than last😭.")
                return

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE teams SET name = ?, start_year = ?, end_year = ? WHERE id = ?",
                (name, start_yr, end_yr, team_id),
            )
            conn.commit()
            conn.close()
            load_data()
            self.update_year_dropdown()
            messagebox.showinfo("Success", "Team updated successfully.")

        def delete_team():
            team_id = selected_id.get()
            if not team_id:
                messagebox.showwarning("Error", "Select a team first brotha.")
                return
            if messagebox.askyesno("Confirm", "Are you sure?"):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
                conn.commit()
                conn.close()
                load_data()
                self.update_year_dropdown()
                edit_name_entry.delete(0, tk.END)
                edit_start_entry.delete(0, tk.END)
                edit_end_entry.delete(0, tk.END)
                selected_id.set("")
                messagebox.showinfo("Success", "Team deleted.")

        btn_frame = ttk.Factory if hasattr(ttk, 'Factory') else ttk.Frame(popup)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Save Changes", command=update_team).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Team", command=delete_team).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=popup.destroy).pack(side="left", padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = F1DatabaseApp(root)
    root.mainloop()
