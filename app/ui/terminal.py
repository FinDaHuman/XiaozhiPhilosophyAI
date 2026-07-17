"""
Lily Philosophy AI — Terminal Interface

A standard CLI REPL using `rich`. 
Supports native terminal input (handles Unikey/Vietnamese perfectly)
while maintaining a beautiful Codex-style experience.
"""

import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from app.rag.pipeline import RAGPipeline

console = Console()

def print_welcome():
    welcome_text = (
        "🤖 **Xin chào! Tôi là Lily**\n\n"
        "Trợ lý AI chuyên về Triết học Mác-Lênin.\n"
        "Hãy hỏi tôi bất kỳ câu hỏi nào về triết học!\n\n"
        "💡 Gõ `/help` để xem danh sách lệnh."
    )
    console.print(Panel(Markdown(welcome_text), title="Lily Philosophy AI", border_style="blue"))

def handle_command(cmd: str, rag: RAGPipeline) -> bool:
    """Handle slash commands. Returns False if we should exit."""
    cmd = cmd.lower().strip()
    
    if cmd == "/help":
        help_text = (
            "📖 **Danh sách lệnh:**\n"
            "`/help`   — Hiển thị trợ giúp\n"
            "`/clear`  — Xóa lịch sử chat\n"
            "`/reload` — Tải lại cơ sở tri thức\n"
            "`/stats`  — Thống kê hệ thống\n"
            "`/exit`   — Thoát chương trình"
        )
        console.print(Panel(Markdown(help_text), border_style="yellow"))
        
    elif cmd == "/clear":
        rag.clear_history()
        console.clear()
        print_welcome()
        console.print("[dim italic]🗑️ Đã xóa lịch sử chat và làm sạch màn hình.[/]")
        
    elif cmd == "/reload":
        with console.status("[yellow]🔄 Đang tải lại cơ sở tri thức..."):
            try:
                result = rag.reload_knowledge_base()
                stats = result.get("stats", {})
                msg = (
                    f"✅ Đã tải lại cơ sở tri thức!\n"
                    f"  Số đoạn: {stats.get('document_count', 'N/A')}"
                )
                console.print(f"[green]{msg}[/]")
            except Exception as e:
                console.print(f"[red]❌ Lỗi tải lại: {str(e)}[/]")
                
    elif cmd == "/stats":
        stats = rag.get_stats()
        kb = stats.get("knowledge_base", {})
        stats_text = (
            f"📊 **Thống kê:**\n"
            f"- Model: {stats.get('model', 'N/A')}\n"
            f"- Lượt hội thoại: {stats.get('conversation_turns', 0)}\n"
            f"- Số đoạn tài liệu: {kb.get('document_count', 'N/A')}\n"
            f"- Embedding: {kb.get('embedding_model', 'N/A')}"
        )
        console.print(Panel(Markdown(stats_text), border_style="cyan"))
        
    elif cmd == "/exit":
        console.print("[dim]👋 Tạm biệt![/]")
        return False
        
    else:
        console.print(f"[red]⚠️ Lệnh không hợp lệ: `{cmd}`. Gõ `/help` để xem danh sách lệnh.[/]")
        
    return True

def run_terminal():
    """Launch the rich REPL terminal."""
    console.clear()
    
    with console.status("[cyan]Đang khởi tạo RAG Pipeline..."):
        rag = RAGPipeline()
        
    print_welcome()
    
    while True:
        try:
            console.print()
            question = Prompt.ask("[bold blue]👤 Bạn[/]")
            question = question.strip()
            
            if not question:
                continue
                
            if question.startswith("/"):
                should_continue = handle_command(question, rag)
                if not should_continue:
                    break
                continue
            
            # AI response
            with console.status("[green]🤖 Lily đang suy nghĩ..."):
                try:
                    answer = rag.ask(question)
                except Exception as e:
                    console.print(f"[red]❌ Lỗi: {str(e)}[/]")
                    continue
            
            console.print()
            console.print(Panel(Markdown(answer), title="🤖 Lily", border_style="green", padding=(1, 2)))
            
        except KeyboardInterrupt:
            console.print("\n[dim]👋 Bấm `/exit` để thoát hoặc gõ câu hỏi mới.[/]")
            continue
        except EOFError:
            break
            
    sys.exit(0)

if __name__ == "__main__":
    run_terminal()
