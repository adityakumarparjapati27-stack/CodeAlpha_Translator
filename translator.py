import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import subprocess

# LANGUAGES  (name shown in dropdown : code used by API)
languages = {
    "English":    "en",
    "Hindi":      "hi",
    "French":     "fr",
    "Spanish":    "es",
    "German":     "de",
    "Chinese":    "zh-CN",
    "Arabic":     "ar",
    "Japanese":   "ja",
    "Korean":     "ko",
    "Portuguese": "pt",
    "Russian":    "ru",
    "Italian":    "it",
    "Turkish":    "tr",
    "Dutch":      "nl",
    "Bengali":    "bn",
}

lang_names = list(languages.keys())


def translate():
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Empty", "Please enter some text to translate.")
        return

    src  = languages[src_var.get()]
    tgt  = languages[tgt_var.get()]

    if src == tgt:
        messagebox.showinfo("Same language", "Source and target language are the same.")
        return

    status_label.config(text="Translating...")
    translate_btn.config(state=tk.DISABLED)

    def run():
        try:
            result = GoogleTranslator(source=src, target=tgt).translate(text)
            output_box.config(state=tk.NORMAL)
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, result)
            output_box.config(state=tk.DISABLED)
            status_label.config(text="Done.")
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed:\n{e}")
            status_label.config(text="")
        finally:
            translate_btn.config(state=tk.NORMAL)

    threading.Thread(target=run, daemon=True).start()


def copy_text():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        return
    window.clipboard_clear()
    window.clipboard_append(text)
    status_label.config(text="Copied!")


def speak():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Empty", "Nothing to speak yet. Translate something first.")
        return

    tgt = languages[tgt_var.get()]

    def run():
        try:
            tts = gTTS(text=text, lang=tgt)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp.name)
            tmp.close()
            # play on linux / mac / windows
            if os.name == "nt":
                os.startfile(tmp.name)
            elif os.uname().sysname == "Darwin":
                subprocess.run(["afplay", tmp.name])
            else:
                subprocess.run(["mpg123", tmp.name], stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Error", f"Text-to-speech failed:\n{e}")

    threading.Thread(target=run, daemon=True).start()


def swap():
    s = src_var.get()
    t = tgt_var.get()
    src_var.set(t)
    tgt_var.set(s)


# UI
window = tk.Tk()
window.title("Language Translator")
window.geometry("680x560")
window.resizable(False, False)
window.configure(bg="#f5f5f5")

BLUE  = "#1a73e8"
WHITE = "#ffffff"
GREY  = "#f5f5f5"
DARK  = "#333333"
FONT  = ("Helvetica", 11)

tk.Label(window, text="Language Translation Tool",
         font=("Helvetica", 16, "bold"), bg=GREY, fg=DARK).pack(pady=(18, 10))


lang_frame = tk.Frame(window, bg=GREY)
lang_frame.pack(pady=(0, 8))

tk.Label(lang_frame, text="From:", font=FONT, bg=GREY, fg=DARK).grid(row=0, column=0, padx=(0,6))
src_var = tk.StringVar(value="English")
ttk.Combobox(lang_frame, textvariable=src_var, values=lang_names,
             state="readonly", width=16, font=FONT).grid(row=0, column=1, padx=(0,10))

tk.Button(lang_frame, text="⇄", font=("Helvetica", 13, "bold"),
          bg=GREY, fg=BLUE, relief=tk.FLAT, cursor="hand2",
          command=swap).grid(row=0, column=2, padx=8)

tk.Label(lang_frame, text="To:", font=FONT, bg=GREY, fg=DARK).grid(row=0, column=3, padx=(10,6))
tgt_var = tk.StringVar(value="Hindi")
ttk.Combobox(lang_frame, textvariable=tgt_var, values=lang_names,
             state="readonly", width=16, font=FONT).grid(row=0, column=4)

tk.Label(window, text="Enter text:", font=FONT, bg=GREY, fg=DARK, anchor="w").pack(padx=30, anchor="w")
input_box = tk.Text(window, height=7, width=76, font=FONT,
                    bg=WHITE, fg=DARK, relief=tk.FLAT,
                    highlightthickness=1, highlightbackground="#ccc",
                    highlightcolor=BLUE, padx=8, pady=8, wrap=tk.WORD)
input_box.pack(padx=30, pady=(4, 10))

translate_btn = tk.Button(window, text="Translate", font=("Helvetica", 12, "bold"),
                          bg=BLUE, fg=WHITE, relief=tk.FLAT,
                          activebackground="#1558b0", activeforeground=WHITE,
                          padx=24, pady=8, cursor="hand2", command=translate)
translate_btn.pack()

tk.Label(window, text="Translation:", font=FONT, bg=GREY, fg=DARK, anchor="w").pack(padx=30, pady=(12,0), anchor="w")
output_box = tk.Text(window, height=7, width=76, font=FONT,
                     bg="#eaf3fb", fg=DARK, relief=tk.FLAT,
                     highlightthickness=1, highlightbackground="#ccc",
                     padx=8, pady=8, wrap=tk.WORD, state=tk.DISABLED)
output_box.pack(padx=30, pady=(4, 8))

btn_frame = tk.Frame(window, bg=GREY)
btn_frame.pack()

tk.Button(btn_frame, text="📋  Copy", font=FONT,
          bg=WHITE, fg=DARK, relief=tk.FLAT,
          highlightthickness=1, highlightbackground="#ccc",
          padx=14, pady=6, cursor="hand2",
          command=copy_text).grid(row=0, column=0, padx=8)

tk.Button(btn_frame, text="🔊  Speak", font=FONT,
          bg=WHITE, fg=DARK, relief=tk.FLAT,
          highlightthickness=1, highlightbackground="#ccc",
          padx=14, pady=6, cursor="hand2",
          command=speak).grid(row=0, column=1, padx=8)

status_label = tk.Label(window, text="", font=("Helvetica", 10),
                        bg=GREY, fg="#888")
status_label.pack(pady=(8, 0))

window.mainloop()
