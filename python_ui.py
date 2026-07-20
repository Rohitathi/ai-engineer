import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from connect_ai.agent.multi_agents import ManagerAgent


class AgentUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect AI • Multi-Agent Studio")
        self.geometry("860x620")
        self.minsize(760, 520)
        self.configure(bg="#0f172a")
        self.agent = ManagerAgent()

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg="#111827", pady=16)
        header.pack(fill="x")

        title = tk.Label(header, text="Connect AI", font=("Segoe UI", 20, "bold"), fg="#f8fafc", bg="#111827")
        title.pack(anchor="w", padx=20)

        subtitle = tk.Label(header, text="Coordinate search, recommendations, and automation in one place", font=("Segoe UI", 10), fg="#cbd5e1", bg="#111827")
        subtitle.pack(anchor="w", padx=20)

        body = tk.Frame(self, bg="#0f172a")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        self.chat_area = tk.Text(body, wrap=tk.WORD, bg="#111827", fg="#f8fafc", insertbackground="#f8fafc", padx=12, pady=12, relief="flat", font=("Segoe UI", 11))
        self.chat_area.tag_configure("user", foreground="#93c5fd")
        self.chat_area.tag_configure("assistant", foreground="#86efac")
        self.chat_area.tag_configure("meta", foreground="#94a3b8")
        self.chat_area.pack(fill="both", expand=True)
        self.chat_area.insert(tk.END, "Welcome to Connect AI\n", "meta")
        self.chat_area.insert(tk.END, "Ask for recommendations, automation, or search help.\n", "assistant")
        self.chat_area.config(state=tk.DISABLED)

        input_frame = tk.Frame(body, bg="#0f172a")
        input_frame.pack(fill="x", pady=(10, 0))

        self.prompt_entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.prompt_entry.pack(side=tk.LEFT, fill="x", expand=True)
        self.prompt_entry.bind("<Return>", self.run_prompt)

        run_button = ttk.Button(input_frame, text="Run", command=self.run_prompt)
        run_button.pack(side=tk.LEFT, padx=(8, 0))

        quick_frame = tk.Frame(body, bg="#0f172a")
        quick_frame.pack(fill="x", pady=(8, 0))

        for text in ["recommend someone interesting", "automate my digest", "find recent insights"]:
            btn = ttk.Button(quick_frame, text=text, command=lambda value=text: self._quick_run(value))
            btn.pack(side=tk.LEFT, padx=(0, 6), pady=2)

    def _quick_run(self, text):
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, text)
        self.run_prompt()

    def run_prompt(self, event=None):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Input required", "Please enter a prompt first.")
            return

        self.prompt_entry.delete(0, tk.END)
        self._append_message("You", prompt, "user")
        self.update_idletasks()

        try:
            result = self.agent.dispatch(prompt)
            self._append_message("Multi-Agent", str(result), "assistant")
        except Exception as exc:
            self._append_message("System", f"Error: {exc}", "meta")

    def _append_message(self, sender, message, tag):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: ", "meta")
        self.chat_area.insert(tk.END, f"{message}\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.configure(state=tk.DISABLED)


if __name__ == "__main__":
    app = AgentUI()
    app.mainloop()
