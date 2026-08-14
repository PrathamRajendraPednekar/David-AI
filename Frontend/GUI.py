# Frontend/GUI.py
# PyQt5 desktop GUI + utility functions shared with the backend.
# IMPORTANT: PyQt5 imports are guarded so this module is safely importable
# in headless/server mode (when running with the Tauri frontend only).
# All utility functions — ShowTextToScreen, SetAssistantStatus, etc. —
# work without Qt and are always available.

import sys, os
from dotenv import dotenv_values

# ── Guard Qt imports ──────────────────────────────────────────────────────────
_QT_AVAILABLE = False
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget,
        QSizePolicy, QFrame, QFileDialog,
    )
    from PyQt5.QtGui import (
        QColor, QTextCharFormat, QTextBlockFormat, QFont, QPixmap,
        QIcon, QPainter,
    )
    from PyQt5.QtCore import Qt, QSize, QTimer
    from PyQt5.QtGui import QMovie
    _QT_AVAILABLE = True
except Exception:
    pass

# ── Project paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_vars       = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
Assistantname  = env_vars.get("Assistantname", "Assistant")
TempDirPath    = os.path.join(PROJECT_ROOT, "Frontend", "Files")
GraphicsDirPath = os.path.join(PROJECT_ROOT, "Frontend", "Graphics")
os.makedirs(TempDirPath, exist_ok=True)

current_dir      = PROJECT_ROOT
old_chat_message = ""

# ── Pure utility functions (no Qt needed) ─────────────────────────────────────

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query   = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how","what","who","where","when","why","which",
                      "whose","whom","can you","what's","where's","how's"]
    if any(word + " " in new_query for word in question_words):
        new_query = new_query[:-1] + "?" if query_words[-1][-1] in ".?!" else new_query + "?"
    else:
        new_query = new_query[:-1] + "." if query_words[-1][-1] in ".?!" else new_query + "."
    return new_query.capitalize()

def GraphicsDirectoryPath(Filename):
    return rf"{GraphicsDirPath}\{Filename}"

def TempDirectoryPath(Filename):
    return rf"{TempDirPath}\{Filename}"

def SetMicrophoneStatus(Command):
    with open(rf"{TempDirPath}\Mic.data", "w", encoding="utf-8") as f:
        f.write(Command)
    try:
        from Backend.Server import emit_mic
        emit_mic(str(Command).lower() == "true")
    except Exception:
        pass

def GetMicrophoneStatus():
    with open(rf"{TempDirPath}\Mic.data", "r", encoding="utf-8") as f:
        return f.read()

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as f:
        f.write(Status)
    try:
        from Backend.Server import emit_status
        emit_status(Status)
    except Exception:
        pass

def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as f:
        return f.read()

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def ShowTextToScreen(Text):
    with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as f:
        f.write(Text)
    try:
        from Backend.Server import emit_message
        if " : " in Text:
            parts       = Text.split(" : ", 1)
            sender_name = parts[0].strip()
            content     = parts[1].strip()
            sender      = "assistant" if sender_name.lower() == Assistantname.lower() else "user"
            # Only broadcast assistant messages — user messages are added
            # optimistically by the frontend's handleSend() already.
            if sender == "assistant" and content:
                emit_message("assistant", content)
        elif Text.strip():
            emit_message("assistant", Text.strip())
    except Exception:
        pass

# ── Qt-dependent classes (only defined when PyQt5 is available) ───────────────
if _QT_AVAILABLE:

    class ChatSection(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(-10, 40, 40, 100)
            layout.setSpacing(-100)

            self.chat_text_edit = QTextEdit()
            self.chat_text_edit.setReadOnly(True)
            self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
            self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
            layout.addWidget(self.chat_text_edit)
            self.setStyleSheet("background-color: black;")
            layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
            layout.setStretch(1, 1)
            self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

            fmt = QTextCharFormat()
            fmt.setForeground(QColor(Qt.blue))
            self.chat_text_edit.setCurrentCharFormat(fmt)

            self.gif_label = QLabel()
            self.gif_label.setStyleSheet("border: none;")
            movie = QMovie(GraphicsDirectoryPath("David.gif"))
            movie.setScaledSize(QSize(480, 270))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
            layout.addWidget(self.gif_label)

            self.label = QLabel("")
            self.label.setStyleSheet("color: white; font-size:16px; margin-right:195px; border:none; margin-top:-30px;")
            self.label.setAlignment(Qt.AlignRight)
            layout.addWidget(self.label)

            input_layout = QHBoxLayout()
            input_layout.setContentsMargins(10, 10, 10, 10)

            self.text_input = QLineEdit()
            self.text_input.setStyleSheet("background-color:white; color:black; font-size:16px; border-radius:5px; padding:5px;")
            self.text_input.setPlaceholderText("Type a message...")
            self.text_input.returnPressed.connect(self.send_message)

            self.attach_btn = QPushButton("📎")
            self.attach_btn.setStyleSheet("background-color:transparent; color:white; font-size:24px; border:none; margin-right:5px;")
            self.attach_btn.setCursor(Qt.PointingHandCursor)
            self.attach_btn.clicked.connect(self.attach_image)
            self.attached_image_path = ""

            self.send_icon_label = QLabel()
            self.send_icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("send-message.png")).scaled(40, 40))
            self.send_icon_label.setFixedSize(40, 40)
            self.send_icon_label.setAlignment(Qt.AlignCenter)
            self.send_icon_label.setCursor(Qt.PointingHandCursor)
            self.send_icon_label.mousePressEvent = lambda e: self.send_message()

            self.icon_label = QLabel()
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_off.png")).scaled(40, 40))
            self.icon_label.setFixedSize(40, 40)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.icon_label.setCursor(Qt.PointingHandCursor)
            self.toggled = False
            self.icon_label.mousePressEvent = self.toggle_icon

            input_layout.addWidget(self.attach_btn)
            input_layout.addWidget(self.text_input)
            input_layout.addWidget(self.icon_label)
            input_layout.addWidget(self.send_icon_label)
            layout.addLayout(input_layout)

            font = QFont()
            font.setPointSize(13)
            self.chat_text_edit.setFont(font)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.loadMessages)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(100)
            self.chat_text_edit.viewport().installEventFilter(self)

        def attach_image(self):
            path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if path:
                self.attached_image_path = path
                self.text_input.setPlaceholderText(f"[Image: {os.path.basename(path)}] Type prompt...")

        def loadMessages(self):
            global old_chat_message
            try:
                with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                    messages = f.read()
                if not messages or old_chat_message == messages:
                    return
                self.addMessage(message=messages, color="White")
                old_chat_message = messages
            except Exception:
                pass

        def SpeechRecogText(self):
            try:
                with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f:
                    self.label.setText(f.read())
            except Exception:
                pass

        def send_message(self):
            text    = self.text_input.text().strip()
            has_img = hasattr(self, "attached_image_path") and self.attached_image_path
            if text or has_img:
                final_query = f"[IMAGE:{self.attached_image_path}] {text}" if has_img else text
                with open(TempDirectoryPath("TypedQuery.data"), "w", encoding="utf-8") as f:
                    f.write(final_query)
                self.text_input.clear()
                self.text_input.setPlaceholderText("Type a message...")
                self.attached_image_path = ""

        def load_icon(self, path, width=40, height=40):
            self.icon_label.setPixmap(QPixmap(path).scaled(width, height))

        def toggle_icon(self, event=None):
            if self.toggled:
                self.load_icon(GraphicsDirectoryPath("Mic_off.png"))
                MicButtonInitialed()
                SetAssistantStatus("Available ...")
            else:
                self.load_icon(GraphicsDirectoryPath("Mic_on.png"))
                MicButtonClosed()
                SetAssistantStatus("Listening ...")
            self.toggled = not self.toggled

        def addMessage(self, message, color):
            cursor  = self.chat_text_edit.textCursor()
            fmt     = QTextCharFormat()
            fmtb    = QTextBlockFormat()
            fmtb.setTopMargin(10)
            fmtb.setLeftMargin(10)
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
            cursor.setBlockFormat(fmtb)
            cursor.insertText(message + "\n")
            self.chat_text_edit.setTextCursor(cursor)

    class InitialScreen(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            sw, sh  = desktop.screenGeometry().width(), desktop.screenGeometry().height()
            layout  = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            gif_label = QLabel()
            movie = QMovie(GraphicsDirectoryPath("David.gif"))
            movie.setScaledSize(QSize(sw, int(sw / 16 * 9)))
            gif_label.setMovie(movie)
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()

            self.icon_label = QLabel()
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_off.png")).scaled(60, 60))
            self.icon_label.setFixedSize(150, 150)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.toggled = False
            self.icon_label.mousePressEvent = self.toggle_icon

            self.label = QLabel("")
            self.label.setStyleSheet("color:white; font-size:16px; margin-bottom:0;")

            layout.addWidget(gif_label, alignment=Qt.AlignCenter)
            layout.addWidget(self.label, alignment=Qt.AlignCenter)
            layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 150)
            self.setLayout(layout)
            self.setFixedSize(sw, sh)
            self.setStyleSheet("background-color:black;")

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(100)

        def SpeechRecogText(self):
            try:
                with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f:
                    self.label.setText(f.read())
            except Exception:
                pass

        def load_icon(self, path, w=60, h=60):
            self.icon_label.setPixmap(QPixmap(path).scaled(w, h))

        def toggle_icon(self, event=None):
            if self.toggled:
                self.load_icon(GraphicsDirectoryPath("Mic_off.png"))
                MicButtonInitialed(); SetAssistantStatus("Available ...")
            else:
                self.load_icon(GraphicsDirectoryPath("Mic_on.png"))
                MicButtonClosed(); SetAssistantStatus("Listening ...")
            self.toggled = not self.toggled

    class MessageScreen(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            sw, sh  = desktop.screenGeometry().width(), desktop.screenGeometry().height()
            layout  = QVBoxLayout()
            layout.addWidget(QLabel(""))
            layout.addWidget(ChatSection())
            self.setLayout(layout)
            self.setStyleSheet("background-color:black;")
            self.setFixedSize(sw, sh)

    class CustomTopBar(QWidget):
        def __init__(self, parent, stacked_widget):
            super().__init__(parent)
            self.stacked_widget = stacked_widget
            self.initUI()

        def initUI(self):
            self.setFixedHeight(50)
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignRight)

            def _btn(icon_file, text, style="height:40px;line-height:40px;background-color:white;color:black"):
                b = QPushButton()
                b.setIcon(QIcon(GraphicsDirectoryPath(icon_file)))
                b.setText(text)
                b.setStyleSheet(style)
                return b

            home_btn    = _btn("Home.png",  "  Home")
            message_btn = _btn("Chats.png", "  Chat")
            home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            message_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

            min_btn = QPushButton()
            min_btn.setIcon(QIcon(GraphicsDirectoryPath("Minimize2.png")))
            min_btn.setStyleSheet("background-color:white")
            min_btn.clicked.connect(self.minimizeWindow)

            self.max_btn   = QPushButton()
            self.max_icon  = QIcon(GraphicsDirectoryPath("Maximize.png"))
            self.rest_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))
            self.max_btn.setIcon(self.max_icon)
            self.max_btn.setFlat(True)
            self.max_btn.setStyleSheet("background-color:white")
            self.max_btn.clicked.connect(self.maximizeWindow)

            close_btn = QPushButton()
            close_btn.setIcon(QIcon(GraphicsDirectoryPath("Close.png")))
            close_btn.setStyleSheet("background-color:white")
            close_btn.clicked.connect(self.closeWindow)

            title = QLabel(f" {Assistantname.capitalize()} AI      ")
            title.setStyleSheet("color:black; font-size:18px; background-color:white")

            layout.addWidget(title)
            layout.addStretch(1)
            layout.addWidget(home_btn)
            layout.addWidget(message_btn)
            layout.addStretch(1)
            layout.addWidget(min_btn)
            layout.addWidget(self.max_btn)
            layout.addWidget(close_btn)

        def paintEvent(self, event):
            p = QPainter(self)
            p.fillRect(self.rect(), Qt.white)
            super().paintEvent(event)

        def minimizeWindow(self):  self.parent().showMinimized()
        def closeWindow(self):     self.parent().close()

        def maximizeWindow(self):
            if self.parent().isMaximized():
                self.parent().showNormal()
                self.max_btn.setIcon(self.max_icon)
            else:
                self.parent().showMaximized()
                self.max_btn.setIcon(self.rest_icon)

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.initUI()

        def initUI(self):
            desktop = QApplication.desktop()
            sw, sh  = desktop.screenGeometry().width(), desktop.screenGeometry().height()
            self.stacked_widget = QStackedWidget(self)
            self.stacked_widget.addWidget(InitialScreen())
            self.stacked_widget.addWidget(MessageScreen())
            self.setGeometry(0, 0, sw, sh)
            self.setStyleSheet("background-color:black;")
            self.setMenuWidget(CustomTopBar(self, self.stacked_widget))
            self.setCentralWidget(self.stacked_widget)
            self.old_chat_message = ""
            try:
                with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                    self.old_chat_message = f.read()
            except Exception:
                pass
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.check_for_updates)
            self.timer.start(500)

        def check_for_updates(self):
            try:
                with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                    messages = f.read()
                if messages and self.old_chat_message != messages:
                    self.stacked_widget.setCurrentIndex(1)
                    self.old_chat_message = messages
            except Exception:
                pass

    def GraphicalUserInterface():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

else:
    # Headless stub — PyQt5 unavailable (Tauri/server mode)
    def GraphicalUserInterface():
        print("[GUI] Headless mode — PyQt5 not available, skipping legacy GUI.")


if __name__ == "__main__":
    GraphicalUserInterface()
