# Enhanced Agent System for Small LLMs
# מערכת אגנטים מתקדמת המקסימה את יכולות המודל הקטן

import os
import json
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


class AgentMode(Enum):
    PLANNER = "planner"  # מתכנן משימות
    CODER = "coder"  # כותב קוד
    REVIEWER = "reviewer"  # בודק קוד
    ARCHITECT = "architect"  # מעצב ארכיטקטורה
    DEBUGGER = "debugger"  # מתקן באגים


@dataclass
class Task:
    id: str
    description: str
    mode: AgentMode
    context: Dict[str, Any]
    completed: bool = False
    result: Optional[str] = None
    dependencies: List[str] = None


class EnhancedLocalLLM:
    """
    מערכת אגנטים מתקדמת המשתמשת ב-ReAct, Chain of Thought וטכניקות נוספות
    כדי למקסם את יכולות המודל הקטן ולאפשר יצירת פרויקטים מורכבים
    """

    def __init__(self, base_llm, max_context_tokens=2048):
        self.base_llm = base_llm
        self.max_context_tokens = max_context_tokens

        # זיכרון מתקדם
        self.working_memory = {}  # זיכרון עבודה קצר טווח
        self.long_term_memory = {}  # זיכרון ארוך טווח
        self.task_queue = []  # תור משימות
        self.completed_tasks = []  # משימות שהושלמו
        self.project_context = {}  # קונטקסט הפרויקט הנוכחי

        # System prompts מיוחדים לכל מצב
        self.agent_prompts = {
            AgentMode.PLANNER: self._get_planner_prompt(),
            AgentMode.CODER: self._get_coder_prompt(),
            AgentMode.REVIEWER: self._get_reviewer_prompt(),
            AgentMode.ARCHITECT: self._get_architect_prompt(),
            AgentMode.DEBUGGER: self._get_debugger_prompt(),
        }

    def _get_planner_prompt(self) -> str:
        return """You are a Project Planner Agent. Your role is to:
1. DECOMPOSE large projects into smaller, manageable tasks
2. PRIORITIZE tasks based on dependencies 
3. CREATE step-by-step implementation plans
4. ESTIMATE complexity and time for each task

Use this format for your responses:
ANALYSIS: [Brief analysis of the request]
TASKS: 
- Task 1: [description] (Priority: High/Medium/Low)
- Task 2: [description] (Priority: High/Medium/Low)
DEPENDENCIES: [List dependencies between tasks]
NEXT_ACTION: [What should be done first]

Keep responses concise and actionable."""

    def _get_coder_prompt(self) -> str:
        return """You are a Code Generation Agent. Your role is to:
1. WRITE clean, functional code for specific tasks
2. FOCUS on one component at a time
3. INCLUDE comments and documentation
4. USE best practices for the target language

Important guidelines:
- Write COMPLETE, WORKING code
- Include error handling where needed
- Keep functions small and focused
- Use clear variable names

Format your response as:
CODE_EXPLANATION: [Brief explanation of what you're implementing]
```language
[Your code here]
```
USAGE_NOTES: [How to use this code]"""

    def _get_reviewer_prompt(self) -> str:
        return """You are a Code Review Agent. Your role is to:
1. ANALYZE code for bugs and issues
2. SUGGEST improvements and optimizations
3. CHECK for best practices compliance
4. IDENTIFY potential security issues

Review format:
REVIEW_SUMMARY: [Overall assessment]
ISSUES_FOUND:
- Issue 1: [description and location]
- Issue 2: [description and location]
SUGGESTIONS:
- Suggestion 1: [improvement idea]
RATING: [1-5 stars for code quality]"""

    def _get_architect_prompt(self) -> str:
        return """You are a Software Architecture Agent. Your role is to:
1. DESIGN system architecture and structure
2. DEFINE interfaces between components  
3. CHOOSE appropriate patterns and technologies
4. PLAN file/folder structure

Architecture format:
ARCHITECTURE_OVERVIEW: [High-level system design]
COMPONENTS:
- Component 1: [purpose and responsibilities]
- Component 2: [purpose and responsibilities]
FILE_STRUCTURE:
```
project/
├── folder1/
│   ├── file1.ext
│   └── file2.ext
└── folder2/
    └── file3.ext
```
TECHNOLOGIES: [Recommended tools/frameworks]"""

    def _get_debugger_prompt(self) -> str:
        return """You are a Debug Analysis Agent. Your role is to:
1. ANALYZE error messages and stack traces
2. IDENTIFY root causes of bugs
3. SUGGEST specific fixes
4. PROVIDE debugging strategies

Debug format:
ERROR_ANALYSIS: [Analysis of the problem]
ROOT_CAUSE: [What's causing the issue]
SOLUTION: [Step-by-step fix]
PREVENTION: [How to avoid this in the future]"""

    def create_project_plan(self, project_description: str) -> List[Task]:
        """יוצר תוכנית פרויקט מפורטת מתיאור כללי"""

        # שלב 1: ניתוח ארכיטקטוני
        architect_response = self._query_agent(
            AgentMode.ARCHITECT,
            f"Design architecture for: {project_description}"
        )

        # שלב 2: תכנון משימות
        planner_response = self._query_agent(
            AgentMode.PLANNER,
            f"Create detailed task breakdown for: {project_description}\n\nArchitecture: {architect_response}"
        )

        # פירוק התשובה למשימות בפועל
        tasks = self._parse_tasks_from_response(planner_response)

        self.project_context = {
            'description': project_description,
            'architecture': architect_response,
            'plan': planner_response,
            'created_at': time.time()
        }

        return tasks

    def _query_agent(self, mode: AgentMode, query: str, context: Dict = None) -> str:
        """שולח שאילתה לאגנט ספציפי עם קונטקסט מותאם"""

        # בניית קונטקסט חכם
        prompt_parts = [self.agent_prompts[mode]]

        # הוספת קונטקסט רלוונטי
        if context:
            prompt_parts.append(f"CONTEXT: {json.dumps(context, indent=2)}")

        # הוספת זיכרון רלוונטי
        relevant_memory = self._get_relevant_memory(query, mode)
        if relevant_memory:
            prompt_parts.append(f"RELEVANT_MEMORY: {relevant_memory}")

        prompt_parts.append(f"TASK: {query}")

        full_prompt = "\n\n".join(prompt_parts)

        # שמירה על גודל הפרומפט
        if len(full_prompt) > self.max_context_tokens * 3:  # estimation
            full_prompt = self._truncate_prompt(full_prompt)

        # שליחה למודל הבסיסי
        response = self.base_llm.generate_stream(full_prompt)

        # עדכון זיכרון
        self._update_memory(mode, query, response)

        return response

    def _parse_tasks_from_response(self, planner_response: str) -> List[Task]:
        """ממיר תגובת המתכנן למשימות מובנות"""
        tasks = []

        # פרסור פשוט - ניתן לשפר עם regex מתקדם יותר
        lines = planner_response.split('\n')
        task_counter = 1

        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith(f'{task_counter}.'):
                task_description = line.strip().lstrip('-').lstrip(f'{task_counter}.').strip()

                # קביעת מצב האגנט לפי התוכן
                if any(keyword in task_description.lower() for keyword in ['architecture', 'design', 'structure']):
                    mode = AgentMode.ARCHITECT
                elif any(keyword in task_description.lower() for keyword in ['code', 'implement', 'write']):
                    mode = AgentMode.CODER
                elif any(keyword in task_description.lower() for keyword in ['test', 'review', 'check']):
                    mode = AgentMode.REVIEWER
                elif any(keyword in task_description.lower() for keyword in ['debug', 'fix', 'error']):
                    mode = AgentMode.DEBUGGER
                else:
                    mode = AgentMode.PLANNER

                task = Task(
                    id=f"task_{task_counter}",
                    description=task_description,
                    mode=mode,
                    context={'priority': self._extract_priority(task_description)}
                )
                tasks.append(task)
                task_counter += 1

        return tasks

    def _extract_priority(self, task_description: str) -> str:
        """מחלץ עדיפות מתיאור המשימה"""
        desc_lower = task_description.lower()
        if 'high' in desc_lower or 'critical' in desc_lower:
            return 'high'
        elif 'low' in desc_lower or 'optional' in desc_lower:
            return 'low'
        return 'medium'

    def execute_task(self, task: Task) -> str:
        """מבצע משימה ספציפית"""

        context = {
            'task_id': task.id,
            'project_context': self.project_context,
            'completed_tasks': [t.result for t in self.completed_tasks if t.result],
            'working_memory': self.working_memory
        }

        result = self._query_agent(task.mode, task.description, context)

        # עדכון המשימה
        task.completed = True
        task.result = result
        self.completed_tasks.append(task)

        # אם זה קוד, שמירה בזיכרון העבודה
        if task.mode == AgentMode.CODER and '```' in result:
            code_blocks = self._extract_code_blocks(result)
            self.working_memory[f"code_{task.id}"] = code_blocks

        return result

    def _extract_code_blocks(self, response: str) -> List[Dict]:
        """מחלץ בלוקי קוד מהתגובה"""
        code_blocks = []
        lines = response.split('\n')
        in_code = False
        current_code = []
        current_language = ""

        for line in lines:
            if line.strip().startswith('```'):
                if in_code:
                    # סוף בלוק קוד
                    code_blocks.append({
                        'language': current_language,
                        'code': '\n'.join(current_code)
                    })
                    current_code = []
                    in_code = False
                else:
                    # התחלת בלוק קוד
                    current_language = line.strip()[3:].strip()
                    in_code = True
            elif in_code:
                current_code.append(line)

        return code_blocks

    def _get_relevant_memory(self, query: str, mode: AgentMode) -> str:
        """מחזיר זיכרון רלוונטי לשאילתה"""
        relevant_items = []

        # חיפוש במילות מפתח
        query_words = set(query.lower().split())

        # חיפוש בזיכרון העבודה
        for key, value in self.working_memory.items():
            if any(word in str(value).lower() for word in query_words):
                relevant_items.append(f"{key}: {str(value)[:200]}...")

        # הגבלת גודל
        return "\n".join(relevant_items[:3]) if relevant_items else ""

    def _update_memory(self, mode: AgentMode, query: str, response: str):
        """מעדכן זיכרון על בסיס השאילתה והתגובה"""
        memory_key = f"{mode.value}_{len(self.long_term_memory)}"
        self.long_term_memory[memory_key] = {
            'query': query[:100] + "..." if len(query) > 100 else query,
            'response': response[:200] + "..." if len(response) > 200 else response,
            'timestamp': time.time()
        }

        # ניקוי זיכרון ישן (שמירה על 20 הפריטים האחרונים בלבד)
        if len(self.long_term_memory) > 20:
            oldest_key = min(self.long_term_memory.keys(),
                             key=lambda k: self.long_term_memory[k]['timestamp'])
            del self.long_term_memory[oldest_key]

    def _truncate_prompt(self, prompt: str) -> str:
        """מקצר פרומפט ארוך מידי"""
        max_chars = self.max_context_tokens * 3  # הערכה גסה
        if len(prompt) <= max_chars:
            return prompt

        # שמירה על התחלה והסוף
        start_portion = prompt[:max_chars // 2]
        end_portion = prompt[-max_chars // 2:]

        return f"{start_portion}\n\n... [CONTENT TRUNCATED FOR LENGTH] ...\n\n{end_portion}"

    def generate_project_iteratively(self, project_description: str, max_iterations: int = 10):
        """
        יוצר פרויקט שלם באופן איטרטיבי
        """
        print(f"🚀 Starting iterative project generation: {project_description}")

        # שלב 1: יצירת תוכנית
        tasks = self.create_project_plan(project_description)
        print(f"📋 Created {len(tasks)} tasks")

        results = []

        # שלב 2: ביצוע משימות
        for i, task in enumerate(tasks[:max_iterations]):
            print(f"🔄 Executing task {i + 1}/{len(tasks)}: {task.description[:50]}...")

            try:
                result = self.execute_task(task)
                results.append({
                    'task': task.description,
                    'mode': task.mode.value,
                    'result': result
                })
                print(f"✅ Task completed successfully")

                # שבר קצר בין משימות
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ Task failed: {e}")
                # ניסיון תיקון עם debugger agent
                debug_result = self._query_agent(
                    AgentMode.DEBUGGER,
                    f"Fix this error in task '{task.description}': {str(e)}"
                )
                results.append({
                    'task': task.description,
                    'mode': 'debugger',
                    'result': debug_result
                })

        return {
            'project_plan': self.project_context,
            'tasks_executed': results,
            'working_memory': self.working_memory,
            'summary': self._generate_project_summary()
        }

    def _generate_project_summary(self) -> str:
        """יוצר סיכום של הפרויקט שבוצע"""
        summary_prompt = f"""
        Create a brief summary of the completed project based on:

        Project: {self.project_context.get('description', 'Unknown')}
        Tasks completed: {len(self.completed_tasks)}
        Code blocks generated: {len([k for k in self.working_memory.keys() if k.startswith('code_')])}

        Provide a 2-3 sentence summary of what was accomplished.
        """

        return self._query_agent(AgentMode.PLANNER, summary_prompt)


# פונקציות עזר לאינטגרציה עם GUI הקיים
def integrate_with_existing_gui(chat_gui_instance):
    """משלב את מערכת האגנטים עם GUI הקיים"""

    # יצירת אגנט משופר
    enhanced_agent = EnhancedLocalLLM(chat_gui_instance.llm)

    # פונקציה חדשה ל-GUI
    def create_full_project(project_description):
        chat_gui_instance._append("system", f"🤖 Starting multi-agent project generation...")

        def progress_callback(message):
            chat_gui_instance._append("system", f"🔄 {message}")

        # הרצה באופן אסינכרוני
        import threading
        def worker():
            try:
                result = enhanced_agent.generate_project_iteratively(project_description)

                chat_gui_instance._append("system", f"✅ Project generation completed!")
                chat_gui_instance._append("assistant", f"Project Summary:\n{result['summary']}")

                # הצגת קבצי קוד שנוצרו
                for task_result in result['tasks_executed']:
                    if '```' in task_result['result']:
                        chat_gui_instance._append("assistant",
                                                  f"Generated for '{task_result['task']}':\n{task_result['result']}")

            except Exception as e:
                chat_gui_instance._append("system", f"❌ Error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    return create_full_project