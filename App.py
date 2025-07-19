import tkinter
from tkinter import colorchooser
import customtkinter as ctk
from PIL import Image
from LyricDisplayer import DisplayWindow
from LyricFetcher import LyricFetcher
import threading
import queue

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Show My Lyrics")
        self.geometry("600x800")
        self.configure(fg_color="#444651")
        self.resizable(False, False)

        # Customization Data
        self.chosen_font = "Arial"
        self.chosen_size = 25
        self.chosen_color = "#c0c0c0"
        self.chosen_opacity = 1.0
        self.chosen_position = (2, 1)
        self.chosen_alignment = "e"


        # Create a queue for thread-safe communication
        self.lyrics_queue = queue.Queue()

        # App Layout
        self.Display = DisplaySection(self, self)
        self.Display.pack(fill="x", pady=(39, 0))

        self.Font = FontSection(self, self)
        self.Font.pack(fill="x", pady=(35, 0))

        self.Size = SizeSection(self, self)
        self.Size.pack(fill="x", pady=(35, 0))

        self.Color = ColorSection(self, self)
        self.Color.pack(fill="x", pady=(35, 0))

        self.Preview = PreviewSection(self, self)
        self.Preview.pack(fill="x", pady=35)

        # Display window
        try:
            self.display_window = DisplayWindow(
                font=self.chosen_font,
                size=self.chosen_size,
                color=self.chosen_color,
                opacity=self.chosen_opacity,
                position=self.chosen_position
            )
            self.display_window.deiconify()
            print(f"Display window created at position {self.chosen_position}")
        except Exception as e:
            print(f"Error creating display window: {e}")

        # Start window checker
        self.window_state = 1
        self.CheckWindowState()

        # Start the lyric fetcher
        self.lyric_fetcher = LyricFetcher(self.on_lyrics_change)
        self.fetcher_thread = threading.Thread(target=self.lyric_fetcher.Run, daemon=True)
        self.fetcher_thread.start()

        # Start processing the queue
        self.process_lyrics_queue()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Functions
    def on_closing(self):
        if hasattr(self, 'lyric_fetcher'):
            self.lyric_fetcher.Stop()
        if hasattr(self, 'display_window'):
            self.display_window.destroy()
        self.destroy()

    def on_lyrics_change(self, lyrics_data):
        # Put the lyrics data in the queue instead of updating directly
        self.lyrics_queue.put(lyrics_data)

    def process_lyrics_queue(self):
        # Process any pending lyrics updates from the queue
        try:
            while not self.lyrics_queue.empty():
                lyrics_data = self.lyrics_queue.get_nowait()
                if hasattr(self, 'display_window') and lyrics_data:
                    # Update the display window with new lyrics
                    self.display_window.UpdateLyrics(lyrics_data)
        except queue.Empty:
            pass

        # Schedule the next check
        self.after(50, self.process_lyrics_queue)


    def CheckWindowState(self):
        is_viewable = self.winfo_viewable()

        if is_viewable == 0 and self.window_state != 0:
            self.display_window.ClosePreview()
            self.window_state = 0

        elif is_viewable == 1 and self.window_state != 1:
            self.display_window.OpenPreview()
            self.window_state = 1


        self.after(1000, self.CheckWindowState)

    def UpdatePreview(self):

        # Update the display window with new settings
        if hasattr(self, 'display_window'):
            self.display_window.UpdateSettings(
                font=self.chosen_font,
                size=self.chosen_size,
                color=self.chosen_color,
                opacity=self.chosen_opacity,
                position=self.chosen_position,
                alignment=self.chosen_alignment
            )


class DisplaySection(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, width=520, height=225, fg_color="#444651")
        self.pack_propagate(False)
        self.app = app_ref

        # Background image
        self.bg_image = ctk.CTkImage(Image.open("images/Position.png"), size=(520, 225))
        self.image_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.image_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Title
        self.title = ctk.CTkLabel(self, text="DISPLAY", font=("Arial", 25, "bold"), text_color="#D886D2")
        self.title.place(x=40, y=10)

        # Description
        self.description = ctk.CTkLabel(self, text="Lyrics\nposition\nand their\nalignment:", font=("Arial", 20, "bold"),
                                        text_color="#AF4FA9", fg_color="#D886D2")
        self.description.place(x=60, y=70)

        # Position Selection
        self.pos_button_frame = ctk.CTkFrame(self, fg_color="#D886D2")
        self.pos_button_frame.place(relx=0.6, rely=0.5, anchor="center")

        btn_tl = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((0, 0)), width=100, height=60,
                               text="Top Left", font=("Arial", 15, "bold"), text_color="#D886D2", fg_color="#AF4FA9",
                               hover_color="#832F7E")
        btn_tl.grid(row=0, column=0, padx=5, pady=5)

        btn_tc = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((1, 0)), width=100, height=60,
                               text="Top\nCenter", font=("Arial", 15, "bold"), text_color="#D886D2", fg_color="#AF4FA9",
                               hover_color="#832F7E")
        btn_tc.grid(row=0, column=1, padx=5, pady=5)

        btn_tr = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((2, 0)), width=100, height=60,
                               text="Top\nRight", font=("Arial", 15, "bold"), text_color="#D886D2", fg_color="#AF4FA9",
                               hover_color="#832F7E")
        btn_tr.grid(row=0, column=2, padx=5, pady=5)

        btn_ml = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((0, 1)), width=100, height=60,
                               text="Middle\nLeft", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_ml.grid(row=1, column=0, padx=5, pady=5)

        btn_mc = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((1, 1)), width=100, height=60,
                               text="Middle\nCenter", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_mc.grid(row=1, column=1, padx=5, pady=5)

        btn_mr = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((2, 1)), width=100, height=60,
                               text="Middle\nRight", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_mr.grid(row=1, column=2, padx=5, pady=5)

        btn_bl = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((0, 2)), width=100, height=60,
                               text="Bottom\nLeft", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_bl.grid(row=2, column=0, padx=5, pady=5)

        btn_bc = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((1, 2)), width=100, height=60,
                               text="Bottom\nCenter", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_bc.grid(row=2, column=1, padx=5, pady=5)

        btn_br = ctk.CTkButton(self.pos_button_frame, command=lambda: self.UpdatePosition((2, 2)), width=100, height=60,
                               text="Bottom\nRight", font=("Arial", 15, "bold"), text_color="#D886D2",
                               fg_color="#AF4FA9", hover_color="#832F7E")
        btn_br.grid(row=2, column=2, padx=5, pady=5)

        self.pos_buttons = [btn_tl, btn_tc, btn_tr, btn_ml, btn_mc, btn_mr, btn_bl, btn_bc, btn_br]

        self.pos_buttons[5].configure(fg_color="#832F7E") # Default


        # Alignment Selection
        self.al_button_frame = ctk.CTkFrame(self, fg_color="#D886D2")
        self.al_button_frame.place(relx=0.18, rely=0.895, anchor="center")

        btn_west = ctk.CTkButton(self.al_button_frame, command=lambda: self.UpdateAlignment(0), width=30, height=20,
                                 text="<", font=("Arial", 15, "bold"), text_color="#D886D2",
                                 fg_color="#AF4FA9", hover_color="#832F7E")
        btn_west.grid(row=0, column=0, padx=5, pady=5)

        btn_center = ctk.CTkButton(self.al_button_frame, command=lambda: self.UpdateAlignment(1), width=30, height=20,
                                 text="|", font=("Arial", 15, "bold"), text_color="#D886D2",
                                 fg_color="#AF4FA9", hover_color="#832F7E")
        btn_center.grid(row=0, column=1, padx=5, pady=5)

        btn_east = ctk.CTkButton(self.al_button_frame, command=lambda: self.UpdateAlignment(2), width=30, height=20,
                                 text=">", font=("Arial", 15, "bold"), text_color="#D886D2",
                                 fg_color="#AF4FA9", hover_color="#832F7E")
        btn_east.grid(row=0, column=2, padx=5, pady=5)

        self.al_buttons = [btn_west, btn_center, btn_east]

        self.al_buttons[2].configure(fg_color="#832F7E") # Default



    def UpdatePosition(self, ind):
        self.pos_buttons[self.app.chosen_position[0] + self.app.chosen_position[1] * 3].configure(fg_color="#AF4FA9")
        self.pos_buttons[ind[0] + ind[1] * 3].configure(fg_color="#832F7E")
        self.app.chosen_position = ind
        self.app.UpdatePreview()

    def UpdateAlignment(self, ind):
        if(self.app.chosen_alignment == "w"): old_ind = 0
        elif(self.app.chosen_alignment == "center"): old_ind = 1
        else: old_ind = 2

        self.al_buttons[old_ind].configure(fg_color="#AF4FA9")
        self.al_buttons[ind].configure(fg_color="#832F7E")

        if(ind == 0): self.app.chosen_alignment = "w"
        if(ind == 1): self.app.chosen_alignment = "center"
        if(ind == 2): self.app.chosen_alignment = "e"

        self.app.UpdatePreview()


class FontSection(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, width=520, height=80, fg_color="#444651")
        self.pack_propagate(False)
        self.app = app_ref

        # Background image
        self.bg_image = ctk.CTkImage(Image.open("images/Font.png"), size=(520, 80))
        self.image_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.image_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Title
        self.title = ctk.CTkLabel(self, text="FONT", font=("Arial", 20, "bold"), text_color="#D886D2")
        self.title.place(x=40, y=5)

        # Description
        self.description = ctk.CTkLabel(self, text="Font of the\nlyrics:", font=("Arial", 20, "bold"),
                                        text_color="#AF4FA9", fg_color="#D886D2")
        self.description.place(x=120, y=15)

        # Font Selection
        font_choices = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", "Verdana"]
        self.font_dropdown = ctk.CTkOptionMenu(
            self,
            values=font_choices,
            command=self.FontSelected,
            width=180,
            height=30,
            font=("Arial", 14),
            fg_color="#AF4FA9",
            bg_color="#D886D2",
            button_color="#832F7E",
            button_hover_color="#6b2563",
            text_color="#D886D2"
        )
        self.font_dropdown.set("Arial")  # default selection
        self.font_dropdown.place(x=300, y=25)

    def FontSelected(self, choice):
        print(f"Selected font: {choice}")
        self.app.chosen_font = choice
        self.app.UpdatePreview()


class SizeSection(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, width=520, height=80, fg_color="#444651")
        self.pack_propagate(False)
        self.app = app_ref

        # Background image
        self.bg_image = ctk.CTkImage(Image.open("images/Size.png"), size=(520, 80))
        self.image_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.image_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Title
        self.title = ctk.CTkLabel(self, text="SIZE", font=("Arial", 23, "bold"), text_color="#D886D2")
        self.title.place(x=40, y=5)

        # Description
        self.description = ctk.CTkLabel(self, text="Size of the\nlyrics:", font=("Arial", 20, "bold"),
                                        text_color="#AF4FA9", fg_color="#D886D2")
        self.description.place(x=110, y=15)

        # Size selection
        size_choices = ["14", "17", "20", "25", "30", "36", "48", "60"]
        self.size_dropdown = ctk.CTkOptionMenu(
            self,
            values=size_choices,
            command=self.SizeSelected,
            width=180,
            height=30,
            font=("Arial", 14),
            fg_color="#AF4FA9",
            bg_color="#D886D2",
            button_color="#832F7E",
            button_hover_color="#6b2563",
            text_color="#D886D2"
        )
        self.size_dropdown.set("25")  # default selection
        self.size_dropdown.place(x=300, y=25)

    def SizeSelected(self, choice):
        print(f"Selected size: {choice}")
        self.app.chosen_size = int(choice)
        self.app.UpdatePreview()


class ColorSection(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, width=520, height=80, fg_color="#444651")
        self.pack_propagate(False)
        self.app = app_ref

        # Background image
        self.bg_image = ctk.CTkImage(Image.open("images/Color.png"), size=(520, 80))
        self.image_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.image_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Title
        self.title = ctk.CTkLabel(self, text="COLOR", font=("Arial", 20, "bold"), text_color="#D886D2")
        self.title.place(x=40, y=5)

        # Description
        self.description = ctk.CTkLabel(self, text="Color and opacity\nof the lyrics:", font=("Arial", 20, "bold"),
                                        text_color="#AF4FA9", fg_color="#D886D2")
        self.description.place(x=140, y=15)

        # Color Selection
        self.color_button = ctk.CTkButton(
            self,
            text="Pick Color",
            width=100,
            height=30,
            font=("Arial", 14),
            text_color="#D886D2",
            fg_color="#AF4FA9",
            bg_color="#D886D2",
            hover_color="#832F7E",
            command=self.ColorPicker
        )
        self.color_button.place(x=340, y=25)

        # Opacity Selection
        self.opacity_entry = ctk.CTkEntry(self, width=50, font=("Arial", 14), text_color="#D886D2", fg_color="#AF4FA9",
                                          bg_color="#D886D2", border_color="#AF4FA9")
        self.opacity_entry.place(x=450, y=26)
        self.opacity_entry.insert(0, "100")
        self.opacity_entry.bind("<KeyRelease>", self.OpacitySelected)

    def ColorPicker(self):
        color_code = tkinter.colorchooser.askcolor(title="Choose Color")[1]
        if color_code:
            print(f"Selected color: {color_code}")
            self.app.chosen_color = color_code
            self.app.UpdatePreview()

    def OpacitySelected(self, event=None):
        val = self.opacity_entry.get()
        try:
            opacity = max(0, min(100, int(val)))
            self.app.chosen_opacity = opacity / 100.0
            self.app.UpdatePreview()
        except ValueError:
            pass


class PreviewSection(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, width=520, height=120, fg_color="#444651")
        self.pack_propagate(False)
        self.app = app_ref

        # Background image
        self.bg_image = ctk.CTkImage(Image.open("images/Preview.png"), size=(520, 120))
        self.image_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.image_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Title
        self.title = ctk.CTkLabel(self, text="PREVIEW", font=("Arial", 23, "bold"), text_color="#D886D2")
        self.title.place(x=40, y=5)

        # Preview Lyrics
        self.preview_lyric = ctk.CTkLabel(self, text="Minimize this window to get your lyrics",
                                          font=("Arial", 25, "bold"),
                                          text_color="#AF4FA9", fg_color="#D886D2", wraplength=540)
        self.preview_lyric.place(relx=0.5, rely=0.6, anchor="center")


if __name__ == "__main__":
    App().mainloop()