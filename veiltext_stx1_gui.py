import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from veiltext_stx1_recovery import decrypt_veiltext, encrypt_veiltext


class VeilTextApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("VeilText STX1 Tool")
        self.geometry("1080x720")
        self.minsize(860, 600)

        self.password_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main,
            text="VeilText STX1 Encryption + Recovery",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor=tk.W, pady=(0, 10))

        password_frame = ttk.LabelFrame(main, text="Password", padding=10)
        password_frame.pack(fill=tk.X, pady=(0, 10))

        password_frame.columnconfigure(1, weight=1)
        password_frame.columnconfigure(3, weight=1)

        ttk.Label(password_frame, text="Password:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8)
        )
        self.password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="*",
        )
        self.password_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 16))

        ttk.Label(password_frame, text="Confirm:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8)
        )
        self.confirm_entry = ttk.Entry(
            password_frame,
            textvariable=self.confirm_var,
            show="*",
        )
        self.confirm_entry.grid(row=0, column=3, sticky=tk.EW, padx=(0, 12))

        ttk.Checkbutton(
            password_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
        ).grid(row=0, column=4, sticky=tk.W)

        body = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True)

        plain_frame = ttk.LabelFrame(body, text="Plaintext", padding=8)
        cipher_frame = ttk.LabelFrame(body, text="STX1 Ciphertext", padding=8)
        body.add(plain_frame, weight=1)
        body.add(cipher_frame, weight=1)

        self.plain_text = tk.Text(
            plain_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 10),
        )
        plain_scroll = ttk.Scrollbar(
            plain_frame, orient=tk.VERTICAL, command=self.plain_text.yview
        )
        self.plain_text.configure(yscrollcommand=plain_scroll.set)
        self.plain_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plain_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cipher_text = tk.Text(
            cipher_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 10),
        )
        cipher_scroll = ttk.Scrollbar(
            cipher_frame, orient=tk.VERTICAL, command=self.cipher_text.yview
        )
        self.cipher_text.configure(yscrollcommand=cipher_scroll.set)
        self.cipher_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cipher_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(10, 6))

        ttk.Button(
            action_frame,
            text="Encrypt  →",
            command=self.encrypt_text,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            action_frame,
            text="←  Decrypt / Recover",
            command=self.decrypt_text,
        ).pack(side=tk.LEFT, padx=(0, 18))

        ttk.Button(
            action_frame,
            text="Open Plaintext",
            command=self.open_plaintext,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            action_frame,
            text="Open Ciphertext",
            command=self.open_ciphertext,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            action_frame,
            text="Save Plaintext",
            command=self.save_plaintext,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            action_frame,
            text="Save Ciphertext",
            command=self.save_ciphertext,
        ).pack(side=tk.LEFT, padx=(0, 8))

        second_actions = ttk.Frame(main)
        second_actions.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(
            second_actions,
            text="Copy Plaintext",
            command=lambda: self.copy_text(self.plain_text, "Plaintext copied"),
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            second_actions,
            text="Copy Ciphertext",
            command=lambda: self.copy_text(self.cipher_text, "Ciphertext copied"),
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            second_actions,
            text="Clear",
            command=self.clear_all,
        ).pack(side=tk.LEFT)

        ttk.Label(
            main,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(6, 3),
        ).pack(fill=tk.X, pady=(4, 0))

    def _toggle_password_visibility(self) -> None:
        show = "" if self.show_password_var.get() else "*"
        self.password_entry.configure(show=show)
        self.confirm_entry.configure(show=show)

    def encrypt_text(self) -> None:
        plaintext = self.plain_text.get("1.0", "end-1c")
        password = self.password_var.get()
        confirmation = self.confirm_var.get()

        if not plaintext:
            messagebox.showwarning("VeilText", "Plaintext is empty.")
            return
        if not password:
            messagebox.showwarning("VeilText", "Password is empty.")
            return
        if password != confirmation:
            messagebox.showerror("VeilText", "Password confirmation does not match.")
            return

        try:
            ciphertext = encrypt_veiltext(plaintext, password)
            self.cipher_text.delete("1.0", tk.END)
            self.cipher_text.insert("1.0", ciphertext)
            self.status_var.set("Encryption completed successfully")
        except Exception as exc:
            messagebox.showerror("Encryption failed", str(exc))
            self.status_var.set("Encryption failed")

    def decrypt_text(self) -> None:
        ciphertext = self.cipher_text.get("1.0", "end-1c").strip()
        password = self.password_var.get()

        if not ciphertext:
            messagebox.showwarning("VeilText", "Ciphertext is empty.")
            return
        if not password:
            messagebox.showwarning("VeilText", "Password is empty.")
            return

        try:
            plaintext = decrypt_veiltext(ciphertext, password)
            self.plain_text.delete("1.0", tk.END)
            self.plain_text.insert("1.0", plaintext)
            self.status_var.set("Recovery completed successfully")
        except Exception as exc:
            messagebox.showerror("Recovery failed", str(exc))
            self.status_var.set("Recovery failed")

    def open_plaintext(self) -> None:
        path = filedialog.askopenfilename(
            title="Open plaintext UTF-8 file",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.plain_text.delete("1.0", tk.END)
            self.plain_text.insert("1.0", content)
            self.status_var.set(f"Loaded plaintext: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))

    def open_ciphertext(self) -> None:
        path = filedialog.askopenfilename(
            title="Open STX1 ciphertext file",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.cipher_text.delete("1.0", tk.END)
            self.cipher_text.insert("1.0", content.strip())
            self.status_var.set(f"Loaded ciphertext: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))

    def save_plaintext(self) -> None:
        content = self.plain_text.get("1.0", "end-1c")
        if not content:
            messagebox.showwarning("VeilText", "Plaintext is empty.")
            return

        path = filedialog.asksaveasfilename(
            title="Save plaintext",
            defaultextension=".txt",
            initialfile="recovered.txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(f"Saved plaintext: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def save_ciphertext(self) -> None:
        content = self.cipher_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("VeilText", "Ciphertext is empty.")
            return

        path = filedialog.asksaveasfilename(
            title="Save STX1 ciphertext",
            defaultextension=".txt",
            initialfile="encrypted_stx1.txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(f"Saved ciphertext: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def copy_text(self, widget: tk.Text, status: str) -> None:
        content = widget.get("1.0", "end-1c")
        if not content:
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self.status_var.set(status)

    def clear_all(self) -> None:
        self.plain_text.delete("1.0", tk.END)
        self.cipher_text.delete("1.0", tk.END)
        self.password_var.set("")
        self.confirm_var.set("")
        self.status_var.set("Ready")
        self.password_entry.focus_set()


if __name__ == "__main__":
    app = VeilTextApp()
    app.mainloop()
