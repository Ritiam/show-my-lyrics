import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient


class TransparentCircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transparent Circle Mouse Effect")
        self.setGeometry(100, 100, 800, 600)
        self.setMouseTracking(True)  # Enable mouse tracking

        # Square properties
        self.square_x = 300
        self.square_y = 200
        self.square_size = 200

        # Circle properties
        self.circle_radius = 80
        self.mouse_pos = QPoint(0, 0)

        # Background color
        self.setStyleSheet("background-color: lightgray;")

    def mouseMoveEvent(self, event):
        """Track mouse movement"""
        self.mouse_pos = event.pos()
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint event to draw the square with transparent circle effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the square with the transparent circle effect
        self.draw_square_with_circle_mask(painter)

    def draw_square_with_circle_mask(self, painter):
        """Draw square with circular transparency based on mouse position"""
        square_rect = (self.square_x, self.square_y, self.square_size, self.square_size)

        # Check if mouse is over the square area
        if self.is_point_in_square(self.mouse_pos.x(), self.mouse_pos.y()):
            # Draw square pixel by pixel with varying transparency
            self.draw_square_with_gradient_transparency(painter)
        else:
            # Draw normal solid square
            painter.fillRect(self.square_x, self.square_y, self.square_size, self.square_size,
                             QColor(100, 150, 200, 255))

    def is_point_in_square(self, x, y):
        """Check if point is within square bounds"""
        return (self.square_x <= x <= self.square_x + self.square_size and
                self.square_y <= y <= self.square_y + self.square_size)

    def draw_square_with_gradient_transparency(self, painter):
        """Draw square with circular gradient transparency around mouse"""
        # Create a brush for the base square color
        base_color = QColor(100, 150, 200)

        # We'll draw the square in small rectangles to create the transparency effect
        step_size = 2  # Smaller step = smoother effect, but slower performance

        for x in range(self.square_x, self.square_x + self.square_size, step_size):
            for y in range(self.square_y, self.square_y + self.square_size, step_size):
                # Calculate distance from current pixel to mouse cursor
                distance = math.sqrt((x - self.mouse_pos.x()) ** 2 + (y - self.mouse_pos.y()) ** 2)

                # Calculate alpha based on distance
                if distance <= self.circle_radius:
                    # Inside the circle - apply transparency gradient
                    # Center is most transparent (10%), edges are less transparent (80%)
                    alpha_ratio = distance / self.circle_radius
                    min_alpha = 25  # 10% opacity (90% transparent)
                    max_alpha = 204  # 80% opacity (20% transparent)
                    alpha = int(min_alpha + (max_alpha - min_alpha) * alpha_ratio)
                else:
                    # Outside the circle - full opacity
                    alpha = 255

                # Create color with calculated alpha
                color = QColor(base_color.red(), base_color.green(), base_color.blue(), alpha)
                painter.fillRect(x, y, step_size, step_size, color)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            # Increase circle radius
            self.circle_radius = min(150, self.circle_radius + 10)
            self.update()
        elif event.key() == Qt.Key.Key_Minus:
            # Decrease circle radius
            self.circle_radius = max(20, self.circle_radius - 10)
            self.update()


def main():
    app = QApplication(sys.argv)

    widget = TransparentCircleWidget()
    widget.show()

    print("Instructions:")
    print("- Move your mouse over the blue square to see the transparency effect")
    print("- Press '+' or '=' to increase circle radius")
    print("- Press '-' to decrease circle radius")
    print("- Press Escape to exit")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()