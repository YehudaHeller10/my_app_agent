from __future__ import annotations

import os
from typing import Optional
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QFileDialog,
    QLabel,
    QToolBar,
)

from core.llm_manager import LLMManager
from core.project_generator import ProjectGenerator
from core.simple_agent import SimpleAppAgent


class AgentSignals(QObject):
    progress = Signal(str)
    done = Signal(str)
    error = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Agent - Android App Generator")
        self.resize(1000, 700)

        # Core
        self.llm = LLMManager()
        self.generator = ProjectGenerator(self.llm)
        self.agent = SimpleAppAgent(self.llm, self.generator)
        self.signals = AgentSignals()

        # UI
        self._init_toolbar()
        self._init_body()
        self._wire_signals()

        self.output_dir: Optional[str] = os.path.abspath("output")
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.action_choose_dir = QAction("Choose Output", self)
        self.action_choose_dir.triggered.connect(self.choose_output_dir)
        toolbar.addAction(self.action_choose_dir)

        toolbar.addSeparator()

        self.action_clear = QAction("Clear Log", self)
        self.action_clear.triggered.connect(self.clear_log)
        toolbar.addAction(self.action_clear)

    def _init_body(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        prompt_row = QHBoxLayout()
        self.input_prompt = QLineEdit()
        self.input_prompt.setPlaceholderText("Describe the Android app you want...")
        self.button_send = QPushButton("Send")
        self.button_send.clicked.connect(self.on_send)
        prompt_row.addWidget(self.input_prompt, stretch=1)
        prompt_row.addWidget(self.button_send)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setVisible(False)

        self.label_status = QLabel("Idle")
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)

        layout.addLayout(prompt_row)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label_status)
        layout.addWidget(self.text_log, stretch=1)

        self.setCentralWidget(central)

    def _wire_signals(self) -> None:
        self.signals.progress.connect(self.on_progress)
        self.signals.done.connect(self.on_done)
        self.signals.error.connect(self.on_error)

    def choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir or os.getcwd())
        if directory:
            self.output_dir = directory

    def clear_log(self) -> None:
        self.text_log.clear()

    # Event handlers
    def on_send(self) -> None:
        text = self.input_prompt.text().strip()
        if not text or not self.output_dir:
            return

        self.button_send.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.label_status.setText("Starting...")
        self.text_log.append("Starting agent...")

        # Run in background thread to keep UI responsive
        import threading

        def runner():
            try:
                def cb(phase: str, message: str) -> None:
                    self.signals.progress.emit(f"{phase}: {message}")

                result = self.agent.run(text, self.output_dir, progress_cb=cb)
                if result.get("success"):
                    self.signals.done.emit(f"Project ready at {result.get('project_path')}")
                else:
                    self.signals.error.emit(result.get("error", "Unknown error"))
            except Exception as exc:
                self.signals.error.emit(str(exc))

        threading.Thread(target=runner, daemon=True).start()

    def on_progress(self, message: str) -> None:
        self.label_status.setText(message)
        self.text_log.append(message)

    def on_done(self, message: str) -> None:
        self.progress_bar.setVisible(False)
        self.button_send.setEnabled(True)
        self.label_status.setText("Done")
        self.text_log.append(message)

    def on_error(self, message: str) -> None:
        self.progress_bar.setVisible(False)
        self.button_send.setEnabled(True)
        self.label_status.setText("Error")
        self.text_log.append(f"Error: {message}")


def run_qt_app() -> None:
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

