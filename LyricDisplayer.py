import time

import customtkinter as ctk

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")




class DisplayWindow(ctk.CTk):
    def __init__(self, font="Arial", size=60, color="#D886D2", opacity=0.8, position=(2, 1), alignment="e"):
        super().__init__()
        self.title("Display")
        self.geometry(f"640x360+{640*position[0]}+{360*position[1]}")
        self.resizable(False, False)
        self.invisible_color = self.DarkenHex(color)
        self.wm_attributes("-transparentcolor", self.invisible_color)
        self.configure(fg_color=self.invisible_color)
        self.wm_attributes("-alpha", opacity)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.lift()
        self.wm_frame()

        self.find_relx = {"w": 0.1, "center": 0.5, "e": 0.9}
        self.chosen_relx = self.find_relx[alignment]

        self.total_anim_frame = 160  # Number of animation frames
        self.animation_delay = 2  # Delay between frames in ms
        self.is_animating = False

        self.chosen_font = font
        self.chosen_size = size
        self.chosen_color = color
        self.chosen_opacity = opacity
        self.chosen_position = position
        self.chosen_alignment = alignment
        self.wrap_length = 576

        # Lyrics
        self.lyrics0 = ctk.CTkLabel(self, text="", font=("Arial", int(size)//1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics0.place(relx=self.chosen_relx, y=108, anchor=self.chosen_alignment)

        self.lyrics1 = ctk.CTkLabel(self, text="Loading", font=("Arial", int(size), "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics1.place(relx=self.chosen_relx, y=180, anchor=self.chosen_alignment)

        self.lyrics2 = ctk.CTkLabel(self, text="", font=("Arial", int(size)//1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics2.place(relx=self.chosen_relx, y=288, anchor=self.chosen_alignment)

        self.lyrics3 = ctk.CTkLabel(self, text="", font=("Arial", int(size)//5, "bold"), text_color=self.invisible_color, wraplength=self.wrap_length)
        self.lyrics3.place(relx=self.chosen_relx, y=324, anchor=self.chosen_alignment)

        # Preview
        self.preview_frame = ctk.CTkFrame(self, width=640, height=360, corner_radius=0, bg_color=self.DarkenHex(self.chosen_color,60))
        self.preview_frame.place(x=0, y=0)

        self.pr_lyric0 = ctk.CTkLabel(self.preview_frame, text="old lyrics here", font=("Arial", int(size) // 1.5, "bold"),
                                    text_color=self.chosen_color, wraplength=self.wrap_length)
        self.pr_lyric0.place(relx=self.chosen_relx, y=108, anchor=self.chosen_alignment)

        self.pr_lyric1 = ctk.CTkLabel(self.preview_frame, text="current lyrics here", font=("Arial", int(size), "bold"),
                                    text_color=self.chosen_color, wraplength=self.wrap_length)
        self.pr_lyric1.place(relx=self.chosen_relx, y=180, anchor=self.chosen_alignment)

        self.pr_lyric2 = ctk.CTkLabel(self.preview_frame, text="future lyrics here", font=("Arial", int(size) // 1.5, "bold"),
                                    text_color=self.chosen_color, wraplength=self.wrap_length)
        self.pr_lyric2.place(relx=self.chosen_relx, y=288, anchor=self.chosen_alignment)




        self.lyrics_arr = [self.lyrics0, self.lyrics1, self.lyrics2, self.lyrics3]

        self.start_pos = [108, 180, 288, 324]
        self.target_pos = [36, 108, 180, 288]
        self.start_size = [int(self.chosen_size)/1.5, int(self.chosen_size), int(self.chosen_size)/1.5, int(self.chosen_size)/3]
        self.target_size = [int(self.chosen_size)/3, int(self.chosen_size)/1.5, int(self.chosen_size), int(self.chosen_size)/1.5]

        self.current_lyrics_data = ["", "", "", ""]

        self.focus_set()

    def UpdateLyrics(self, lyrics_data):
        self.current_lyrics_data = lyrics_data.copy()

        # Update the text content of the labels
        for i, lyric in enumerate(lyrics_data):
            if i < len(self.lyrics_arr):
                self.lyrics_arr[i].configure(text=lyric)

        # Trigger animation
        self.Step()
    def UpdateSettings(self, font=None, size=None, color=None, opacity=None, position=None, alignment=None):

        if font is not None:
            self.chosen_font = font
        if size is not None:
            self.chosen_size = size
        if color is not None:
            self.chosen_color = color
            self.invisible_color = self.DarkenHex(color)
        if opacity is not None:
            self.chosen_opacity = opacity
            self.wm_attributes("-alpha", opacity)
        if position is not None:
            self.chosen_position = position
            self.geometry(f"640x360+{640 * position[0]}+{360 * position[1]}")
        if alignment is not None:
            self.chosen_alignment = alignment
            self.chosen_relx = self.find_relx[alignment]


        self.RefreshLyrics()

    def RefreshLyrics(self):
        size = int(self.chosen_size)

        # Update fonts and colors for all labels
        self.lyrics0.configure(font=(self.chosen_font, size // 1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics1.configure(font=(self.chosen_font, size, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics2.configure(font=(self.chosen_font, size // 1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.lyrics3.configure(font=(self.chosen_font, size // 5, "bold"), text_color=self.invisible_color, wraplength=self.wrap_length)

        self.preview_frame.configure(bg_color=self.DarkenHex(self.chosen_color, 60))

        self.pr_lyric0.configure(font=(self.chosen_font, size // 1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.pr_lyric1.configure(font=(self.chosen_font, size, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)
        self.pr_lyric2.configure(font=(self.chosen_font, size // 1.5, "bold"), text_color=self.chosen_color, wraplength=self.wrap_length)

        self.pr_lyric0.place(relx=self.chosen_relx, anchor=self.chosen_alignment)
        self.pr_lyric1.place(relx=self.chosen_relx, anchor=self.chosen_alignment)
        self.pr_lyric2.place(relx=self.chosen_relx, anchor=self.chosen_alignment)


        # Update size arrays
        self.start_size = [self.chosen_size / 1.5, self.chosen_size, self.chosen_size / 1.5, self.chosen_size / 3]
        self.target_size = [self.chosen_size / 3, self.chosen_size / 1.5, self.chosen_size, self.chosen_size / 1.5]

    # Functions
    def Step(self):
        if(self.is_animating): return
        else:
            self.is_animating = True
            self.current_frame = 0

            self.Animate()


    def Animate(self):

        # Check if the animation finished
        if self.current_frame >= self.total_anim_frame:
            self.is_animating = False

            temp = self.lyrics_arr.pop(0)
            self.lyrics_arr.append(temp)

            # Place labels at final positions
            for i, label in enumerate(self.lyrics_arr):
                label.place(relx=self.chosen_relx, y=self.start_pos[i], anchor=self.chosen_alignment)

            return

        # current step calculation and smoothing
        t = self.current_frame / (self.total_anim_frame - 1)
        t = 1 - (1 - t) ** 2

        # Change positions
        for i in range(len(self.start_pos)):
            start_pos = self.start_pos[i]
            target_pos = self.target_pos[i]
            current_pos = start_pos + (target_pos - start_pos) * t

            self.lyrics_arr[i].place(relx=self.chosen_relx, y=current_pos, anchor=self.chosen_alignment)

        # Change sizes
        for i in range(len(self.start_pos)):
            start_size = self.start_size[i]
            target_size = self.target_size[i]
            current_size = start_size + (target_size - start_size) * t

            self.lyrics_arr[i].configure(font=(self.chosen_font, current_size, "bold"))

        # Change colors
        fade_out_color = self.ChangeColor(self.chosen_color, self.invisible_color, t)
        fade_in_color = self.ChangeColor(self.invisible_color, self.chosen_color, t)

        self.lyrics_arr[0].configure(text_color=fade_out_color)
        self.lyrics_arr[3].configure(text_color=fade_in_color)


        # Next frame plan
        self.current_frame += 1
        self.after(self.animation_delay, self.Animate)

    def ChangeColor(self, start_color, end_color, t):

        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)

        # Interpolate each RGB component
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t)

        return self.rgb_to_hex((r, g, b))

    def hex_to_rgb(self, hex_color):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def DarkenHex(self, hex_color, factor=0.5):

        rgb = self.hex_to_rgb(hex_color)

        # Darken each component
        darkened_rgb = tuple(
            max(0, min(255, int(component * factor)))
            for component in rgb
        )

        return self.rgb_to_hex(darkened_rgb)

    def OpenPreview(self):
        self.preview_frame.place(x=0)


    def ClosePreview(self):
        time.sleep(2)
        self.preview_frame.place(x=5000)