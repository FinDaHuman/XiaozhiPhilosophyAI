import asyncio
import json
import logging
import os
import signal
import subprocess
import sys

import websockets
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MCP_PIPE")

INITIAL_BACKOFF = 1
MAX_BACKOFF = 600


def load_config() -> dict:
    path = os.environ.get("MCP_CONFIG") or os.path.join(os.getcwd(), "mcp_config.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_server_command(target: str) -> tuple[list[str], dict]:
    config = load_config()
    servers = config.get("mcpServers", {}) if isinstance(config, dict) else {}

    if target in servers:
        entry = servers[target] or {}
        if entry.get("disabled"):
            raise RuntimeError(f"Server '{target}' is disabled in config")

        child_env = os.environ.copy()
        for key, value in (entry.get("env") or {}).items():
            child_env[str(key)] = str(value)

        transport_type = (entry.get("type") or entry.get("transportType") or "stdio").lower()
        if transport_type == "stdio":
            command = entry.get("command")
            args = entry.get("args") or []
            if not command:
                raise RuntimeError(f"Server '{target}' is missing 'command'")
            return [command, *args], child_env

        if transport_type in {"sse", "http", "streamablehttp"}:
            url = entry.get("url")
            if not url:
                raise RuntimeError(f"Server '{target}' is missing 'url'")
            command = [sys.executable, "-m", "mcp_proxy"]
            if transport_type in {"http", "streamablehttp"}:
                command += ["--transport", "streamablehttp"]
            for header_key, header_value in (entry.get("headers") or {}).items():
                command += ["-H", header_key, str(header_value)]
            command.append(url)
            return command, child_env

        raise RuntimeError(f"Unsupported server type: {transport_type}")

    if os.path.exists(target):
        return [sys.executable, target], os.environ.copy()

    raise RuntimeError(f"'{target}' is neither a configured server nor an existing script")


async def pipe_websocket_to_process(websocket, process, target: str) -> None:
    try:
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                message = message.decode("utf-8")
            process.stdin.write(message + "\n")
            process.stdin.flush()
    finally:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()


async def pipe_process_to_websocket(process, websocket, target: str) -> None:
    while True:
        data = await asyncio.to_thread(process.stdout.readline)
        if not data:
            logger.info("[%s] Process stdout ended", target)
            break
        await websocket.send(data)


async def pipe_process_stderr_to_terminal(process, target: str) -> None:
    while True:
        data = await asyncio.to_thread(process.stderr.readline)
        if not data:
            logger.info("[%s] Process stderr ended", target)
            break
        sys.stderr.write(data)
        sys.stderr.flush()


async def connect_to_server(uri: str, target: str) -> None:
    logger.info("[%s] Connecting to WebSocket endpoint", target)
    process = None
    try:
        async with websockets.connect(uri) as websocket:
            command, env = build_server_command(target)
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                text=True,
                env=env,
            )
            logger.info("[%s] Started server process: %s", target, " ".join(command))
            await asyncio.gather(
                pipe_websocket_to_process(websocket, process, target),
                pipe_process_to_websocket(process, websocket, target),
                pipe_process_stderr_to_terminal(process, target),
            )
    finally:
        if process:
            logger.info("[%s] Terminating server process", target)
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


async def connect_with_retry(uri: str, target: str) -> None:
    reconnect_attempt = 0
    backoff = INITIAL_BACKOFF
    while True:
        try:
            if reconnect_attempt:
                logger.info("[%s] Reconnecting in %ss", target, backoff)
                await asyncio.sleep(backoff)
            await connect_to_server(uri, target)
        except Exception as exc:
            reconnect_attempt += 1
            logger.warning("[%s] Connection closed: %s", target, exc)
            backoff = min(backoff * 2, MAX_BACKOFF)


def signal_handler(sig, frame) -> None:
    logger.info("Received interrupt signal, shutting down")
    sys.exit(0)


async def main() -> None:
    endpoint = os.environ.get("MCP_ENDPOINT")
    if not endpoint:
        raise RuntimeError("Please set MCP_ENDPOINT in .env")

    target_arg = sys.argv[1] if len(sys.argv) >= 2 else None
    if target_arg:
        await connect_with_retry(endpoint, target_arg)
        return

    servers = (load_config().get("mcpServers") or {})
    enabled = [name for name, entry in servers.items() if not (entry or {}).get("disabled")]
    if not enabled:
        raise RuntimeError("No enabled mcpServers found in config")

    logger.info("Starting servers: %s", ", ".join(enabled))
    await asyncio.gather(*(connect_with_retry(endpoint, server) for server in enabled))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
