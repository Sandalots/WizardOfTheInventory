import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from google import genai

# ==========================================
# SETUP: Add your Gemini API Key here
# ==========================================
API_KEY = "YOUR_API_KEY_HERE"

# Initialize the NEW client
client = genai.Client(api_key=API_KEY)
MODEL_ID = 'gemini-2.5-flash'  # The current recommended fast model

# Set the theme and color scheme for CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class WizardOfTheInventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- APP BRANDING ---
        self.title("Wizard Of The Inventory")
        self.geometry("900x650")
        self.df = None

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT SIDEBAR
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Adjusted to push bottom elements down

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Wizard Of The\nInventory",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Upload Section
        self.upload_btn = ctk.CTkButton(self.sidebar_frame, text="Upload CSV Inventory", command=self.upload_csv)
        self.upload_btn.grid(row=1, column=0, padx=20, pady=10)

        self.file_label = ctk.CTkLabel(self.sidebar_frame, text="No file loaded.", text_color="gray")
        self.file_label.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Actions
        self.summary_btn = ctk.CTkButton(self.sidebar_frame, text="Generate Summary", command=self.generate_summary,
                                         state="disabled")
        self.summary_btn.grid(row=3, column=0, padx=20, pady=10)

        # NEW: View Data Button
        self.view_data_btn = ctk.CTkButton(self.sidebar_frame, text="View Raw Data", command=self.view_data,
                                           state="disabled", fg_color="transparent", border_width=2,
                                           text_color=("gray10", "#DCE4EE"))
        self.view_data_btn.grid(row=4, column=0, padx=20, pady=10)

        # Appearance Toggle
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("System")

        # ==========================================
        # RIGHT MAIN CONTENT AREA
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Tabs for organizing content
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        self.tabview.add("General Summary")
        self.tabview.add("Q&A Chat")

        # --- Tab 1: Summary ---
        self.tabview.tab("General Summary").grid_rowconfigure(0, weight=1)
        self.tabview.tab("General Summary").grid_columnconfigure(0, weight=1)
        self.summary_text = ctk.CTkTextbox(self.tabview.tab("General Summary"), wrap="word", font=ctk.CTkFont(size=14))
        self.summary_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Tab 2: Q&A Chat ---
        self.tabview.tab("Q&A Chat").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Q&A Chat").grid_columnconfigure(0, weight=1)

        self.answer_text = ctk.CTkTextbox(self.tabview.tab("Q&A Chat"), wrap="word", font=ctk.CTkFont(size=14))
        self.answer_text.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 0))

        # Q&A Input Area
        self.query_entry = ctk.CTkEntry(self.tabview.tab("Q&A Chat"),
                                        placeholder_text="Ask the Wizard (e.g., 'How is the milk doing?')...")
        self.query_entry.grid(row=1, column=0, sticky="ew", padx=(10, 10), pady=10)

        self.ask_btn = ctk.CTkButton(self.tabview.tab("Q&A Chat"), text="Ask AI", command=self.ask_question, width=100,
                                     state="disabled")
        self.ask_btn.grid(row=1, column=1, sticky="e", padx=(0, 10), pady=10)

        # ==========================================
        # CONFIGURE BOLD TAGS FOR MARKDOWN
        # ==========================================
        bold_font = ctk.CTkFont(size=14, weight="bold")
        self.summary_text._textbox.tag_config("bold", font=bold_font)
        self.answer_text._textbox.tag_config("bold", font=bold_font)

    # --- LOGIC ---

    def insert_markdown_text(self, textbox, text):
        """A lightweight markdown parser for Tkinter text boxes."""
        parts = text.split("**")
        for i, part in enumerate(parts):
            if i % 2 == 1:
                textbox.insert("end", part, "bold")
            else:
                textbox.insert("end", part)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                filename = file_path.split('/')[-1]
                self.file_label.configure(text=f"Loaded: {filename}", text_color="green")

                # Enable the buttons
                self.summary_btn.configure(state="normal")
                self.ask_btn.configure(state="normal")
                self.view_data_btn.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def view_data(self):
        """Opens a popup window displaying the CSV data in a table."""
        if self.df is None:
            return

        # Create a popup window
        data_window = ctk.CTkToplevel(self)
        data_window.title("Raw CSV Data")
        data_window.geometry("800x400")

        # Ensure it stays on top initially
        data_window.attributes("-topmost", True)
        data_window.after(100, lambda: data_window.attributes("-topmost", False))

        frame = ctk.CTkFrame(data_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Treeview
        tree = ttk.Treeview(frame)

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout for table and scrollbars
        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Define columns
        tree["columns"] = list(self.df.columns)
        tree["show"] = "headings"  # Hides the default empty first column

        for col in self.df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        # Insert data
        for index, row in self.df.iterrows():
            tree.insert("", "end", values=list(row))

    def generate_summary(self):
        if self.df is None:
            return

        self.tabview.set("General Summary")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "Consulting the crystal ball... please wait.\n")
        self.update()

        data_str = self.df.to_string(index=False)
        prompt = f"""
        You are an expert agricultural business analyst, known as the Wizard of the Inventory. 
        I am providing you with 30 days of farm stock data.
        The rows are items, the columns are dates, and the values are remaining stock.

        Please provide a short, punchy summary of the overall inventory performance. 
        Identify what is selling out fast (hotcakes), what is dead weight, and give a brief recommendation.
        Keep it simple, natural, and business-focused. Use markdown bullet points for readability.

        Data:
        {data_str}
        """

        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            self.summary_text.delete("1.0", "end")
            self.insert_markdown_text(self.summary_text, response.text)
        except Exception as e:
            self.summary_text.insert("end", f"\nError communicating with AI: {e}")

    def ask_question(self):
        if self.df is None:
            return

        user_question = self.query_entry.get()
        if not user_question.strip():
            messagebox.showwarning("Warning", "Please type a question first.")
            return

        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("end", f"You asked: {user_question}\n\nThinking...\n")
        self.update()

        data_str = self.df.to_string(index=False)
        prompt = f"""
        You are the 'Wizard of the Inventory', a helpful inventory assistant for a small farm. 
        Based on the following 30-day stock data (rows = items, columns = dates, values = remaining stock), 
        answer the user's specific question using natural language. 
        If they ask how an item is doing, tell them if it's booming, needs restocking, or isn't selling well.

        Data:
        {data_str}

        User Question: {user_question}
        """

        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            self.answer_text.delete("1.0", "end")
            self.insert_markdown_text(self.answer_text, f"You asked: {user_question}\n\n")
            self.insert_markdown_text(self.answer_text, response.text)
            self.answer_text.insert("end", "\n\n" + "-" * 40 + "\n\n")

            self.query_entry.delete(0, "end")
        except Exception as e:
            self.answer_text.insert("end", f"\nError communicating with AI: {e}")


if __name__ == "__main__":
    app = WizardOfTheInventoryApp()
    app.mainloop()