import os
import json
from typing import Callable, Dict, Any, Optional

from core.llm_manager import LLMManager
from core.project_generator import ProjectGenerator


class SimpleAppAgent:
    """
    A simplified, user-friendly agent that:
    1) Plans: uses the LLM to derive a project name and short description
    2) Builds: uses ProjectGenerator to create a runnable Android project

    Exposes a single run() method with a simple progress callback.
    """

    def __init__(self, llm_manager: LLMManager, project_generator: ProjectGenerator) -> None:
        self.llm = llm_manager
        self.generator = project_generator

    def _emit(self, cb: Optional[Callable[[str, str], None]], phase: str, message: str) -> None:
        if cb:
            try:
                cb(phase, message)
            except Exception:
                pass

    def _plan(self, request: str) -> Dict[str, str]:
        prompt = (
            "You help non-technical users name and describe Android apps.\n"
            "Given their request, propose: project_name (short, safe), description (2-3 lines).\n"
            "Return JSON with keys: project_name, description.\n\n"
            f"REQUEST:\n{request}\n"
        )
        reply = self.llm.generate_response(prompt, prompt_type='default')
        plan = self._safe_parse_json(reply)
        if not plan:
            plan = {
                "project_name": "MyAndroidApp",
                "description": request.strip() or "Simple Android application"
            }
        # sanitize fallback name
        name = plan.get("project_name", "MyAndroidApp").strip() or "MyAndroidApp"
        plan["project_name"] = name
        return plan

    def _safe_parse_json(self, text: str) -> Optional[Dict[str, str]]:
        try:
            text = text.strip()
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end + 1])
            return json.loads(text)
        except Exception:
            return None

    def run(
        self,
        request: str,
        output_dir: str,
        progress_cb: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the simple pipeline and create a runnable Android project.

        progress_cb receives (phase, message) where phase in:
        - planning, generating, done, error
        """
        if not output_dir or not os.path.isdir(output_dir):
            raise ValueError("Output directory must exist")

        self._emit(progress_cb, "planning", "Thinking of a good app name and summary...")
        plan = self._plan(request)
        project_name = plan.get("project_name", "MyAndroidApp")
        description = plan.get("description", request)
        self._emit(progress_cb, "planning", f"I'll create: {project_name}")

        def gen_cb(step_key: str, message: str, phase: str):
            # Map generator phases to friendly updates
            icon = {
                'start': '⏳',
                'done': '✅',
                'error': '❌'
            }.get(phase, 'ℹ️')
            self._emit(progress_cb, "generating", f"{icon} {message}")

        self._emit(progress_cb, "generating", "Setting up the project files...")
        result = self.generator.generate_project(
            project_name=project_name,
            description=description,
            output_dir=output_dir,
            progress_callback=gen_cb
        )

        if not result.get('success'):
            self._emit(progress_cb, "error", result.get('error', 'Unknown error'))
            return result

        self._emit(progress_cb, "done", f"Project ready at {result.get('project_path')}")
        result['plan'] = plan
        return result

