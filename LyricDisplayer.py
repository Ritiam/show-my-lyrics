import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPalette, QFontMetrics, QKeyEvent



class CustomLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._font_size = 10
        self._font_family = "Arial"
        self._y_position = 0

        self.setWordWrap(True)

        # Create opacity effect for the label
        self._opacity_effect = QGraphicsOpacityEffect()
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

    @pyqtProperty(float)
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, size):
        self._font_size = size
        # Update position when font size changes
        self.update_position()

    @pyqtProperty(float)
    def opacity(self):
        if self._opacity_effect:
            return self._opacity_effect.opacity()
        return 1.0

    @opacity.setter
    def opacity(self, value):
        if self._opacity_effect:
            self._opacity_effect.setOpacity(value)

    @pyqtProperty(float)
    def y_position(self):
        return self._y_position

    @y_position.setter
    def y_position(self, value):
        self._y_position = value
        self.update_position()

    def update_position(self):
        if self.parent():
            self._font_family = self.parent().chosen_font
        # Calculate y position based on font size
        font = QFont(self._font_family, int(self._font_size))
        font.setBold(True)
        metrics = QFontMetrics(font)
        text_height = metrics.height()
        y_pos = int(self._y_position - (text_height // 2))
        self.setGeometry(0, y_pos, 640, 1080)

        font_type = ""
        if self.parent().chosen_italic: font_type += "italic "
        if self.parent().chosen_bold: font_type += "bold "

        style_sheet = f"font: {font_type}{self._font_size}px {self._font_family}; color: {self.parent().chosen_color if self.parent() else '#FFFFFF'}; padding-left: 20px; padding-right: 20px;"
        if self.parent().chosen_underline: style_sheet += "text-decoration: underline;"


        self.setStyleSheet(style_sheet)




class DisplayWindow(QMainWindow):
    def __init__(self, font="Arial", size=40, color="#FFFFFF", opacity=0.8, position=(2, 1), alignment=2, bold=False, italic=False, underline=False):
        super().__init__()

        # Set the size
        self.setWindowTitle("Display")
        self.setGeometry(640*position[0], 0, 640, 1080)
        self.setFixedSize(640, 1080)

        # Apply the opacity and make the window stay on top
        self.setWindowOpacity(opacity)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)


        # Store settings
        self.chosen_font = font
        self.chosen_bold = bold
        self.chosen_italic = italic
        self.chosen_underline = underline
        self.chosen_size = size
        self.chosen_color = color
        self.chosen_opacity = opacity
        self.chosen_position = position
        self.chosen_alignment = alignment
        self.wrap_length = 576

        self.lyrics0 = CustomLabel("Old lyrics", self)
        self.lyrics1 = CustomLabel("Current lyrics", self)
        self.lyrics2 = CustomLabel("Future lyrics", self)
        self.lyrics3 = CustomLabel("Hidden lyrics", self)

        self.lyrics_arr = [self.lyrics0, self.lyrics1, self.lyrics2, self.lyrics3]

        self.CalculatePositions()

        for ind, lyrics in enumerate(self.lyrics_arr):
            lyrics.setGeometry(0, int(self.start_pos[ind]), 640, 1080)

        self.animation_duration = 500
        self.is_animating = False

        self.LoadLyricsStyle()



    def LoadLyricsStyle(self):
        for ind, lyrics in enumerate(self.lyrics_arr):
            if self.chosen_alignment == 0:
                lyrics.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            elif self.chosen_alignment == 1:
                lyrics.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            elif self.chosen_alignment == 2:
                lyrics.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

            font_type = ""
            if self.chosen_italic: font_type += "italic "
            if self.chosen_bold: font_type += "bold "

            style_sheet = f"font: {font_type}{self.start_size[ind]}px {self.chosen_font}; color: {self.chosen_color}; padding-left: 20px; padding-right: 20px;"
            if self.chosen_underline: style_sheet += "text-decoration: underline;"

            self.lyrics_arr[ind].setStyleSheet(style_sheet)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not self.is_animating:
            self.Animate()
        super().keyPressEvent(event)

    def Animate(self):
        self.is_animating = True

        # Create animation group
        self.animation_group = QParallelAnimationGroup()

        for i, lyrics in enumerate(self.lyrics_arr):

            start_pos = self.start_pos[i]
            start_size = self.start_size[i]

            target_pos = self.target_pos[i]
            target_size = self.target_size[i]

            if i == 0:
                start_opacity = 1.0
                target_opacity = 0.0
            elif i == 3:
                start_opacity = 0.0
                target_opacity = 1.0
            else:
                start_opacity = 1.0
                target_opacity = 1.0

            # Create position animation
            pos_animation = QPropertyAnimation(lyrics, b"y_position")
            pos_animation.setDuration(self.animation_duration)
            pos_animation.setStartValue(start_pos)
            pos_animation.setEndValue(target_pos)
            pos_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # Create font size animation
            size_animation = QPropertyAnimation(lyrics, b"font_size")
            size_animation.setDuration(self.animation_duration)
            size_animation.setStartValue(start_size)
            size_animation.setEndValue(target_size)
            size_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # Create opacity animation
            opacity_animation = QPropertyAnimation(lyrics, b"opacity")
            opacity_animation.setDuration(self.animation_duration)
            opacity_animation.setStartValue(start_opacity)
            opacity_animation.setEndValue(target_opacity)
            opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.animation_group.addAnimation(pos_animation)
            self.animation_group.addAnimation(size_animation)
            self.animation_group.addAnimation(opacity_animation)


        # Start animation
        self.animation_group.finished.connect(self.on_animation_finished)
        self.animation_group.start()
    def on_animation_finished(self):
        self.is_animating = False

    def UpdateCustomization(self, font="Arial", size=40, color="#FFFFFF", opacity=0.8, position=(2, 1), alignment=2, bold=False, italic=False, underline=False):

        # Set the window position
        self.setGeometry(640 * position[0], 0, 640, 1080)

        self.chosen_font = font
        self.chosen_size = size
        self.chosen_color = color
        self.chosen_opacity = opacity
        self.chosen_position = position
        self.chosen_alignment = alignment
        self.chosen_bold = bold
        self.chosen_italic = italic
        self.chosen_underline = underline

        self.CalculatePositions()

        # Update window opacity
        self.setWindowOpacity(opacity / 100.0)

        # Re-apply styling
        self.LoadLyricsStyle()


    def CalculatePositions(self):
        new_dist = self.chosen_size * 6 / 5

        if (self.chosen_position[1] == 0):
            self.start_pos = [new_dist * 3, new_dist * 6, new_dist * 9, new_dist * 12]
            self.target_pos = [0, new_dist * 3, new_dist * 6, new_dist * 9]

        elif (self.chosen_position[1] == 1):
            self.start_pos = [600 - new_dist * 4.5, 600 - new_dist * 1.5, 600 + new_dist * 1.5, 600 + new_dist * 4.5]
            self.target_pos = [600 - new_dist * 7.5, 600 - new_dist * 4.5, 600 - new_dist * 1.5, 600 + new_dist * 1.5]

        else:
            self.start_pos = [1080 - new_dist * 10, 1080 - new_dist * 7, 1080 - new_dist * 4, 1080 - new_dist * 1]
            self.target_pos = [1080 - new_dist * 13, 1080 - new_dist * 10, 1080 - new_dist * 7, 1080 - new_dist * 4]

        self.start_size = [self.chosen_size / 1.5, self.chosen_size, self.chosen_size / 1.5, self.chosen_size / 3]
        self.target_size = [self.chosen_size / 3, self.chosen_size / 1.5, self.chosen_size, self.chosen_size / 1.5]


    def UpdateLyrics(self, lyrics_data):
        if len(lyrics_data) >= 4:
            for i, lyric in enumerate(lyrics_data[:4]):
                if i < len(self.lyrics_arr):
                    self.lyrics_arr[i].setText(lyric)

            if not self.is_animating:
                self.Animate()



def main():
    app = QApplication(sys.argv)

    # Create window with default settings
    window = DisplayWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()