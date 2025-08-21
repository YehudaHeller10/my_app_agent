import os
import json
import threading
import time
from typing import Callable, Dict, Any, Optional, List

from core.llm_manager import LLMManager


class UserFriendlyAgent:
    """
    A user-friendly Agent that plans, generates, and writes code into files with
    intermediate progress updates. Intended for a general audience with clear, simple
    guidance messages and safe file-writing defaults.

    Usage pattern:
    - Call run("Make a weather app...") with callbacks for progress and file events
    - The agent decomposes tasks, proposes a file plan, writes files, and reports
      intermediate messages like a friendly AGENT.
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        default_output_dir: Optional[str] = None,
    ) -> None:
        self.llm = llm_manager
        self.default_output_dir = default_output_dir or os.path.join(os.getcwd(), "output", "agent")
        os.makedirs(self.default_output_dir, exist_ok=True)

    def _emit(self, cb: Optional[Callable[[str, str], None]], phase: str, message: str) -> None:
        if cb:
            try:
                cb(phase, message)
            except Exception:
                pass

    def _plan(self, request: str) -> Dict[str, Any]:
        prompt = (
            "You are a very friendly app-building assistant for non-programmers.\n"
            "Task: Create a simple plan for generating an app or code project from this request.\n"
            "Keep it short and concrete.\n\n"
            f"REQUEST:\n{request}\n\n"
            "Respond in JSON with keys: steps (list of strings), files (array of objects {path, purpose}),"
            " and summary (string)."
        )
        response = self.llm.generate_response(prompt, prompt_type='default')
        plan = self._safe_json_parse(response)
        if not plan:
            plan = {
                "steps": [
                    "Understand the request",
                    "Create initial project structure",
                    "Add main code files",
                    "Add a short README"
                ],
                "files": [
                    {"path": "README.md", "purpose": "Project overview and how to run"}
                ],
                "summary": "Basic plan created."
            }
        return plan

    def _generate_file_content(self, request: str, file_spec: Dict[str, Any]) -> str:
        path = file_spec.get("path", "file.txt")
        purpose = file_spec.get("purpose", "")
        language_hint = self._guess_language_from_path(path)
        code_prompt = (
            "Generate COMPLETE, ready-to-use content for the following file.\n"
            "Be friendly for non-programmers: include a few comments or headings, but keep it simple.\n"
            "Return only the file content without extra explanations.\n\n"
            f"FILE_PATH: {path}\n"
            f"FILE_PURPOSE: {purpose}\n"
            f"LANGUAGE_HINT: {language_hint}\n\n"
            f"USER_REQUEST:\n{request}\n"
        )
        return self.llm.generate_response(code_prompt, prompt_type='default')

    def _guess_language_from_path(self, path: str) -> str:
        _, ext = os.path.splitext(path.lower())
        return {
            ".md": "markdown",
            ".kt": "kotlin",
            ".java": "java",
            ".xml": "xml",
            ".json": "json",
            ".py": "python",
            ".txt": "text",
        }.get(ext, "text")

    def _safe_json_parse(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            # Try to find a JSON block inside the text
            text = text.strip()
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end + 1])
            return json.loads(text)
        except Exception:
            return None

    def _write_file(self, base_dir: str, rel_path: str, content: str) -> str:
        safe_rel = rel_path.strip().lstrip('/').lstrip('\\')
        abs_path = os.path.join(base_dir, safe_rel)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return abs_path

    def run(
        self,
        request: str,
        output_dir: Optional[str] = None,
        progress_cb: Optional[Callable[[str, str], None]] = None,
        file_cb: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the friendly agent flow. Emits human-readable phases:
        - planning: creating plan
        - preparing: creating folders
        - generating: generating file content (multiple times)
        - writing: writing a file
        - done/error: finished
        """
        base_dir = output_dir or self.default_output_dir
        os.makedirs(base_dir, exist_ok=True)

        self._emit(progress_cb, "planning", "Thinking about the best simple plan...")
        plan = self._plan(request)
        self._emit(progress_cb, "planning", "Plan ready. I will create the files now.")

        files: List[Dict[str, Any]] = plan.get("files", [])
        if not files:
            files = [{"path": "README.md", "purpose": "Project overview"}]

        written: List[Dict[str, str]] = []
        errors: List[str] = []

        self._emit(progress_cb, "preparing", "Creating folders for your project...")
        # Ensure all directories exist
        for spec in files:
            rel = spec.get("path", "").strip()
            if not rel:
                continue
            dir_name = os.path.dirname(os.path.join(base_dir, rel))
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

        for spec in files:
            rel = spec.get("path", "").strip()
            if not rel:
                continue
            self._emit(progress_cb, "generating", f"Creating: {rel}")
            try:
                content = self._generate_file_content(request, spec)
                self._emit(progress_cb, "writing", f"Saving: {rel}")
                abs_path = self._write_file(base_dir, rel, content)
                written.append({"path": rel, "abs_path": abs_path})
                if file_cb:
                    try:
                        file_cb(rel, abs_path)
                    except Exception:
                        pass
            except Exception as e:
                msg = f"Failed to create {rel}: {e}"
                errors.append(msg)
                self._emit(progress_cb, "error", msg)

        summary = plan.get("summary", "Project created.")
        self._emit(progress_cb, "done", "All set! Your files are ready.")

        return {
            "success": len(errors) == 0,
            "output_dir": base_dir,
            "written": written,
            "errors": errors,
            "plan": plan,
            "summary": summary,
        }


def run_agent_in_thread(
    agent: UserFriendlyAgent,
    request: str,
    output_dir: Optional[str],
    progress_cb: Optional[Callable[[str, str], None]],
    file_cb: Optional[Callable[[str, str], None]],
):
    """Helper to run the agent in a background thread."""
    def worker():
        try:
            agent.run(request=request, output_dir=output_dir, progress_cb=progress_cb, file_cb=file_cb)
        except Exception:
            if progress_cb:
                try:
                    progress_cb("error", "Unexpected error while running the agent.")
                except Exception:
                    pass

    threading.Thread(target=worker, daemon=True).start()

