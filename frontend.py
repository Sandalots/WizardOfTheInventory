import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import google.generativeai as genai

# ==========================================
# SETUP: Add your Gemini API Key here
# ==========================================
API_KEY = "AIzaSyDOIkEt65cf9VbDRDe8UxY_BP0YA5LvBj0"
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
# We use gemini-1.5-flash as it is fast and excellent for text/data tasks
model = genai.GenerativeModel('gemini-1.5-flash')


class FarmStockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Farm Stock AI Analyzer")
        self.root.geometry("700x800")
        self.df = None

        # --- UI ELEMENTS ---

        # 1. Upload Section
        self.upload_btn = tk.Button(root, text="Upload CSV Inventory", command=self.upload_csv,
                                    font=('Arial', 12, 'bold'))
        self.upload_btn.pack(pady=15)

        self.file_label = tk.Label(root, text="No file loaded.", fg="gray")
        self.file_label.pack()

        # 2. General Summary Section
        self.summary_btn = tk.Button(root, text="Generate Performance Summary", command=self.generate_summary,
                                     state=tk.DISABLED)
        self.summary_btn.pack(pady=10)

        self.summary_text = scrolledtext.ScrolledText(root, height=10, width=80, wrap=tk.WORD, font=('Arial', 10))
        self.summary_text.pack(pady=5)

        # 3. Q&A Section
        tk.Label(root, text="Ask about specific stock (e.g., 'How is the milk doing?'):",
                 font=('Arial', 11, 'bold')).pack(pady=(20, 5))

        self.query_entry = tk.Entry(root, width=70, font=('Arial', 12))
        self.query_entry.pack(pady=5)

        self.ask_btn = tk.Button(root, text="Ask AI", command=self.ask_question, state=tk.DISABLED)
        self.ask_btn.pack(pady=5)

        self.answer_text = scrolledtext.ScrolledText(root, height=10, width=80, wrap=tk.WORD, font=('Arial', 10))
        self.answer_text.pack(pady=5)

    # --- LOGIC ---

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.file_label.config(text=f"Loaded: {file_path.split('/')[-1]}", fg="green")
                # Enable the AI buttons now that data is loaded
                self.summary_btn.config(state=tk.NORMAL)
                self.ask_btn.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def generate_summary(self):
        if self.df is None:
            return

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "Analyzing data... please wait.\n")
        self.root.update()

        # Convert the dataframe to a string representation for the LLM
        data_str = self.df.to_string(index=False)

        prompt = f"""
        You are an expert agricultural business analyst. I am providing you with 30 days of farm stock data.
        The rows are items, the columns are dates, and the values are remaining stock.

        Please provide a short, punchy summary of the overall inventory performance. 
        Identify what is selling out fast (hotcakes), what is dead weight, and give a brief recommendation.
        Keep it simple, natural, and business-focused.

        Data:
        {data_str}
        """

        try:
            response = model.generate_content(prompt)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, response.text)
        except Exception as e:
            self.summary_text.insert(tk.END, f"\nError communicating with AI: {e}")

    def ask_question(self):
        if self.df is None:
            return

        user_question = self.query_entry.get()
        if not user_question.strip():
            messagebox.showwarning("Warning", "Please type a question first.")
            return

        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "Thinking...\n")
        self.root.update()

        data_str = self.df.to_string(index=False)

        prompt = f"""
        You are a helpful inventory assistant for a small farm. 
        Based on the following 30-day stock data (rows = items, columns = dates, values = remaining stock), 
        answer the user's specific question using natural language. 
        If they ask how an item is doing, tell them if it's booming, needs restocking, or isn't selling well.

        Data:
        {data_str}

        User Question: {user_question}
        """

        try:
            response = model.generate_content(prompt)
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, response.text)
        except Exception as e:
            self.answer_text.insert(tk.END, f"\nError communicating with AI: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FarmStockApp(root)
    root.mainloop()