import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from veiltext_stx1_recovery import decrypt_veiltext, encrypt_veiltext


TEXTS = {
    "en": {
        "window_title": "VeilText STX1 Tool",
        "title": "VeilText STX1 Encryption + Recovery",
        "language": "Language:",
        "password_frame": "Password",
        "password": "Password:",
        "show_password": "Show password",
        "plaintext": "Plaintext",
        "ciphertext": "STX1 Ciphertext",
        "encrypt": "Encrypt  →",
        "decrypt": "←  Decrypt / Recover",
        "open_plain": "Open Plaintext",
        "open_cipher": "Open Ciphertext",
        "save_plain": "Save Plaintext",
        "save_cipher": "Save Ciphertext",
        "copy_plain": "Copy Plaintext",
        "copy_cipher": "Copy Ciphertext",
        "paste_cipher": "Paste Ciphertext",
        "clear": "Clear",
        "ready": "Ready",
        "plain_empty": "Plaintext is empty.",
        "password_empty": "Password is empty.",
        "encrypt_ok": "Encryption completed successfully",
        "encrypt_failed": "Encryption failed",
        "cipher_empty": "Ciphertext is empty.",
        "recover_ok": "Recovery completed successfully",
        "recover_failed": "Recovery failed",
        "open_plain_title": "Open plaintext UTF-8 file",
        "open_cipher_title": "Open STX1 ciphertext file",
        "save_plain_title": "Save plaintext",
        "save_cipher_title": "Save STX1 ciphertext",
        "text_files": "Text files",
        "all_files": "All files",
        "loaded_plain": "Loaded plaintext: {name}",
        "loaded_cipher": "Loaded ciphertext: {name}",
        "saved_plain": "Saved plaintext: {name}",
        "saved_cipher": "Saved ciphertext: {name}",
        "open_failed": "Open failed",
        "save_failed": "Save failed",
        "plain_copied": "Plaintext copied",
        "cipher_copied": "Ciphertext copied",
        "cipher_pasted": "Ciphertext pasted",
        "menu_copy": "Copy",
        "menu_paste": "Paste",
        "menu_select_all": "Select All",
    },
    "zh": {
        "window_title": "VeilText STX1 工具",
        "title": "VeilText STX1 加密与恢复工具",
        "language": "语言：",
        "password_frame": "密码",
        "password": "密码：",
        "show_password": "显示密码",
        "plaintext": "明文",
        "ciphertext": "STX1 密文",
        "encrypt": "加密  →",
        "decrypt": "←  解密 / 恢复",
        "open_plain": "打开明文",
        "open_cipher": "打开密文",
        "save_plain": "保存明文",
        "save_cipher": "保存密文",
        "copy_plain": "复制明文",
        "copy_cipher": "复制密文",
        "paste_cipher": "粘贴密文",
        "clear": "清空",
        "ready": "就绪",
        "plain_empty": "明文为空。",
        "password_empty": "密码为空。",
        "encrypt_ok": "加密成功",
        "encrypt_failed": "加密失败",
        "cipher_empty": "密文为空。",
        "recover_ok": "解密 / 恢复成功",
        "recover_failed": "解密 / 恢复失败",
        "open_plain_title": "打开 UTF-8 明文文件",
        "open_cipher_title": "打开 STX1 密文文件",
        "save_plain_title": "保存明文",
        "save_cipher_title": "保存 STX1 密文",
        "text_files": "文本文件",
        "all_files": "所有文件",
        "loaded_plain": "已加载明文：{name}",
        "loaded_cipher": "已加载密文：{name}",
        "saved_plain": "已保存明文：{name}",
        "saved_cipher": "已保存密文：{name}",
        "open_failed": "打开失败",
        "save_failed": "保存失败",
        "plain_copied": "明文已复制",
        "cipher_copied": "密文已复制",
        "cipher_pasted": "密文已粘贴",
        "menu_copy": "复制",
        "menu_paste": "粘贴",
        "menu_select_all": "全选",
    },
}


class VeilTextApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1080x720")
        self.minsize(860, 600)

        self.language_var = tk.StringVar(value="简体中文")
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar()

        self._build_ui()
        self._update_ui_text()

    def _lang(self) -> str:
        return "zh" if self.language_var.get() == "简体中文" else "en"

    def _t(self, key: str) -> str:
        return TEXTS[self._lang()][key]

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(
            header,
            font=("Segoe UI", 16, "bold"),
        )
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)

        language_box = ttk.Frame(header)
        language_box.pack(side=tk.RIGHT)

        self.language_label = ttk.Label(language_box)
        self.language_label.pack(side=tk.LEFT, padx=(0, 6))

        self.language_combo = ttk.Combobox(
            language_box,
            textvariable=self.language_var,
            values=("简体中文", "English"),
            state="readonly",
            width=12,
        )
        self.language_combo.pack(side=tk.LEFT)
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        self.password_frame = ttk.LabelFrame(main, padding=10)
        self.password_frame.pack(fill=tk.X, pady=(0, 10))
        self.password_frame.columnconfigure(1, weight=1)

        self.password_label = ttk.Label(self.password_frame)
        self.password_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 8))

        self.password_entry = ttk.Entry(
            self.password_frame,
            textvariable=self.password_var,
            show="*",
        )
        self.password_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 12))

        self.show_password_check = ttk.Checkbutton(
            self.password_frame,
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
        )
        self.show_password_check.grid(row=0, column=2, sticky=tk.W)

        body = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True)

        self.plain_frame = ttk.LabelFrame(body, padding=8)
        self.cipher_frame = ttk.LabelFrame(body, padding=8)
        body.add(self.plain_frame, weight=1)
        body.add(self.cipher_frame, weight=1)

        self.plain_text = tk.Text(
            self.plain_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 10),
        )
        plain_scroll = ttk.Scrollbar(
            self.plain_frame, orient=tk.VERTICAL, command=self.plain_text.yview
        )
        self.plain_text.configure(yscrollcommand=plain_scroll.set)
        self.plain_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plain_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cipher_text = tk.Text(
            self.cipher_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 10),
        )
        cipher_scroll = ttk.Scrollbar(
            self.cipher_frame, orient=tk.VERTICAL, command=self.cipher_text.yview
        )
        self.cipher_text.configure(yscrollcommand=cipher_scroll.set)
        self.cipher_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cipher_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._install_text_shortcuts(self.plain_text)
        self._install_text_shortcuts(self.cipher_text)

        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(10, 6))

        self.encrypt_button = ttk.Button(action_frame, command=self.encrypt_text)
        self.encrypt_button.pack(side=tk.LEFT, padx=(0, 8))

        self.decrypt_button = ttk.Button(action_frame, command=self.decrypt_text)
        self.decrypt_button.pack(side=tk.LEFT, padx=(0, 18))

        self.open_plain_button = ttk.Button(action_frame, command=self.open_plaintext)
        self.open_plain_button.pack(side=tk.LEFT, padx=(0, 8))

        self.open_cipher_button = ttk.Button(action_frame, command=self.open_ciphertext)
        self.open_cipher_button.pack(side=tk.LEFT, padx=(0, 8))

        self.save_plain_button = ttk.Button(action_frame, command=self.save_plaintext)
        self.save_plain_button.pack(side=tk.LEFT, padx=(0, 8))

        self.save_cipher_button = ttk.Button(action_frame, command=self.save_ciphertext)
        self.save_cipher_button.pack(side=tk.LEFT, padx=(0, 8))

        second_actions = ttk.Frame(main)
        second_actions.pack(fill=tk.X, pady=(0, 6))

        self.copy_plain_button = ttk.Button(
            second_actions,
            command=lambda: self.copy_text(self.plain_text, "plain_copied"),
        )
        self.copy_plain_button.pack(side=tk.LEFT, padx=(0, 8))

        self.copy_cipher_button = ttk.Button(
            second_actions,
            command=lambda: self.copy_text(self.cipher_text, "cipher_copied"),
        )
        self.copy_cipher_button.pack(side=tk.LEFT, padx=(0, 8))

        self.paste_cipher_button = ttk.Button(
            second_actions,
            command=self.paste_ciphertext,
        )
        self.paste_cipher_button.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_button = ttk.Button(second_actions, command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)

        ttk.Label(
            main,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(6, 3),
        ).pack(fill=tk.X, pady=(4, 0))

    def _install_text_shortcuts(self, widget: tk.Text) -> None:
        widget.bind("<Control-a>", lambda _e, w=widget: self._select_all(w))
        widget.bind("<Control-A>", lambda _e, w=widget: self._select_all(w))
        widget.bind("<Button-3>", lambda e, w=widget: self._show_text_menu(e, w))

    def _select_all(self, widget: tk.Text):
        widget.tag_add(tk.SEL, "1.0", "end-1c")
        widget.mark_set(tk.INSERT, "1.0")
        widget.see("1.0")
        return "break"

    def _show_text_menu(self, event, widget: tk.Text) -> None:
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(
            label=self._t("menu_copy"),
            command=lambda: widget.event_generate("<<Copy>>"),
        )
        menu.add_command(
            label=self._t("menu_paste"),
            command=lambda: widget.event_generate("<<Paste>>"),
        )
        menu.add_separator()
        menu.add_command(
            label=self._t("menu_select_all"),
            command=lambda: self._select_all(widget),
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_language_change(self, _event=None) -> None:
        self._update_ui_text()

    def _update_ui_text(self) -> None:
        self.title(self._t("window_title"))
        self.title_label.configure(text=self._t("title"))
        self.language_label.configure(text=self._t("language"))
        self.password_frame.configure(text=self._t("password_frame"))
        self.password_label.configure(text=self._t("password"))
        self.show_password_check.configure(text=self._t("show_password"))
        self.plain_frame.configure(text=self._t("plaintext"))
        self.cipher_frame.configure(text=self._t("ciphertext"))
        self.encrypt_button.configure(text=self._t("encrypt"))
        self.decrypt_button.configure(text=self._t("decrypt"))
        self.open_plain_button.configure(text=self._t("open_plain"))
        self.open_cipher_button.configure(text=self._t("open_cipher"))
        self.save_plain_button.configure(text=self._t("save_plain"))
        self.save_cipher_button.configure(text=self._t("save_cipher"))
        self.copy_plain_button.configure(text=self._t("copy_plain"))
        self.copy_cipher_button.configure(text=self._t("copy_cipher"))
        self.paste_cipher_button.configure(text=self._t("paste_cipher"))
        self.clear_button.configure(text=self._t("clear"))
        self.status_var.set(self._t("ready"))

    def _toggle_password_visibility(self) -> None:
        show = "" if self.show_password_var.get() else "*"
        self.password_entry.configure(show=show)

    def encrypt_text(self) -> None:
        plaintext = self.plain_text.get("1.0", "end-1c")
        password = self.password_var.get()

        if not plaintext:
            messagebox.showwarning("VeilText", self._t("plain_empty"))
            return
        if not password:
            messagebox.showwarning("VeilText", self._t("password_empty"))
            return
        try:
            ciphertext = encrypt_veiltext(plaintext, password)
            self.cipher_text.delete("1.0", tk.END)
            self.cipher_text.insert("1.0", ciphertext)
            self.cipher_text.tag_add(tk.SEL, "1.0", "end-1c")
            self.cipher_text.mark_set(tk.INSERT, "1.0")
            self.cipher_text.see("1.0")
            self.cipher_text.focus_set()
            self.status_var.set(self._t("encrypt_ok"))
        except Exception as exc:
            messagebox.showerror(self._t("encrypt_failed"), str(exc))
            self.status_var.set(self._t("encrypt_failed"))

    def decrypt_text(self) -> None:
        ciphertext = self.cipher_text.get("1.0", "end-1c").strip()
        password = self.password_var.get()

        if not ciphertext:
            messagebox.showwarning("VeilText", self._t("cipher_empty"))
            return
        if not password:
            messagebox.showwarning("VeilText", self._t("password_empty"))
            return

        try:
            plaintext = decrypt_veiltext(ciphertext, password)
            self.plain_text.delete("1.0", tk.END)
            self.plain_text.insert("1.0", plaintext)
            self.status_var.set(self._t("recover_ok"))
        except Exception as exc:
            messagebox.showerror(self._t("recover_failed"), str(exc))
            self.status_var.set(self._t("recover_failed"))

    def _filetypes(self):
        return [
            (self._t("text_files"), "*.txt"),
            (self._t("all_files"), "*.*"),
        ]

    def open_plaintext(self) -> None:
        path = filedialog.askopenfilename(
            title=self._t("open_plain_title"),
            filetypes=self._filetypes(),
        )
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.plain_text.delete("1.0", tk.END)
            self.plain_text.insert("1.0", content)
            self.status_var.set(self._t("loaded_plain").format(name=Path(path).name))
        except Exception as exc:
            messagebox.showerror(self._t("open_failed"), str(exc))

    def open_ciphertext(self) -> None:
        path = filedialog.askopenfilename(
            title=self._t("open_cipher_title"),
            filetypes=self._filetypes(),
        )
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.cipher_text.delete("1.0", tk.END)
            self.cipher_text.insert("1.0", content.strip())
            self.status_var.set(self._t("loaded_cipher").format(name=Path(path).name))
        except Exception as exc:
            messagebox.showerror(self._t("open_failed"), str(exc))

    def save_plaintext(self) -> None:
        content = self.plain_text.get("1.0", "end-1c")
        if not content:
            messagebox.showwarning("VeilText", self._t("plain_empty"))
            return

        path = filedialog.asksaveasfilename(
            title=self._t("save_plain_title"),
            defaultextension=".txt",
            initialfile="recovered.txt",
            filetypes=self._filetypes(),
        )
        if not path:
            return

        try:
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(self._t("saved_plain").format(name=Path(path).name))
        except Exception as exc:
            messagebox.showerror(self._t("save_failed"), str(exc))

    def save_ciphertext(self) -> None:
        content = self.cipher_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("VeilText", self._t("cipher_empty"))
            return

        path = filedialog.asksaveasfilename(
            title=self._t("save_cipher_title"),
            defaultextension=".txt",
            initialfile="encrypted_stx1.txt",
            filetypes=self._filetypes(),
        )
        if not path:
            return

        try:
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(self._t("saved_cipher").format(name=Path(path).name))
        except Exception as exc:
            messagebox.showerror(self._t("save_failed"), str(exc))

    def copy_text(self, widget: tk.Text, status_key: str) -> None:
        content = widget.get("1.0", "end-1c")
        if not content:
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self.status_var.set(self._t(status_key))

    def paste_ciphertext(self) -> None:
        try:
            content = self.clipboard_get().strip()
        except tk.TclError:
            content = ""

        if not content:
            return

        self.cipher_text.delete("1.0", tk.END)
        self.cipher_text.insert("1.0", content)
        self.cipher_text.focus_set()
        self.status_var.set(self._t("cipher_pasted"))

    def clear_all(self) -> None:
        self.plain_text.delete("1.0", tk.END)
        self.cipher_text.delete("1.0", tk.END)
        self.password_var.set("")
        self.status_var.set(self._t("ready"))
        self.password_entry.focus_set()


if __name__ == "__main__":
    app = VeilTextApp()
    app.mainloop()
