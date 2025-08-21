import os
import shutil
from typing import Callable, Optional, Dict, Any


class MinProjectGenerator:
    """
    Minimal project generator that copies the bundled Android template and
    applies a few lightweight substitutions (app name only).
    """

    def __init__(self, template_dir: Optional[str] = None) -> None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = template_dir or os.path.join(root, "empty_activity_template")

    def generate_project(
        self,
        project_name: str,
        description: str,
        output_dir: str,
        progress_callback: Optional[Callable[[str, str, str], None]] = None,
    ) -> Dict[str, Any]:
        try:
            if progress_callback:
                progress_callback("start", f"Preparing '{project_name}'", "start")

            if not os.path.isdir(self.template_dir):
                raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

            project_path = os.path.join(output_dir, project_name)
            if os.path.exists(project_path):
                shutil.rmtree(project_path)

            shutil.copytree(self.template_dir, project_path)

            # Update app name in strings.xml
            strings_xml = os.path.join(
                project_path, "app", "src", "main", "res", "values", "strings.xml"
            )
            if os.path.isfile(strings_xml):
                try:
                    text = open(strings_xml, "r", encoding="utf-8").read()
                    text = text.replace("<string name=\"app_name\">empty_activity_template</string>", f"<string name=\"app_name\">{project_name}</string>")
                    with open(strings_xml, "w", encoding="utf-8") as f:
                        f.write(text)
                except Exception:
                    pass

            if progress_callback:
                progress_callback("done", "Project files ready", "done")

            return {
                "success": True,
                "project_path": project_path,
                "description": description,
            }
        except Exception as e:
            if progress_callback:
                progress_callback("error", str(e), "error")
            return {"success": False, "error": str(e)}

