from flask import Flask, render_template, request, jsonify
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import threading

app = Flask(__name__, template_folder="templates")

# Standard-Crosshair-Einstellungen
crosshair_settings = {
    "inner_line_width": 3,
    "inner_line_length": 10,
    "border_width": 3,
    "gap": 5,
    "inner_line_color": "#ffffff",
    "border_color": "#0000ff",
    "show_border": True,
    "show_inner_lines": True,
    "show_center_dot": False,
    "center_dot_size": 5,
    "center_dot_color": "#ffffff",
    "show_center_dot_border": True,
    "center_dot_border_color": "#ff0000",
    "center_dot_border_width": 2,  # Separate Größe für die Border des Mittelpunkts
    "scale": 1  # Skalierungsfaktor für das gesamte Crosshair
}

# Temporäre Crosshair-Einstellungen
temp_crosshair_settings = crosshair_settings.copy()

profiles = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_temp', methods=['POST'])
def update_temp_crosshair():
    global temp_crosshair_settings, overlay
    data = request.get_json()

    temp_crosshair_settings["inner_line_width"] = float(data.get("innerLineWidth", temp_crosshair_settings["inner_line_width"]))
    temp_crosshair_settings["inner_line_length"] = float(data.get("innerLineLength", temp_crosshair_settings["inner_line_length"]))
    temp_crosshair_settings["border_width"] = float(data.get("borderWidth", temp_crosshair_settings["border_width"]))
    temp_crosshair_settings["gap"] = float(data.get("gap", temp_crosshair_settings["gap"]))
    temp_crosshair_settings["inner_line_color"] = data.get("innerLineColor", temp_crosshair_settings["inner_line_color"])
    temp_crosshair_settings["border_color"] = data.get("borderColor", temp_crosshair_settings["border_color"])
    temp_crosshair_settings["show_border"] = data.get("showBorder", temp_crosshair_settings["show_border"])
    temp_crosshair_settings["show_inner_lines"] = data.get("showInnerLines", temp_crosshair_settings["show_inner_lines"])
    temp_crosshair_settings["show_center_dot"] = data.get("showCenterDot", temp_crosshair_settings["show_center_dot"])
    temp_crosshair_settings["center_dot_size"] = float(data.get("centerDotSize", temp_crosshair_settings["center_dot_size"]))
    temp_crosshair_settings["center_dot_color"] = data.get("centerDotColor", temp_crosshair_settings["center_dot_color"])
    temp_crosshair_settings["show_center_dot_border"] = data.get("showCenterDotBorder", temp_crosshair_settings["show_center_dot_border"])
    temp_crosshair_settings["center_dot_border_color"] = data.get("centerDotBorderColor", temp_crosshair_settings["center_dot_border_color"])
    temp_crosshair_settings["center_dot_border_width"] = float(data.get("centerDotBorderWidth", temp_crosshair_settings["center_dot_border_width"]))
    temp_crosshair_settings["scale"] = float(data.get("scale", temp_crosshair_settings["scale"]))

    # Trigger repaint of the overlay
    overlay.repaint()

    return jsonify(success=True)

@app.route('/apply', methods=['POST'])
def apply_crosshair():
    global crosshair_settings, temp_crosshair_settings
    crosshair_settings.update(temp_crosshair_settings)
    return jsonify(success=True)

@app.route('/reset', methods=['POST'])
def reset_crosshair():
    global temp_crosshair_settings
    temp_crosshair_settings = crosshair_settings.copy()
    overlay.repaint()
    return jsonify(success=True)

@app.route('/save_profile', methods=['POST'])
def save_profile():
    global profiles
    data = request.get_json()
    profile_name = data.get("profileName")
    if profile_name:
        profiles[profile_name] = temp_crosshair_settings.copy()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/load_profile', methods=['POST'])
def load_profile():
    global temp_crosshair_settings
    data = request.get_json()
    profile_name = data.get("profileName")
    if profile_name in profiles:
        temp_crosshair_settings = profiles[profile_name].copy()
        overlay.repaint()
        return jsonify(success=True)
    return jsonify(success=False), 400

class CrosshairOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crosshair Overlay")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        settings = temp_crosshair_settings
        scale = settings["scale"]
        inner_line_width = settings["inner_line_width"] * scale
        inner_line_length = settings["inner_line_length"] * scale
        border_width = settings["border_width"] * scale
        gap = settings["gap"] * scale
        inner_line_color = QColor(settings["inner_line_color"])
        border_color = QColor(settings["border_color"])
        show_border = settings["show_border"]
        show_inner_lines = settings["show_inner_lines"]
        show_center_dot = settings["show_center_dot"]
        center_dot_size = settings["center_dot_size"] * scale
        center_dot_color = QColor(settings["center_dot_color"])
        show_center_dot_border = settings["show_center_dot_border"]
        center_dot_border_color = QColor(settings["center_dot_border_color"])
        center_dot_border_width = settings["center_dot_border_width"] * scale

        center_x = self.width() // 2
        center_y = self.height() // 2

        if show_border:
            # Zeichne Rand um die inneren Linien
            pen = QPen()
            pen.setWidthF(inner_line_width + 2 * border_width)
            pen.setColor(border_color)
            painter.setPen(pen)

            # Horizontale Linie
            painter.drawLine(int(center_x - inner_line_length - gap), int(center_y), int(center_x - gap), int(center_y))
            painter.drawLine(int(center_x + gap), int(center_y), int(center_x + inner_line_length + gap), int(center_y))

            # Vertikale Linie
            painter.drawLine(int(center_x), int(center_y - inner_line_length - gap), int(center_x), int(center_y - gap))
            painter.drawLine(int(center_x), int(center_y + gap), int(center_x), int(center_y + inner_line_length + gap))

        if show_inner_lines:
            # Zeichne Fadenkreuz mit Lücke in der Mitte
            pen = QPen()
            pen.setWidthF(inner_line_width)
            pen.setColor(inner_line_color)
            painter.setPen(pen)

            # Horizontale Linie
            painter.drawLine(int(center_x - inner_line_length - gap), int(center_y), int(center_x - gap), int(center_y))
            painter.drawLine(int(center_x + gap), int(center_y), int(center_x + inner_line_length + gap), int(center_y))

            # Vertikale Linie
            painter.drawLine(int(center_x), int(center_y - inner_line_length - gap), int(center_x), int(center_y - gap))
            painter.drawLine(int(center_x), int(center_y + gap), int(center_x), int(center_y + inner_line_length + gap))

        if show_center_dot:
            if show_center_dot_border:
                # Zeichne Rand um den Mittelpunkt
                pen = QPen()
                pen.setWidthF(center_dot_border_width)
                pen.setColor(center_dot_border_color)
                painter.setPen(pen)
                painter.drawPoint(int(center_x), int(center_y))

            # Zeichne Mittelpunkt
            pen = QPen()
            pen.setWidthF(center_dot_size)
            pen.setColor(center_dot_color)
            painter.setPen(pen)
            painter.drawPoint(int(center_x), int(center_y))

class CustomizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customizer")
        self.setGeometry(100, 100, 800, 1000)  # Größeres Fenster
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("http://127.0.0.1:5000"))
        self.setCentralWidget(self.webview)

def start_flask():
    app.run(debug=True, use_reloader=False)

def start_overlay():
    global overlay
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    qt_app = QApplication(sys.argv)
    overlay = CrosshairOverlay()
    overlay.show()

    customizer_window = CustomizerWindow()
    customizer_window.show()
    qt_app.exec()

if __name__ == '__main__':
    start_overlay()