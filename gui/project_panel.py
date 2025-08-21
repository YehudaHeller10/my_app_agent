import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import subprocess
from typing import List, Dict, Any


class ProjectPanel(ttk.Frame):
    """
    Panel for managing generated Android projects
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.projects = []
        self.projects_file = "projects.json"
        
        self.setup_ui()
        self.load_projects()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Top toolbar
        self.create_toolbar()
        
        # Projects list
        self.create_projects_list()
        
        # Bottom status
        self.create_status_bar()
        
    def create_toolbar(self):
        """Create top toolbar with controls"""
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Left side - Title
        title_frame = ttk.Frame(toolbar)
        title_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(title_frame, text="📁 Generated Projects", 
                 font=('Segoe UI', 14, 'bold')).pack(side='left')
        
        # Right side - Controls
        controls_frame = ttk.Frame(toolbar)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Refresh", 
                  command=self.refresh_projects).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="📂 Open Folder", 
                  command=self.open_projects_folder).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="🗑️ Clear History", 
                  command=self.clear_history).pack(side='left', padx=2)
        
    def create_projects_list(self):
        """Create the projects list view"""
        # Projects container
        projects_container = ttk.Frame(self)
        projects_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        projects_container.grid_rowconfigure(0, weight=1)
        projects_container.grid_columnconfigure(0, weight=1)
        
        # Create Treeview for projects
        columns = ('Name', 'Path', 'Date', 'Status')
        self.projects_tree = ttk.Treeview(projects_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.projects_tree.heading('Name', text='Project Name')
        self.projects_tree.heading('Path', text='Location')
        self.projects_tree.heading('Date', text='Created')
        self.projects_tree.heading('Status', text='Status')
        
        self.projects_tree.column('Name', width=200)
        self.projects_tree.column('Path', width=300)
        self.projects_tree.column('Date', width=150)
        self.projects_tree.column('Status', width=100)
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(projects_container, orient='vertical', command=self.projects_tree.yview)
        tree_scroll_x = ttk.Scrollbar(projects_container, orient='horizontal', command=self.projects_tree.xview)
        self.projects_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Grid layout
        self.projects_tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Bind events
        self.projects_tree.bind('<Double-1>', self.on_project_double_click)
        self.projects_tree.bind('<Button-3>', self.show_context_menu)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open in Android Studio", command=self.open_in_android_studio)
        self.context_menu.add_command(label="Open in File Explorer", command=self.open_in_file_explorer)
        self.context_menu.add_command(label="Copy Path", command=self.copy_project_path)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Project", command=self.delete_project)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side='left')
        
        # Project count
        self.project_count_label = ttk.Label(status_frame, text="0 projects")
        self.project_count_label.pack(side='right')
        
    def load_projects(self):
        """Load projects from JSON file"""
        try:
            if os.path.exists(self.projects_file):
                with open(self.projects_file, 'r') as f:
                    self.projects = json.load(f)
            else:
                self.projects = []
                
            self.refresh_projects_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")
            self.projects = []
            
    def save_projects(self):
        """Save projects to JSON file"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save projects: {str(e)}")
            
    def refresh_projects_list(self):
        """Refresh the projects list display"""
        # Clear existing items
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
            
        # Add projects
        for project in self.projects:
            # Check if project still exists
            exists = os.path.exists(project['path'])
            status = "✅ Exists" if exists else "❌ Missing"
            
            self.projects_tree.insert('', 'end', values=(
                project['name'],
                project['path'],
                project.get('date', 'Unknown'),
                status
            ))
            
        # Update status
        self.project_count_label.config(text=f"{len(self.projects)} projects")
        
    def add_project(self, project_info: Dict[str, Any]):
        """Add a new project to the list"""
        # Check if project already exists
        for project in self.projects:
            if project['path'] == project_info['project_path']:
                return
                
        # Add new project
        new_project = {
            'name': project_info['project_name'],
            'path': project_info['project_path'],
            'date': project_info.get('timestamp', ''),
            'config': project_info.get('config', {})
        }
        
        self.projects.append(new_project)
        self.save_projects()
        self.refresh_projects_list()
        
    def refresh_projects(self):
        """Refresh the projects list"""
        self.load_projects()
        self.status_label.config(text="Projects refreshed")
        
    def open_projects_folder(self):
        """Open the projects folder in file explorer"""
        if self.projects:
            # Open the folder of the first project
            project_dir = os.path.dirname(self.projects[0]['path'])
            self.open_folder(project_dir)
        else:
            # Open default projects directory
            default_dir = os.path.join(os.path.expanduser("~"), "AndroidProjects")
            os.makedirs(default_dir, exist_ok=True)
            self.open_folder(default_dir)
            
    def open_folder(self, path: str):
        """Open folder in system file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['xdg-open', path] if os.name == 'posix' else ['open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
            
    def clear_history(self):
        """Clear project history"""
        if messagebox.askyesno("Clear History", 
                              "Are you sure you want to clear the project history? This will not delete the actual projects."):
            self.projects = []
            self.save_projects()
            self.refresh_projects_list()
            self.status_label.config(text="History cleared")
            
    def on_project_double_click(self, event):
        """Handle double-click on project"""
        selection = self.projects_tree.selection()
        if selection:
            item = self.projects_tree.item(selection[0])
            project_path = item['values'][1]
            self.open_in_android_studio(project_path)
            
    def show_context_menu(self, event):
        """Show context menu for right-click"""
        selection = self.projects_tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_selected_project(self) -> Dict[str, Any]:
        """Get the currently selected project"""
        selection = self.projects_tree.selection()
        if selection:
            item = self.projects_tree.item(selection[0])
            project_name = item['values'][0]
            project_path = item['values'][1]
            
            # Find project in our list
            for project in self.projects:
                if project['name'] == project_name and project['path'] == project_path:
                    return project
        return None
        
    def open_in_android_studio(self, project_path: str = None):
        """Open project in Android Studio"""
        if not project_path:
            project = self.get_selected_project()
            if not project:
                messagebox.showwarning("Warning", "Please select a project first.")
                return
            project_path = project['path']
            
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Project directory does not exist.")
            return
            
        try:
            # Try to open with Android Studio
            if os.name == 'nt':  # Windows
                subprocess.run(['studio64.exe', project_path], shell=True)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['studio.sh', project_path])
            else:
                # Fallback to opening the folder
                self.open_folder(project_path)
                
            self.status_label.config(text=f"Opening {os.path.basename(project_path)} in Android Studio")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Android Studio: {str(e)}\n\nPlease open the project manually.")
            
    def open_in_file_explorer(self):
        """Open project folder in file explorer"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Warning", "Please select a project first.")
            return
            
        project_path = project['path']
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Project directory does not exist.")
            return
            
        self.open_folder(project_path)
        self.status_label.config(text=f"Opened {project['name']} folder")
        
    def copy_project_path(self):
        """Copy project path to clipboard"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Warning", "Please select a project first.")
            return
            
        try:
            self.clipboard_clear()
            self.clipboard_append(project['path'])
            self.status_label.config(text="Project path copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy path: {str(e)}")
            
    def delete_project(self):
        """Delete project from list and optionally from disk"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Warning", "Please select a project first.")
            return
            
        # Ask user what to delete
        choice = messagebox.askyesnocancel(
            "Delete Project",
            f"Do you want to delete '{project['name']}'?\n\n"
            "Yes = Delete from disk and list\n"
            "No = Remove from list only\n"
            "Cancel = Cancel operation"
        )
        
        if choice is None:  # Cancel
            return
            
        if choice:  # Delete from disk
            try:
                import shutil
                shutil.rmtree(project['path'])
                self.status_label.config(text=f"Deleted {project['name']} from disk")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project: {str(e)}")
                return
                
        # Remove from list
        self.projects = [p for p in self.projects if p['path'] != project['path']]
        self.save_projects()
        self.refresh_projects_list()
        
        if not choice:  # Only removed from list
            self.status_label.config(text=f"Removed {project['name']} from list")