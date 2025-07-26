import sys
import threading
import queue
import json
import os

from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QColorDialog, QPushButton, QComboBox, QSpinBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QByteArray
from PyQt6.QtGui import QFont, QColor, QPainter, QIcon

from LyricDisplayer import DisplayWindow
from TokenManager import TokenManager
from LyricFetcher import LyricFetcher


class ThemeButton(QPushButton):
    def __init__(self, theme_name, bg_color, top_color, highlight_color, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.bg_color = bg_color
        self.top_color = top_color
        self.highlight_color = highlight_color

        # Set button size
        self.setFixedSize(30, 60)
        self.setup_style()

    def setup_style(self, clicked=False):
        if(not clicked):
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.bg_color};
                    border: 3px solid {self.parent().main.menu_bg_color_top};
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.bg_color};
                    border: 3px solid {self.parent().main.menu_highlight_color};
                    border-radius: 8px;
                }}
            """)



    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        button_rect = self.rect()
        width = int(button_rect.width()*0.8)
        height = int(button_rect.height()*0.5)
        x = (button_rect.width() - width) // 2
        y = (button_rect.height()) // 2

        painter.setBrush(QColor(self.top_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(x, y-10, width, height, 5, 5)

        height = int(button_rect.height() * 0.4)
        y = (button_rect.height() + width) // 2
        painter.setBrush(QColor(self.highlight_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(x, y-6, width, height, 5, 5)


        painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Show My Lyrics")
        self.setFixedSize(600, 800)

        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "images/icon.png")
        else: icon_path = os.path.join(os.path.abspath("."), "images/icon.png")
        app.setWindowIcon(QIcon(icon_path))

        self.settings_file = "settings.json"

        # Lyrics Data
        self.chosen_font = "Arial"
        self.chosen_bold = False
        self.chosen_italic = False
        self.chosen_underline = False
        self.chosen_size = 40
        self.chosen_color = "#FFFFFF"
        self.chosen_opacity = 80
        self.chosen_position = (2, 1)
        self.chosen_alignment = 2
        self.chosen_theme_ind = 0

        # Customization Menu Data
        self.theme_labels = ["red", "orange", "green", "turquoise", "blue", "purple"]
        self.menu_bg_color_bottom = "#34282C"
        self.menu_bg_color = "#EFE1E6"
        self.menu_bg_color_top = "#9A6A79"
        self.menu_text_color = "#5E404A"
        self.menu_highlight_color = "#B296E3"

        self.setStyleSheet(f"background-color: {self.menu_bg_color_bottom};")

        # Set the token manager
        self.token_manager = TokenManager(client_id="7314df2b002f4442a5f07737b77cfab3", on_token_refresh=self.RefreshSpotifyClient)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout with proper spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Create the sections
        self.display_section = DisplaySection(self)
        self.font_section = FontSection(self)
        self.color_section = ColorSection(self)
        self.theme_section = ThemeSection(self)
        self.details = DetailSection(self)
        self.login = LoginSection(self)

        # Add sections to main layout
        main_layout.addWidget(self.display_section)
        main_layout.addWidget(self.font_section)
        main_layout.addWidget(self.color_section)
        main_layout.addWidget(self.theme_section)

        # Instantiate necessary things
        self.display_window = DisplayWindow()
        self.lyrics_queue = queue.Queue()

        # Start LyricFetcher
        self.lyric_fetcher = LyricFetcher(self.OnLyricsChange)
        self.fetcher_thread = threading.Thread(target=self.lyric_fetcher.Run, daemon=True)
        self.fetcher_thread.start()

        # Load last settings
        self.LoadSettings()
        self.UpdateDisplaySettings()
        self.ChangeMenuTheme(self.theme_labels[self.chosen_theme_ind])

        # Start processing the queue
        self.ProcessLyricsQueue()
        self.CheckLoginRemoval()


    # Function to change menu theme according to a certain color
    def ChangeMenuTheme(self, color):
        if color == "red":
            self.menu_bg_color_bottom = "#34282C"
            self.menu_bg_color = "#EFE1E6"
            self.menu_bg_color_top = "#9A6A79"
            self.menu_text_color = "#5E404A"
            self.menu_highlight_color = "#B296E3"

        elif color == "orange":
            self.menu_bg_color_bottom = "#4B392A"
            self.menu_bg_color = "#F0E7E0"
            self.menu_bg_color_top = "#9F8065"
            self.menu_text_color = "#614D3D"
            self.menu_highlight_color = "#E088A4"

        elif color == "green":
            self.menu_bg_color_bottom = "#353928"
            self.menu_bg_color = "#E4E4E2"
            self.menu_bg_color_top = "#808377"
            self.menu_text_color = "#4C4E46"
            self.menu_highlight_color = "#DA955B"

        elif color == "turquoise":
            self.menu_bg_color_bottom = "#223F3A"
            self.menu_bg_color = "#E1EAE9"
            self.menu_bg_color_top = "#748B87"
            self.menu_text_color = "#465351"
            self.menu_highlight_color = "#9EB15D"

        elif color == "blue":
            self.menu_bg_color_bottom = "#2F4351"
            self.menu_bg_color = "#E9F1F6"
            self.menu_bg_color_top = "#6392B0"
            self.menu_text_color = "#3A5D73"
            self.menu_highlight_color = "#42BEA9"

        elif color == "purple":
            self.menu_bg_color_bottom = "#4B4653"
            self.menu_bg_color = "#EEEAF6"
            self.menu_bg_color_top = "#8169AB"
            self.menu_text_color = "#503E6F"
            self.menu_highlight_color = "#5FB0E6"

        self.ApplyMenuTheme()

    # Function to apply the color change to all components
    def ApplyMenuTheme(self):
        self.setStyleSheet(f"background-color: {self.menu_bg_color_bottom};")

        self.display_section.ChangeTheme()
        self.font_section.ChangeTheme()
        self.color_section.ChangeTheme()
        self.theme_section.ChangeTheme()
        self.details.ChangeTheme()

    # Function to apply lyrics customization to our display window
    def UpdateDisplaySettings(self):
        if hasattr(self, "display_window"):
            self.display_window.UpdateCustomization(
                font=self.chosen_font,
                size=self.chosen_size,
                color=self.chosen_color,
                opacity=self.chosen_opacity,
                position=self.chosen_position,
                alignment=self.chosen_alignment,
                bold=self.chosen_bold,
                italic=self.chosen_italic,
                underline=self.chosen_underline
            )

    # Function to get lyrics from our queue
    def ProcessLyricsQueue(self):
        try:
            while not self.lyrics_queue.empty():
                lyrics_data = self.lyrics_queue.get_nowait()
                self.display_window.UpdateLyrics(lyrics_data)

        except queue.Empty:
            pass

        QTimer.singleShot(250, self.ProcessLyricsQueue)

    # Function to put lyrics into the queue
    def OnLyricsChange(self, lyrics_data):
        self.lyrics_queue.put(lyrics_data)

    # Function that works when we close the main window
    def closeEvent(self, event):
        if hasattr(self, 'lyric_fetcher'):
            self.lyric_fetcher.Stop()
        if hasattr(self, 'display_window'):
            self.display_window.close()
        event.accept()

    # Function connected to the login button if the user is not authenticated yet
    def Login(self):
        self.token_manager.start_server()
        self.CheckLoginRemoval()

    # Function to check if user logged in, to remove login block
    def CheckLoginRemoval(self):
        if self.token_manager.is_session_valid():
            self.login.hide()
            self.display_window.show()
            self.RefreshSpotifyClient()
            return
        else:
            QTimer.singleShot(1000, self.CheckLoginRemoval)

    # Function to refresh spotify client after changing tokens
    def RefreshSpotifyClient(self):
        sp = self.token_manager.create_spotify_client()
        self.lyric_fetcher.sp = sp

    # Function to save customization settings
    def SaveSettings(self):
        data = {
            "chosen_font": self.chosen_font,
            "chosen_bold": self.chosen_bold,
            "chosen_italic": self.chosen_italic,
            "chosen_underline": self.chosen_underline,
            "chosen_size": self.chosen_size,
            "chosen_color": self.chosen_color,
            "chosen_opacity": self.chosen_opacity,
            "chosen_position": self.chosen_position,
            "chosen_alignment": self.chosen_alignment,
            "chosen_theme_ind": self.chosen_theme_ind
        }

        with open(self.settings_file, "w") as f:
            json.dump(data, f)

    # Function to load customization settings
    def LoadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)

                    self.chosen_font = data.get("chosen_font", "Arial")
                    self.chosen_bold = data.get("chosen_bold", False)
                    self.chosen_italic = data.get("chosen_italic", False)
                    self.chosen_underline = data.get("chosen_underline", False)
                    self.chosen_size = data.get("chosen_size", 40)
                    self.chosen_color = data.get("chosen_color", "#FFFFFF")
                    self.chosen_opacity = data.get("chosen_opacity", 80)
                    self.chosen_position = tuple(data.get("chosen_position", (1, 1)))
                    self.chosen_alignment = data.get("chosen_alignment", 2)
                    self.chosen_theme_ind = data.get("chosen_theme_ind", 0)

            except Exception as e:
                print(f"[MainWindow] Failed to load settings: {e}")


class DisplaySection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.setFixedSize(520, 225)
        self.main = main

        # Background
        self.bottom_bg_rect = QFrame(self)
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.bottom_bg_rect.setGeometry(0, 0, 520, 225)

        # Title
        self.title_shadow = QLabel("DISPLAY", self)
        self.title_shadow.setFont(QFont("Arial", 25, QFont.Weight.Bold))
        self.title_shadow.setStyleSheet(f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title_shadow.setGeometry(0, 0, 150, 40)

        self.title = QLabel("DISPLAY", self)
        self.title.setFont(QFont("Arial", 25, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.title.setGeometry(0, -4, 150, 40)

        # Description
        self.description = QLabel("Position of lyrics and their alignment:", self)
        self.description.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.description.setStyleSheet(f"color: {self.main.menu_text_color}; background-color: transparent; padding: 10px;")
        self.description.setGeometry(150, 0, 370, 45)

        # Position Buttons
        self.pos_btn_tl = QPushButton("Top\nLeft", self)
        self.pos_btn_tc = QPushButton("Top\nCenter", self)
        self.pos_btn_tr = QPushButton("Top\nRight", self)
        self.pos_btn_ml = QPushButton("Middle\nLeft", self)
        self.pos_btn_mc = QPushButton("Middle\nCenter", self)
        self.pos_btn_mr = QPushButton("Middle\nRight", self)
        self.pos_btn_bl = QPushButton("Bottom\nLeft", self)
        self.pos_btn_bc = QPushButton("Bottom\nCenter", self)
        self.pos_btn_br = QPushButton("Bottom\nRight", self)

        self.pos_buttons = [self.pos_btn_tl, self.pos_btn_tc, self.pos_btn_tr, self.pos_btn_ml, self.pos_btn_mc, self.pos_btn_mr, self.pos_btn_bl,
                            self.pos_btn_bc, self.pos_btn_br]


        for ind, pos_btn in enumerate(self.pos_buttons):
            pos_btn.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: {self.main.menu_bg_color_top};
                                            color: {self.main.menu_text_color};
                                            border: none;
                                            border-radius: 5;
                                            font: bold 14px Arial;
                                        }}
                                        QPushButton:hover {{                                                       
                                            background-color: {self.main.menu_highlight_color};
                                            color: {self.main.menu_bg_color};
                                        }}
                                    """)

            row = ind // 3
            col = ind % 3

            pos_btn.setGeometry(230 + col * 75, 75 + row * 45, 70, 40)
            pos_btn.clicked.connect(lambda checked, idx=ind: self.PosButtonPressed(idx))

        self.pos_buttons[self.main.chosen_position[0] + 3*self.main.chosen_position[1]].setStyleSheet(f"background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-radius: 5; font: bold 14px Arial;")



        # Alignment Buttons
        self.w_shadow = QFrame(self)
        self.c_shadow = QFrame(self)
        self.e_shadow = QFrame(self)

        self.w_shadow.setGeometry(40, 125, 35, 40)
        self.c_shadow.setGeometry(80, 125, 35, 40)
        self.e_shadow.setGeometry(120, 125, 35, 40)

        self.w_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;")
        self.c_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-radius: 0px;font: bold 14px Arial;")
        self.e_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;")



        self.al_button_w = QPushButton("<", self)
        self.al_button_c = QPushButton("|", self)
        self.al_button_e = QPushButton(">", self)

        if(self.main.chosen_alignment == 0): self.al_button_w.setGeometry(40, 122, 35, 40)
        else: self.al_button_w.setGeometry(40, 120, 35, 40)
        if(self.main.chosen_alignment == 1): self.al_button_c.setGeometry(80, 122, 35, 40)
        else: self.al_button_c.setGeometry(80, 120, 35, 40)
        if(self.main.chosen_alignment == 2): self.al_button_e.setGeometry(120, 122, 35, 40)
        else: self.al_button_e.setGeometry(120, 120, 35, 40)

        if(self.main.chosen_alignment == 0): self.al_button_w.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        else: self.al_button_w.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        if(self.main.chosen_alignment == 1): self.al_button_c.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-radius: 0px;font: bold 14px Arial;}}""")
        else: self.al_button_c.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-radius: 0px;font: bold 14px Arial;}}""")
        if(self.main.chosen_alignment == 2): self.al_button_e.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;}}""")
        else: self.al_button_e.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;}}""")

        self.al_buttons = [self.al_button_w, self.al_button_c, self.al_button_e]

        for ind, al_btn in enumerate(self.al_buttons):
            al_btn.clicked.connect(lambda checked, idx=ind: self.AlButtonPressed(idx))



    def PosButtonPressed(self, ind):
        old_ind = self.main.chosen_position[0] + 3*self.main.chosen_position[1]
        self.pos_buttons[old_ind].setStyleSheet(f"""
                                QPushButton {{
                                    background-color: {self.main.menu_bg_color_top};
                                    color: {self.main.menu_text_color};
                                    border: none;
                                    border-radius: 5;
                                    font: bold 14px Arial;
                                }}
                                QPushButton:hover {{
                                    color: {self.main.menu_bg_color};
                                    background-color: {self.main.menu_highlight_color};
                                }}
                            """)
        self.pos_buttons[ind].setStyleSheet(f"""
                                QPushButton {{
                                    background-color: {self.main.menu_highlight_color};
                                    color: {self.main.menu_bg_color};
                                    border: none;
                                    border-radius: 5;
                                    font: bold 14px Arial;
                                }}
                            """)

        self.main.chosen_position = (ind % 3, ind // 3)
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()


    def AlButtonPressed(self, ind):
        if(ind == self.main.chosen_alignment): return

        old_ind = self.main.chosen_alignment
        old_btn = self.al_buttons[old_ind]
        new_btn = self.al_buttons[ind]

        self.up_anim = QPropertyAnimation(old_btn,b"pos")
        self.up_anim.setStartValue(old_btn.pos())
        self.up_anim.setEndValue(old_btn.pos() + QPoint(0, -2))
        self.up_anim.setDuration(200)
        self.up_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.down_anim = QPropertyAnimation(new_btn, b"pos")
        self.down_anim.setStartValue(new_btn.pos())
        self.down_anim.setEndValue(new_btn.pos() + QPoint(0, 2))
        self.down_anim.setDuration(200)
        self.down_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        self.up_anim.start()
        self.down_anim.start()

        def ChangeAlButtonStyle(ind, is_new):
            if(is_new):
                if(ind == 0):
                    self.al_buttons[ind].setStyleSheet(f" border-top-left-radius: 5px; border-bottom-left-radius: 5px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: bold 14px Arial;")
                if (ind == 1):
                    self.al_buttons[ind].setStyleSheet(f"border-radius: 0px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: bold 14px Arial;")
                if (ind == 2):
                    self.al_buttons[ind].setStyleSheet(f" border-top-right-radius: 5px; border-bottom-right-radius: 5px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: bold 14px Arial;")

            else:
                if (ind == 0):
                    self.al_buttons[ind].setStyleSheet(f" border-top-left-radius: 5px; border-bottom-left-radius: 5px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: bold 14px Arial;")
                if (ind == 1):
                    self.al_buttons[ind].setStyleSheet(f"border-radius: 0px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: bold 14px Arial;")
                if (ind == 2):
                    self.al_buttons[ind].setStyleSheet(f" border-top-right-radius: 5px; border-bottom-right-radius: 5px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: bold 14px Arial;")


        ChangeAlButtonStyle(old_ind, False)
        ChangeAlButtonStyle(ind, True)

        self.main.chosen_alignment = ind
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()


    def ChangeTheme(self):
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.title_shadow.setStyleSheet(
            f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.description.setStyleSheet(
            f"color: {self.main.menu_text_color}; background-color: transparent; padding: 10px;")

        for ind, pos_btn in enumerate(self.pos_buttons):
            pos_btn.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: {self.main.menu_bg_color_top};
                                            color: {self.main.menu_text_color};
                                            border: none;
                                            border-radius: 5;
                                            font: bold 14px Arial;
                                        }}
                                        QPushButton:hover {{                                                       
                                            background-color: {self.main.menu_highlight_color};
                                            color: {self.main.menu_bg_color};
                                        }}
                                    """)

        self.pos_buttons[self.main.chosen_position[0] + self.main.chosen_position[1]*3].setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-radius: 5; font: bold 14px Arial;")
        self.w_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;")
        self.c_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-radius: 0px;font: bold 14px Arial;")
        self.e_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;")

        self.al_button_w.setStyleSheet(
            f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        self.al_button_c.setStyleSheet(
            f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-radius: 0px;font: bold 14px Arial;}}""")
        self.al_button_e.setStyleSheet(
            f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;}}""")

        if(self.main.chosen_alignment == 0): self.al_buttons[0].setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        if(self.main.chosen_alignment == 1): self.al_buttons[1].setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-radius: 0px; font: bold 14px Arial;}}""")
        if(self.main.chosen_alignment == 2): self.al_buttons[2].setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;}}""")
class FontSection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.setFixedSize(520, 80)
        self.main = main

        # Background
        self.bottom_bg_rect = QFrame(self)
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.bottom_bg_rect.setGeometry(0, 0, 520, 80)



        # Title
        self.title_shadow = QLabel("FONT", self)
        self.title_shadow.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_shadow.setStyleSheet(f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title_shadow.setGeometry(0, 0, 80, 32)

        self.title = QLabel("FONT", self)
        self.title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.title.setGeometry(0, -4, 80, 32)

        # Description
        self.description = QLabel("Font of the lyrics:", self)
        self.description.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.description.setStyleSheet(f"color: {self.main.menu_text_color}; background-color: transparent; padding: 10px;")
        self.description.setGeometry(85, 0, 440, 40)

        # Font dropdown
        self.font_shadow = QPushButton("", self)
        self.font_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color}; border-radius: 5px; padding: 10px;")
        self.font_shadow.setGeometry(102, 53, 100, 20)

        self.font_button = QComboBox(self)
        self.font_button.setGeometry(102, 48, 100, 20)

        common_fonts = [
            "Arial",
            "Times New Roman",
            "Helvetica",
            "Calibri",
            "Georgia",
            "Verdana",
            "Comic Sans MS",
            "Trebuchet MS",
            "Courier New",
            "Impact"
        ]
        self.font_button.addItems(common_fonts)

        current_index = self.font_button.findText(self.main.chosen_font)
        if current_index >= 0:
            self.font_button.setCurrentIndex(current_index)

        self.font_button.setStyleSheet(f"""
                    QComboBox {{
                        background-color: {self.main.menu_bg_color_top};
                        color: {self.main.menu_text_color};
                        border: none;
                        border-radius: 5px;
                        padding: 2px 5px;
                        font: bold 12px Arial;
                        text-align: center;
                        qproperty-alignment: AlignCenter;
                    }}
                    QComboBox:hover {{
                        background-color: {self.main.menu_highlight_color};
                        color: {self.main.menu_bg_color};
                    }}
                    QComboBox::drop-down {{
                        border: none;
                        width: 20px;
                    }}
                    QComboBox QAbstractItemView {{
                        background-color: {self.main.menu_bg_color_top};
                        color: {self.main.menu_bg_color};
                        selection-color: {self.main.menu_bg_color};
                        border: 3px solid {self.main.menu_highlight_color};
                    }}
                    QScrollBar:vertical {{
                    border: none;
                    background: {self.main.menu_highlight_color};  
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                    }}
                """)

        self.font_button.currentTextChanged.connect(self.FontChanged)

        # Font specials
        self.bold_shadow = QFrame(self)
        self.italic_shadow = QFrame(self)
        self.underline_shadow = QFrame(self)

        self.bold_shadow.setGeometry(245, 55, 25, 20)
        self.italic_shadow.setGeometry(275, 55, 25, 20)
        self.underline_shadow.setGeometry(305, 55, 25, 20)

        self.bold_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;")
        self.italic_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-radius: 0px;font: bold 14px Arial;")
        self.underline_shadow.setStyleSheet(f"background-color: {self.main.menu_highlight_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;")

        self.bold_button = QPushButton("B", self)
        self.italic_button = QPushButton("I", self)
        self.underline_button = QPushButton("U", self)

        if(self.main.chosen_bold): self.bold_button.setGeometry(245, 52, 25, 20)
        else: self.bold_button.setGeometry(245, 50, 25, 20)
        if(self.main.chosen_italic): self.italic_button.setGeometry(275, 52, 25, 20)
        else: self.italic_button.setGeometry(275, 50, 25, 20)
        if(self.main.chosen_underline): self.underline_button.setGeometry(305, 52, 25, 20)
        else: self.underline_button.setGeometry(305, 50, 25, 20)

        if(self.main.chosen_bold): self.bold_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        else: self.bold_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        if(self.main.chosen_italic): self.italic_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-radius: 0px;font: italic 14px Arial;}}""")
        else: self.italic_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-radius: 0px;font: italic 14px Arial;}}""")
        if(self.main.chosen_underline): self.underline_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_bg_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: 14px Arial; text-decoration: underline}}""")
        else: self.underline_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: 14px Arial; text-decoration: underline}}""")

        self.special_buttons = [self.bold_button, self.italic_button, self.underline_button]

        for ind, special_btn in enumerate(self.special_buttons):
            special_btn.clicked.connect(lambda checked, idx=ind: self.SpecialButtonPressed(idx))


        # Font size
        self.size_button = QSpinBox(self)
        self.size_button.setGeometry(375, 52, 35, 25)
        self.size_label = QLabel("px", self)
        self.size_label.setStyleSheet(f"background-color: none;font: bold 16px Arial; color: {self.main.menu_bg_color_top}")
        self.size_label.setGeometry(414, 53, 20, 20)

        self.size_button.setRange(8, 80)
        self.size_button.setValue(int(self.main.chosen_size))
        self.size_button.setStyleSheet(f"""
                    QSpinBox {{
                        background-color: transparent;
                        color: {self.main.menu_text_color};
                        border: 3px solid {self.main.menu_bg_color_top};
                        border-radius: 5px;
                        font: bold 12px Arial;
                    }}
                    QSpinBox:hover {{
                        border: 3px solid {self.main.menu_highlight_color};
                    }}
                    QSpinBox::up-button, QSpinBox::down-button {{
                    width: 0px;
                    height: 0px;
                    border: none;
                    }}
                """)
        self.size_button.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.size_button.valueChanged.connect(self.SizeChanged)

    def FontChanged(self, font_name):
        self.main.chosen_font = font_name
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()

    def SizeChanged(self, size_value):
        self.main.chosen_size = float(size_value)
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()
    def SpecialButtonPressed(self, ind):
        if (ind == 0):
            self.main.chosen_bold = not self.main.chosen_bold
            new_state = self.main.chosen_bold

        elif (ind == 1):
            self.main.chosen_italic = not self.main.chosen_italic
            new_state = self.main.chosen_italic

        else:
            self.main.chosen_underline = not self.main.chosen_underline
            new_state = self.main.chosen_underline

        btn = self.special_buttons[ind]

        if(new_state == False):
            self.move_anim = QPropertyAnimation(btn, b"pos")
            self.move_anim.setStartValue(btn.pos())
            self.move_anim.setEndValue(btn.pos() + QPoint(0, -2))
            self.move_anim.setDuration(200)
            self.move_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        else:
            self.move_anim = QPropertyAnimation(btn, b"pos")
            self.move_anim.setStartValue(btn.pos())
            self.move_anim.setEndValue(btn.pos() + QPoint(0, 2))
            self.move_anim.setDuration(200)
            self.move_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        self.move_anim.start()

        def ChangeSpecialButtonStyle(ind, state):
            if (state):
                if (ind == 0):
                    self.special_buttons[ind].setStyleSheet(
                        f" border-top-left-radius: 5px; border-bottom-left-radius: 5px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: bold 14px Arial;")
                if (ind == 1):
                    self.special_buttons[ind].setStyleSheet(
                        f"border-radius: 0px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: italic 14px Arial;")
                if (ind == 2):
                    self.special_buttons[ind].setStyleSheet(
                        f" border-top-right-radius: 5px; border-bottom-right-radius: 5px; background-color: {self.main.menu_highlight_color}; color: {self.main.menu_bg_color}; border: none; font: 14px Arial; text-decoration: underline;")

            else:
                if (ind == 0):
                    self.special_buttons[ind].setStyleSheet(
                        f" border-top-left-radius: 5px; border-bottom-left-radius: 5px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: bold 14px Arial;")
                if (ind == 1):
                    self.special_buttons[ind].setStyleSheet(
                        f"border-radius: 0px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: italic 14px Arial;")
                if (ind == 2):
                    self.special_buttons[ind].setStyleSheet(
                        f" border-top-right-radius: 5px; border-bottom-right-radius: 5px; background-color: {self.main.menu_bg_color_top}; color: {self.main.menu_text_color}; border: none; font: bold 14px Arial; text-decoration: underline;")

        ChangeSpecialButtonStyle(ind, new_state)
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()


    def ChangeTheme(self):
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.title_shadow.setStyleSheet(
            f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.description.setStyleSheet(
            f"color: {self.main.menu_text_color}; background-color: transparent; padding: 10px;")
        self.font_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color}; border-radius: 5px; padding: 10px;")
        self.font_button.setStyleSheet(f"""
                            QComboBox {{
                                background-color: {self.main.menu_bg_color_top};
                                color: {self.main.menu_text_color};
                                border: none;
                                border-radius: 5px;
                                padding: 2px 5px;
                                font: bold 12px Arial;
                                text-align: center;
                                qproperty-alignment: AlignCenter;
                            }}
                            QComboBox:hover {{
                                background-color: {self.main.menu_highlight_color};
                                color: {self.main.menu_bg_color};
                            }}
                            QComboBox::drop-down {{
                                border: none;
                                width: 20px;
                            }}
                            QComboBox QAbstractItemView {{
                                background-color: {self.main.menu_bg_color_top};
                                color: {self.main.menu_bg_color};
                                selection-color: {self.main.menu_bg_color};
                                border: 3px solid {self.main.menu_highlight_color};
                            }}
                            QScrollBar:vertical {{
                            border: none;
                            background: {self.main.menu_highlight_color};  
                            width: 10px;
                            margin: 0px 0px 0px 0px;
                            }}
                        """)
        self.bold_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;")
        self.italic_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-radius: 0px;font: bold 14px Arial;")
        self.underline_shadow.setStyleSheet(
            f"background-color: {self.main.menu_highlight_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: bold 14px Arial;")
        if(self.main.chosen_bold): self.bold_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_text_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        else: self.bold_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px; font: bold 14px Arial;}}""")
        if(self.main.chosen_italic): self.italic_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_text_color};border: none; border-radius: 0px;font: italic 14px Arial;}}""")
        else : self.italic_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-radius: 0px;font: italic 14px Arial;}}""")
        if(self.main.chosen_underline): self.underline_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_highlight_color};color: {self.main.menu_text_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: 14px Arial; text-decoration: underline}}""")
        else: self.underline_button.setStyleSheet(f"""QPushButton {{background-color: {self.main.menu_bg_color_top};color: {self.main.menu_text_color};border: none; border-top-right-radius: 5px; border-bottom-right-radius: 5px; font: 14px Arial; text-decoration: underline}}""")
        self.size_button.setStyleSheet(f"""
                            QSpinBox {{
                                background-color: transparent;
                                color: {self.main.menu_text_color};
                                border: 3px solid {self.main.menu_bg_color_top};
                                border-radius: 5px;
                                font: bold 12px Arial;
                            }}
                            QSpinBox:hover {{
                                border: 3px solid {self.main.menu_highlight_color};
                            }}
                            QSpinBox::up-button, QSpinBox::down-button {{
                            width: 0px;
                            height: 0px;
                            border: none;
                            }}
                        """)

class ColorSection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.setFixedSize(520, 80)
        self.main = main

        # Background
        self.bottom_bg_rect = QFrame(self)
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.bottom_bg_rect.setGeometry(0, 0, 520, 80)

        # Title
        self.title_shadow = QLabel("COLOR", self)
        self.title_shadow.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_shadow.setStyleSheet(f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title_shadow.setGeometry(0, 0, 105, 32)

        self.title = QLabel("COLOR", self)
        self.title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.title.setGeometry(0, -4, 105, 32)

        # Description
        self.description = QLabel("Color and opacity of the lyrics:", self)
        self.description.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.description.setStyleSheet(f"color: {self.main.menu_text_color}; background-color: transparent; padding: 10px;")
        self.description.setGeometry(110, 0, 382, 40)

        # Color Selection Button
        self.color_button = QPushButton("Pick a Color", self)
        self.color_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.main.menu_bg_color_top};
                        color: {self.main.menu_text_color};
                        border: none;
                        border-top-left-radius: 5px; 
                        border-bottom-left-radius: 5px;
                        font: bold 12px Arial;
                    }}
                    QPushButton:hover {{
                        color: {self.main.menu_bg_color};
                        background-color: {self.main.menu_highlight_color};
                    }}
                """)
        self.color_button.setGeometry(203, 42, 85, 25)
        self.color_button.clicked.connect(self.OpenColorPicker)



        # Color Preview Square
        self.color_preview = QFrame(self)
        self.color_preview.setStyleSheet(f"background-color: {self.main.chosen_color}; border: 2px solid {self.main.menu_bg_color_top};")
        self.color_preview.setGeometry(146, 42, 27, 27)

        # Opacity Selection
        self.opacity_button = QSpinBox(self)
        self.opacity_button.setGeometry(295, 42, 40, 25)
        self.opacity_button.setRange(0, 100)
        self.opacity_button.setValue(int(self.main.chosen_opacity))
        self.opacity_button.setStyleSheet(f"""
                            QSpinBox {{
                                background-color: transparent;
                                color: {self.main.menu_text_color};
                                border: 3px solid {self.main.menu_bg_color_top};
                                border-top-right-radius: 5px;
                                border-bottom-right-radius: 5px;
                                font: bold 12px Arial;
                            }}
                            QSpinBox:hover {{
                                border: 3px solid {self.main.menu_highlight_color};
                            }}
                            QSpinBox::up-button, QSpinBox::down-button {{
                            width: 0px;
                            height: 0px;
                            border: none;
                            }}
                        """)
        self.opacity_button.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opacity_button.valueChanged.connect(self.AlphaChanged)


    def AlphaChanged(self, alpha_value):
        self.main.chosen_opacity = float(alpha_value)
        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()

    def OpenColorPicker(self):
        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)

        dialog.setStyleSheet(f"""
                /* Customize the Qt color dialog here */
                QWidget {{
                    background-color: {self.main.menu_bg_color};
                    color: {self.main.menu_text_color};
                    font: bold 14px Arial;
                }}
                QPushButton {{
                    background-color: {self.main.menu_bg_color_top};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.main.menu_highlight_color};
                    color: {self.main.menu_bg_color};
                }}
                /* Add more styles for sliders, labels, etc. */
            """)

        if dialog.exec():
            color = dialog.selectedColor()
            if color.isValid():
                self.main.chosen_color = color.name()
                self.color_preview.setStyleSheet(
                    f"background-color: {color.name()}; border: 2px solid {self.main.menu_bg_color_top};")

        self.main.SaveSettings()
        self.main.UpdateDisplaySettings()


    def ChangeTheme(self):
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.title_shadow.setStyleSheet(
            f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.color_button.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {self.main.menu_bg_color_top};
                                color: {self.main.menu_text_color};
                                border: none;
                                border-top-left-radius: 5px; 
                                border-bottom-left-radius: 5px;
                                font: bold 14px Arial;
                            }}
                            QPushButton:hover {{
                                color: {self.main.menu_bg_color};
                                background-color: {self.main.menu_highlight_color};
                            }}
                        """)
        self.color_preview.setStyleSheet(
            f"background-color: {self.main.chosen_color}; border: 2px solid {self.main.menu_bg_color_top}; border-radius: 5px;")
        self.opacity_button.setStyleSheet(f"""
                                    QSpinBox {{
                                        background-color: transparent;
                                        color: {self.main.menu_text_color};
                                        border: 3px solid {self.main.menu_bg_color_top};
                                        border-top-right-radius: 5px;
                                        border-bottom-right-radius: 5px;
                                        font: bold 12px Arial;
                                    }}
                                    QSpinBox:hover {{
                                        border: 3px solid {self.main.menu_highlight_color};
                                    }}
                                    QSpinBox::up-button, QSpinBox::down-button {{
                                    width: 0px;
                                    height: 0px;
                                    border: none;
                                    }}
                                """)



class ThemeSection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.setFixedSize(520, 80)
        self.main = main

        # Background
        self.bottom_bg_rect = QFrame(self)
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.bottom_bg_rect.setGeometry(0, 0, 520, 80)

        # Title
        self.title_shadow = QLabel("THEME", self)
        self.title_shadow.setFont(QFont("Arial", 23, QFont.Weight.Bold))
        self.title_shadow.setStyleSheet(f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title_shadow.setGeometry(0, 0, 120, 40)

        self.title = QLabel("THEME", self)
        self.title.setFont(QFont("Arial", 23, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")
        self.title.setGeometry(0, -4, 120, 40)


        # Buttons
        self.shadow0 = QFrame(self)
        self.shadow0.setStyleSheet(f"background-color: {self.main.menu_highlight_color}; border-radius: 8px;")
        self.shadow0.setGeometry(135,  15, 30, 60)

        self.shadow1 = QFrame(self)
        self.shadow1.setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")
        self.shadow1.setGeometry(200, 15, 30, 60)

        self.shadow2 = QFrame(self)
        self.shadow2.setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")
        self.shadow2.setGeometry(270, 15, 30, 60)

        self.shadow3 = QFrame(self)
        self.shadow3.setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")
        self.shadow3.setGeometry(340, 15, 30, 60)

        self.shadow4 = QFrame(self)
        self.shadow4.setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")
        self.shadow4.setGeometry(410, 15, 30, 60)

        self.shadow5 = QFrame(self)
        self.shadow5.setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")
        self.shadow5.setGeometry(475, 15, 30, 60)




        self.theme_btn0 = ThemeButton("red", "#34282C", "#9A6A79", "#B296E3", parent=self)
        self.theme_btn0.setGeometry(135, 12, 30, 60)
        self.theme_btn0.clicked.connect(lambda checked, idx=0: self.ThemeButtonPressed(idx))

        self.theme_btn1 = ThemeButton("orange", "#4B392A", "#9F8065", "#E088A4", parent=self)
        self.theme_btn1.setGeometry(200, 10, 30, 60)
        self.theme_btn1.clicked.connect(lambda checked, idx=1: self.ThemeButtonPressed(idx))

        self.theme_btn2 = ThemeButton("green", "#353928", "#808377", "#DA955B", parent=self)
        self.theme_btn2.setGeometry(270, 10, 30, 60)
        self.theme_btn2.clicked.connect(lambda checked, idx=2: self.ThemeButtonPressed(idx))

        self.theme_btn3 = ThemeButton("turquoise", "#223F3A", "#748B87", "#9EB15D", parent=self)
        self.theme_btn3.setGeometry(340, 10, 30, 60)
        self.theme_btn3.clicked.connect(lambda checked, idx=3: self.ThemeButtonPressed(idx))

        self.theme_btn4 = ThemeButton("blue", "#2F4351", "#6392B0", "#42BEA9", parent=self)
        self.theme_btn4.setGeometry(410, 10, 30, 60)
        self.theme_btn4.clicked.connect(lambda checked, idx=4: self.ThemeButtonPressed(idx))

        self.theme_btn5 = ThemeButton("purple", "#4B4653", "#8169AB", "#5FB0E6", parent=self)
        self.theme_btn5.setGeometry(475, 10, 30, 60)
        self.theme_btn5.clicked.connect(lambda checked, idx=5: self.ThemeButtonPressed(idx))

        self.theme_buttons = [self.theme_btn0, self.theme_btn1, self.theme_btn2, self.theme_btn3, self.theme_btn4, self.theme_btn5]
        self.theme_shadows = [self.shadow0, self.shadow1, self.shadow2, self.shadow3, self.shadow4, self.shadow5]

        self.theme_btn0.setup_style(True)

    def ThemeButtonPressed(self, ind):
        if (ind == self.main.chosen_theme_ind): return

        old_ind = self.main.chosen_theme_ind
        old_btn = self.theme_buttons[old_ind]
        new_btn = self.theme_buttons[ind]



        self.up_anim = QPropertyAnimation(old_btn, b"pos")
        self.up_anim.setStartValue(old_btn.pos())
        self.up_anim.setEndValue(old_btn.pos() + QPoint(0, -2))
        self.up_anim.setDuration(200)
        self.up_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.down_anim = QPropertyAnimation(new_btn, b"pos")
        self.down_anim.setStartValue(new_btn.pos())
        self.down_anim.setEndValue(new_btn.pos() + QPoint(0, 2))
        self.down_anim.setDuration(200)
        self.down_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        self.up_anim.start()
        self.down_anim.start()

        self.main.chosen_theme_ind = ind
        self.main.SaveSettings()
        self.main.ChangeMenuTheme(self.theme_buttons[ind].theme_name)


    def ChangeTheme(self):
        self.bottom_bg_rect.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 10")
        self.title_shadow.setStyleSheet(
            f"color: {self.main.menu_highlight_color}; background: {self.main.menu_bg_color_bottom};")
        self.title.setStyleSheet(f"color: {self.main.menu_bg_color}; background: transparent;")

        for ind, theme_btn in enumerate(self.theme_buttons):
            if(ind == self.main.chosen_theme_ind):
                theme_btn.setup_style(True)
                self.theme_shadows[ind].setStyleSheet(f"background-color: {self.main.menu_highlight_color}; border-radius: 8px;")

            else:
                theme_btn.setup_style(False)
                self.theme_shadows[ind].setStyleSheet(f"background-color: {self.main.menu_bg_color_top}; border-radius: 8px;")


class DetailSection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setParent(main)
        self.setGeometry(0, 0, main.width(), main.height())
        self.setStyleSheet("background-color: transparent")

        with open(self.ResourcePath("images/Display Details.svg"), "r", encoding="utf-8") as file:
            self.display_file = file.read()

        with open(self.ResourcePath("images/Font Details.svg"), "r", encoding="utf-8") as file:
            self.font_file = file.read()

        with open(self.ResourcePath("images/Color Details.svg"), "r", encoding="utf-8") as file:
            self.color_file = file.read()

        self.display_details = QSvgWidget(self)
        self.font_details = QSvgWidget(self)
        self.color_details = QSvgWidget(self)

        self.display_details.load(self.ChangeSVGColor(self.display_file))
        self.font_details.load(self.ChangeSVGColor(self.font_file))
        self.color_details.load(self.ChangeSVGColor(self.color_file))

        self.display_details.setGeometry(70, 124, 450, 180)
        self.font_details.setGeometry(40, 404, 440, 40)
        self.color_details.setGeometry(150, 534, 240, 50)

    def ResourcePath(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def ChangeSVGColor(self, file):
        file = file.replace('fill="#000000"', f'fill="{self.main.menu_bg_color_top}"')
        file = file.replace('stroke="#000000"', f'stroke="{self.main.menu_bg_color_top}"')

        return QByteArray(file.encode("utf-8"))

    def ChangeTheme(self):
        self.display_details.load(self.ChangeSVGColor(self.display_file))
        self.font_details.load(self.ChangeSVGColor(self.font_file))
        self.color_details.load(self.ChangeSVGColor(self.color_file))


class LoginSection(QFrame):
    def __init__(self, main):
        super().__init__()
        self.main = main

        self.setParent(main)
        self.setGeometry(0, 0, main.width(), main.height())
        self.setStyleSheet(f"background-color: {self.main.menu_bg_color_bottom}")

        # Background
        self.background = QFrame(self)
        self.background.setStyleSheet(f"background-color: {self.main.menu_bg_color}; border-radius: 12px")
        self.background.setGeometry(100, 200, 400, 300)

        # Description
        self.word0 = QLabel("Login", self)
        self.word1 = QLabel("and", self)
        self.word2 = QLabel("start", self)
        self.word3 = QLabel("catching", self)
        self.word4 = QLabel("those", self)
        self.word5 = QLabel("lyrics", self)

        self.description = [self.word0, self.word1, self.word2, self.word3, self.word4, self.word5]

        for word in self.description:
            word.setObjectName("descLabel")
            word.setStyleSheet(f"""
                QLabel#descLabel {{
                    background: transparent;
                    color: {self.main.menu_bg_color_top};
                    font: bold 30px Arial;
                }}
                QLabel#descLabel:hover {{
                    color: {self.main.menu_highlight_color};
                }}
            """)

            word.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
            word.setMouseTracking(True)

        self.description[0].setGeometry(150, 260, 120, 40)
        self.description[1].setGeometry(240, 260, 120, 40)
        self.description[2].setGeometry(300, 260, 120, 40)
        self.description[3].setGeometry(150, 300, 140, 40)
        self.description[4].setGeometry(285, 300, 120, 40)
        self.description[5].setGeometry(375, 300, 120, 40)


        # Button
        self.shadow = QFrame(self)
        self.shadow.setStyleSheet(f"background-color: transparent; border: 5px solid {self.main.menu_bg_color_top}; border-radius: 12px")
        self.shadow.setGeometry(235, 365, 130, 90)

        self.login_button = QPushButton("Log in", self)
        self.login_button.setStyleSheet(f"""
                                            QPushButton {{
                                                background-color: {self.main.menu_bg_color_top}; 
                                                color: {self.main.menu_bg_color_bottom}; 
                                                border: none; border-radius: 8px; 
                                                font: bold 20px Arial
                                            }}
                                            QPushButton:hover {{                                                       
                                            background-color: {self.main.menu_highlight_color};
                                            color: {self.main.menu_bg_color};
                                            }}  
                                        """)
        self.login_button.setGeometry(250, 380, 100, 60)
        self.login_button.clicked.connect(self.main.Login)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())