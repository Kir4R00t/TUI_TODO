from textual.app import App, ComposeResult # type: ignore
from textual.widgets import Header, Footer, Input, Button, ListView, ListItem, Static, Label # type: ignore
from textual.containers import Horizontal, Vertical # type: ignore
from textual.reactive import reactive # type: ignore
from typing import Any
import logging
import json

logger = logging.getLogger(__name__)

from backend import TaskHandler, TASK_FILE

def load_tasks() -> list[dict[str, Any]]:
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return sorted(data, key=lambda t: t.get("id", 0), reverse=True)
            return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

class TaskItem(ListItem):
    def __init__(self, task: dict[str, Any]) -> None:
        self.task_data = task
        self.task_id = task.get("id")

        title = task.get("title", "(no title)")
        desc = task.get("description", "")
        ts = task.get("timestamp", "")

        # one-line, truncated
        content = Static(
            f"• [b]{title}[/b] — {desc}  [dim]{ts}[/dim]",
            classes="task"
        )
        super().__init__(content)


class TasksTUI(App):
    CSS = """
        Screen { layout: vertical; }
        #topbar { height: 5; padding: 1 1; }
        #status { height: 1; color: green; }
        Input { width: 1fr; }
        Button { width: 16; }
        ListView { height: 1fr; border: round #666; margin: 0 1; }
        ListView > ListItem { padding: 0 1; min-height: 1; height: auto; }
        .task { height: 1; overflow: hidden; text-overflow: ellipsis; }
    """

    # Keyboard shortcuts
    BINDINGS = [
        ("d", "delete_selected", "Delete selected"),
        ("r", "refresh", "Refresh"),
        ("enter", "add_from_focus", "Add when focused on inputs"),
        ("q", "quit", "Quit"),
    ]

    status_text = reactive("ready")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="topbar"):
            yield Input(placeholder="Task title…", id="title_in")
            yield Input(placeholder="Task description…", id="desc_in")
            yield Button("Add", id="add_btn", variant="primary")
            yield Button("Refresh (r)", id="refresh_btn")
            yield Button("Delete (d)", id="delete_btn", variant="error")
        yield ListView(id="tasks_list")
        yield Label(self.status_text, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_tasks()

    # Event handlers
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_btn":
            self.add_task_from_inputs()
        elif event.button.id == "refresh_btn":
            self.refresh_tasks()
        elif event.button.id == "delete_btn":
            self.delete_selected()

    def action_refresh(self) -> None:
        self.refresh_tasks()

    def action_delete_selected(self) -> None:
        self.delete_selected()

    def action_add_from_focus(self) -> None:
        focus = self.focused
        if isinstance(focus, Input):
            self.add_task_from_inputs()

    def set_status(self, msg: str, ok: bool = True) -> None:
        status = self.query_one("#status", Label)
        status.update(msg)
        status.styles.color = "green" if ok else "tomato"

    def refresh_tasks(self) -> None:
        lst = self.query_one("#tasks_list", ListView)
        lst.clear()
        for t in load_tasks():
            lst.append(TaskItem(t))
        self.set_status(f"Loaded {len(lst.children)} tasks")

    def add_task_from_inputs(self) -> None:
        title = self.query_one("#title_in", Input).value.strip()
        desc = self.query_one("#desc_in", Input).value.strip()
        if not title:
            self.set_status("Title is required", ok=False)
            return
        try:
            TaskHandler.add_task(TaskHandler, title, desc)
        except Exception as e:
            self.set_status(f"Failed to add: {e}", ok=False)
            return
        self.query_one("#title_in", Input).value = ""
        self.query_one("#desc_in", Input).value = ""
        self.refresh_tasks()
        self.set_status(f'Added "{title}"')

    def delete_selected(self) -> None:
        lst = self.query_one("#tasks_list", ListView)
        if lst.index is not None and 0 <= lst.index < len(lst.children):
            item = lst.children[lst.index]
            if isinstance(item, TaskItem):
                tid = item.task_id
                if tid is None:
                    self.set_status("Selected item has no id", ok=False)
                    return
                try:
                    TaskHandler.remove_task(TaskHandler, int(tid))
                except Exception as e:
                    self.set_status(f"Failed to delete: {e}", ok=False)
                    return
                self.refresh_tasks()
                self.set_status(f"Removed id={tid}")
        else:
            self.set_status("No selection", ok=False)
