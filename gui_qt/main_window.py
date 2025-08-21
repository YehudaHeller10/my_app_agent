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
from core.min_generator import MinProjectGenerator
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
        # Ensure LLM manager is initialized; failure is tolerated and agent will fallback
        try:
            self.llm.initialize()
        except Exception:
            pass
        self.generator = MinProjectGenerator()
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

        toolbar.addSeparator()

        # Dark mode toggle
        self.is_dark = False
        self.action_dark = QAction("Dark Mode", self)
        self.action_dark.setCheckable(True)
        self.action_dark.toggled.connect(self.toggle_dark_mode)
        toolbar.addAction(self.action_dark)

        toolbar.addSeparator()

        # Save/Load prompt
        self.action_save_prompt = QAction("Save Prompt", self)
        self.action_save_prompt.triggered.connect(self.save_prompt)
        toolbar.addAction(self.action_save_prompt)

        self.action_load_prompt = QAction("Load Prompt", self)
        self.action_load_prompt.triggered.connect(self.load_prompt)
        toolbar.addAction(self.action_load_prompt)

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
        self.button_stop = QPushButton("Stop")
        self.button_stop.setEnabled(False)
        self.button_stop.clicked.connect(self.on_stop)
        prompt_row.addWidget(self.input_prompt, stretch=1)
        prompt_row.addWidget(self.button_send)
        prompt_row.addWidget(self.button_stop)

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
        self.button_stop.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.label_status.setText("Starting...")
        self.text_log.append("Starting agent...")

        # Run in background thread to keep UI responsive
        import threading

        self._stop_requested = False
        def runner():
            try:
                def cb(phase: str, message: str) -> None:
                    if self._stop_requested:
                        raise RuntimeError("Stopped by user")
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
        self.button_stop.setEnabled(False)
        self.label_status.setText("Done")
        self.text_log.append(message)

    def on_error(self, message: str) -> None:
        self.progress_bar.setVisible(False)
        self.button_send.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.label_status.setText("Error")
        self.text_log.append(f"Error: {message}")

    # Extra features
    def toggle_dark_mode(self, enabled: bool) -> None:
        self.is_dark = enabled
        if enabled:
            # Simple dark palette via stylesheet
            self.setStyleSheet(
                """
                QMainWindow { background: #202124; }
                QWidget { color: #e8eaed; background: #202124; }
                QLineEdit, QTextEdit { background: #303134; color: #e8eaed; border: 1px solid #5f6368; }
                QPushButton { background: #3c4043; color: #e8eaed; border: 1px solid #5f6368; padding: 6px 12px; }
                QPushButton:disabled { background: #2b2b2b; color: #8e8e8e; }
                QToolBar { background: #202124; border-bottom: 1px solid #5f6368; }
                QLabel { color: #e8eaed; }
                QProgressBar { background: #303134; color: #e8eaed; border: 1px solid #5f6368; }
                QProgressBar::chunk { background: #8ab4f8; }
                """
            )
        else:
            self.setStyleSheet("")

    def save_prompt(self) -> None:
        text = self.input_prompt.text()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Prompt", self.output_dir or os.getcwd(), "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.text_log.append(f"Saved prompt to {path}")
            except Exception as e:
                self.on_error(str(e))

    def load_prompt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Prompt", self.output_dir or os.getcwd(), "Text Files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.input_prompt.setText(f.read())
                self.text_log.append(f"Loaded prompt from {path}")
            except Exception as e:
                self.on_error(str(e))

    def on_stop(self) -> None:
        # Cooperative stop flag - respected at each progress callback
        self._stop_requested = True
        self.label_status.setText("Stopping...")
        self.text_log.append("Stopping requested by user...")


def run_qt_app() -> None:
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

