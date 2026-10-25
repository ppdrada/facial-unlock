import os
import sys
import tkinter as tk

from auth import verify_owner
from face_engine import FaceEngine, resource_path
from register_face import register
from unlock_face import open_calculator, unlock
from window import ICON_ICO, WINDOW_TITLE, set_app_icon

ICON_PNG = resource_path(os.path.join("assets", "icon", "icon.png"))

BG = "#1C1C1E"
CARD = "#2C2C2E"
TEXT = "#F2F2F2"
MUTED = "#8E8E93"
GREEN = "#30D158"
ORANGE = "#FF9F0A"
RED = "#FF453A"
BUTTON = "#3A3A3C"
BUTTON_HOVER = "#48484A"
PRIMARY = "#0A84FF"
PRIMARY_HOVER = "#409CFF"


class HomeScreen:
    """Tela inicial: mostra se há rosto cadastrado e as opções."""

    def __init__(self):
        self.engine = FaceEngine()

        # o Tk precisa ser criado antes de mexer no ícone do Dock (macOS)
        self.root = tk.Tk()
        set_app_icon()
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.icon = tk.PhotoImage(file=ICON_PNG)
        if sys.platform == "win32":
            self.root.iconbitmap(ICON_ICO)
        else:
            self.root.iconphoto(True, self.icon)

        tk.Label(self.root, image=self.icon, bg=BG).pack(pady=(36, 12))
        tk.Label(self.root, text="Facial Unlock", bg=BG, fg=TEXT, font=("Helvetica", 24, "bold")).pack()

        self.status = tk.Label(self.root, bg=BG, font=("Helvetica", 10))
        self.status.pack(pady=(14, 4))
        self.message = tk.Label(self.root, bg=BG, fg=MUTED, font=("Helvetica", 10))
        self.message.pack(pady=(0, 18))

        self.buttons = tk.Frame(self.root, bg=BG)
        self.buttons.pack(padx=48, pady=(0, 40))

        self.refresh()
        self.center()

    # ---------- tela ----------

    def center(self):
        self.root.update_idletasks()
        w, h = 360, self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def button(self, text, command, primary=False):
        # Label no lugar de Button: no macOS o Button ignora as cores
        bg, hover = (PRIMARY, PRIMARY_HOVER) if primary else (BUTTON, BUTTON_HOVER)
        b = tk.Label(self.buttons, text=text, bg=bg, fg=TEXT, font=("Helvetica", 12),
                     width=22, pady=8, cursor="hand2")
        b.bind("<Button-1>", lambda e: command())
        b.bind("<Enter>", lambda e: b.configure(bg=hover))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        b.pack(pady=5)

    def link(self, text, command):
        # texto clicável discreto, estilo "Esqueceu a senha?"
        l = tk.Label(self.buttons, text=text, bg=BG, fg=MUTED, font=("Helvetica", 11),
                     cursor="hand2")
        l.bind("<Button-1>", lambda e: command())
        l.bind("<Enter>", lambda e: l.configure(fg=TEXT))
        l.bind("<Leave>", lambda e: l.configure(fg=MUTED))
        l.pack(pady=(14, 0))

    def refresh(self):
        for child in self.buttons.winfo_children():
            child.destroy()

        total = len(self.engine.known_faces)
        if total:
            self.status.configure(text=f"●  Face registered ({total} samples)", fg=GREEN)
            self.button("Test recognition", self.on_test, primary=True)
            self.button("Add samples", self.on_add)
            self.link("Register a new face", self.on_new)
        else:
            self.status.configure(text="●  No face registered", fg=ORANGE)
            self.button("Register face", self.on_new, primary=True)

    def say(self, text, color=MUTED):
        self.message.configure(text=text, fg=color)

    def run_camera(self, action):
        # esconde a tela inicial enquanto a janela da câmera está aberta
        self.root.withdraw()
        self.root.update()
        try:
            return action()
        except RuntimeError as e:
            self.say(str(e), RED)
            return None
        finally:
            self.root.deiconify()
            self.root.lift()
            self.refresh()

    # ---------- ações ----------

    def on_test(self):
        result = self.run_camera(lambda: unlock(self.engine))
        if result:
            self.say("Recognized! Opening the calculator...", GREEN)
            open_calculator()
        elif result is False:
            self.say("Test cancelled.")

    def on_add(self):
        self.record(reset=False, reason="add samples to your face")

    def on_new(self):
        self.record(reset=True, reason="register a new face")

    def record(self, reset, reason):
        # por segurança, só o dono do computador pode cadastrar rostos
        if not verify_owner(f"Facial Unlock needs your password to {reason}."):
            self.say("Password not confirmed.", RED)
            return
        result = self.run_camera(lambda: register(self.engine, reset=reset))
        if result:
            self.say("Face saved!", GREEN)
        elif result is False:
            self.say("Registration cancelled.")

    def run(self):
        self.root.mainloop()
