"""
Xiaozhi Philosophy AI — Terminal Interface

A Textual-based TUI with a Codex CLI-style experience.
Features: conversation history, markdown rendering, commands, scrolling.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, Markdown, LoadingIndicator
from textual.binding import Binding
from textual.css.query import NoMatches
from textual import work

from app.rag.pipeline import RAGPipeline


# ─── Chat Message Widgets ───────────────────────────────────────────────────

class UserMessage(Static):
    """A user message bubble."""

    DEFAULT_CSS = """
    UserMessage {
        background: $primary-background;
        color: $text;
        margin: 1 2 0 8;
        padding: 1 2;
        border: round $primary;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"👤 **Bạn:** {message}")


class AIMessage(Markdown):
    """An AI response bubble with markdown rendering."""

    DEFAULT_CSS = """
    AIMessage {
        background: $surface;
        color: $text;
        margin: 0 8 1 2;
        padding: 1 2;
        border: round $success;
    }
    """


class SystemMessage(Static):
    """A system notification."""

    DEFAULT_CSS = """
    SystemMessage {
        color: $text-muted;
        text-style: italic;
        margin: 0 4;
        padding: 0 2;
        text-align: center;
    }
    """


# ─── Main Application ───────────────────────────────────────────────────────

class XiaozhiTerminal(App):
    """Xiaozhi Philosophy AI Terminal Interface."""

    TITLE = "Xiaozhi Philosophy AI (小智哲学)"
    SUB_TITLE = "Trợ lý Triết học Mác-Lênin"

    CSS = """
    Screen {
        background: $surface;
    }

    #chat-container {
        height: 1fr;
        border: round $primary;
        margin: 0 1;
    }

    #chat-scroll {
        height: 1fr;
        padding: 1;
    }

    #welcome {
        color: $text;
        text-align: center;
        padding: 2;
        margin: 2 4;
    }

    #input-container {
        height: auto;
        margin: 0 1 1 1;
        padding: 0;
    }

    #user-input {
        margin: 0 0;
        border: round $primary;
    }

    #loading {
        height: 3;
        margin: 0 2;
        display: none;
    }

    .loading-visible {
        display: block !important;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Thoát", show=True),
        Binding("ctrl+l", "clear_chat", "Xóa chat", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.rag = RAGPipeline()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="chat-container"):
                with VerticalScroll(id="chat-scroll"):
                    yield Static(
                        "🤖 **Xin chào! Tôi là Xiaozhi (小智)**\n\n"
                        "Trợ lý AI chuyên về Triết học Mác-Lênin.\n"
                        "Hãy hỏi tôi bất kỳ câu hỏi nào về triết học!\n\n"
                        "💡 Gõ `/help` để xem danh sách lệnh.",
                        id="welcome",
                    )
                yield LoadingIndicator(id="loading")
            with Container(id="input-container"):
                yield Input(
                    placeholder="Nhập câu hỏi triết học... (hoặc /help)",
                    id="user-input",
                )
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input."""
        message = event.value.strip()
        if not message:
            return

        # Clear input
        event.input.value = ""

        # Handle commands
        if message.startswith("/"):
            await self._handle_command(message)
            return

        # Show user message
        chat = self.query_one("#chat-scroll")
        chat.mount(UserMessage(message))

        # Show loading
        self._show_loading(True)

        # Get AI response in background
        self._get_response(message)

    @work(thread=True)
    def _get_response(self, question: str) -> None:
        """Get RAG response in a background thread."""
        try:
            answer = self.rag.ask(question)
            self.app.call_from_thread(self._display_response, answer)
        except Exception as e:
            error_msg = f"❌ Lỗi: {str(e)}"
            self.app.call_from_thread(self._display_error, error_msg)

    def _display_response(self, answer: str) -> None:
        """Display AI response in the chat."""
        chat = self.query_one("#chat-scroll")
        msg = AIMessage()
        chat.mount(msg)
        msg.update(f"🤖 **Xiaozhi:**\n\n{answer}")
        self._show_loading(False)
        chat.scroll_end(animate=True)

    def _display_error(self, error: str) -> None:
        """Display error message."""
        chat = self.query_one("#chat-scroll")
        chat.mount(SystemMessage(error))
        self._show_loading(False)
        chat.scroll_end(animate=True)

    def _show_loading(self, visible: bool) -> None:
        """Toggle loading indicator."""
        try:
            loading = self.query_one("#loading")
            if visible:
                loading.add_class("loading-visible")
            else:
                loading.remove_class("loading-visible")
        except NoMatches:
            pass

    async def _handle_command(self, command: str) -> None:
        """Process slash commands."""
        chat = self.query_one("#chat-scroll")
        cmd = command.lower().strip()

        if cmd == "/help":
            chat.mount(SystemMessage(
                "📖 **Danh sách lệnh:**\n"
                "`/help`   — Hiển thị trợ giúp\n"
                "`/clear`  — Xóa lịch sử chat\n"
                "`/reload` — Tải lại cơ sở tri thức\n"
                "`/stats`  — Thống kê hệ thống\n"
                "`/exit`   — Thoát chương trình"
            ))

        elif cmd == "/clear":
            # Remove all messages
            for child in list(chat.children):
                if child.id != "welcome":
                    child.remove()
            self.rag.clear_history()
            chat.mount(SystemMessage("🗑️ Đã xóa lịch sử chat."))

        elif cmd == "/reload":
            chat.mount(SystemMessage("🔄 Đang tải lại cơ sở tri thức..."))
            self._reload_kb()

        elif cmd == "/stats":
            stats = self.rag.get_stats()
            kb = stats.get("knowledge_base", {})
            chat.mount(SystemMessage(
                f"📊 **Thống kê:**\n"
                f"  Model: {stats.get('model', 'N/A')}\n"
                f"  Lượt hội thoại: {stats.get('conversation_turns', 0)}\n"
                f"  Số đoạn tài liệu: {kb.get('document_count', 'N/A')}\n"
                f"  Embedding: {kb.get('embedding_model', 'N/A')}"
            ))

        elif cmd == "/exit":
            self.exit()

        else:
            chat.mount(SystemMessage(f"⚠️ Lệnh không hợp lệ: `{command}`. Gõ `/help` để xem danh sách lệnh."))

        chat.scroll_end(animate=True)

    @work(thread=True)
    def _reload_kb(self) -> None:
        """Reload knowledge base in background."""
        try:
            result = self.rag.reload_knowledge_base()
            stats = result.get("stats", {})
            msg = (
                f"✅ Đã tải lại cơ sở tri thức!\n"
                f"  Số đoạn: {stats.get('document_count', 'N/A')}"
            )
            self.app.call_from_thread(self._display_system_message, msg)
        except Exception as e:
            self.app.call_from_thread(
                self._display_system_message,
                f"❌ Lỗi tải lại: {str(e)}"
            )

    def _display_system_message(self, message: str) -> None:
        """Display a system message."""
        chat = self.query_one("#chat-scroll")
        chat.mount(SystemMessage(message))
        chat.scroll_end(animate=True)

    def action_clear_chat(self) -> None:
        """Action for Ctrl+L keybinding."""
        import asyncio
        asyncio.ensure_future(self._handle_command("/clear"))


def run_terminal():
    """Launch the terminal UI."""
    app = XiaozhiTerminal()
    app.run()


if __name__ == "__main__":
    run_terminal()
