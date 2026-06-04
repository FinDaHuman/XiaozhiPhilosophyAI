# Connecting Xiaozhi AI Hardware to XiaozhiPhilosophyAI

This tutorial explains how to connect your physical Xiaozhi AI hardware (e.g., ESP32-S3 custom builds, Astronaut Ball, Mino) to the local Philosophy AI backend using the Model Context Protocol (MCP).

The hardware communicates with the Xiaozhi cloud platform, which in turn communicates with your local backend via a WebSocket bridge, enabling the robot to use your locally hosted RAG (Retrieval-Augmented Generation) pipeline to answer complex philosophical questions.

---

## Prerequisites
1.  **Hardware:** A Xiaozhi AI device running the latest firmware (v2.0+ recommended), connected to your local Wi-Fi.
2.  **Account:** A registered account on [xiaozhi.me](https://xiaozhi.me) with your device successfully paired.
3.  **Local Backend:** The `XiaozhiPhilosophyAI` project cloned and set up on your machine (Python virtual environment activated, `.env` file created).

---

## Step-by-Step Setup

### Step 1: Obtain the MCP Endpoint from Xiaozhi Console
1.  Log in to the [Xiaozhi Console](https://xiaozhi.me).
2.  If you haven't paired your device yet, power it on, connect to its hotspot (`Xiaozhi-XXXX`) at `192.168.4.1` to enter your Wi-Fi credentials, and listen for the 6-digit pairing code to add it via **Console > Add Device**.
3.  Navigate to your **Agent** (Character Settings / Role Configuration).
4.  Scroll down to find the **MCP Settings** (Model Context Protocol) section.
5.  Locate or generate your specific **MCP WebSocket Endpoint URL**. It should look something like `wss://api.xiaozhi.me/mcp/...` and includes an authentication token. 
6.  **Copy this entire URL.**

### Step 2: Configure Your Local Environment
1.  Open the `.env` file in the root directory of the `XiaozhiPhilosophyAI` project.
2.  Add the copied URL as the `MCP_ENDPOINT` variable. Make sure you also have your Groq API key configured.
    ```ini
    # .env
    GROQ_API_KEY=gsk_your_groq_api_key_here
    MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/your-unique-token-here"
    ```

### Step 3: Initialize the Lightweight Vector Database
To ensure ultra-low latency suitable for a voice assistant hardware device, this project uses a specialized, lightweight FAISS/TF-IDF pipeline specifically for the MCP integration (separate from the heavier ChromaDB web app pipeline).

1.  Open a terminal and activate your virtual environment:
    ```bash
    # Windows
    .\venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```
2.  Navigate to the `mcp/` directory:
    ```bash
    cd mcp
    ```
3.  Build the index from your philosophy documents (which should be placed in the root `data/` folder):
    ```bash
    python rag_pipeline_faiss.py ingest
    ```

### Step 4: Start the WebSocket Bridge
1.  While still in the `mcp/` directory with the virtual environment active, start the communication pipe:
    ```bash
    python mcp_pipe.py
    ```
2.  You should see logs indicating a successful connection to the Xiaozhi cloud endpoint. This script bridges the Xiaozhi cloud with the local `mcp_rag.py` tools via stdio. **Keep this terminal running** as long as you want the hardware to be able to access the philosophy AI.

### Step 5: Test the Integration
1.  Speak to your Xiaozhi hardware. Try asking a question covered by your documents, for example: 
    *   *"Mâu thuẫn biện chứng là gì?"* (What is dialectical contradiction?)
    *   *"Nguyên nhân và kết quả có mối liên hệ như thế nào?"* (How are cause and effect related?)
2.  The hardware sends your speech to the Xiaozhi cloud.
3.  The Xiaozhi cloud routes a tool call (like `rag_answer`) through the WebSocket to your running `mcp_pipe.py`.
4.  Your local machine processes the request using the FAISS index and the Groq LLM, and sends the text answer back to the robot.
5.  The robot synthesizes the text and speaks the answer aloud.

---

## Troubleshooting

*   **MCP pipe disconnects frequently:** Check if the `MCP_ENDPOINT` token has expired in the console and update your `.env` file. The pipe is designed to auto-reconnect with exponential backoff if the connection drops.
*   **"Chua co index" (No index) error:** This means the local database hasn't been built. Ensure you ran `python rag_pipeline_faiss.py ingest` inside the `mcp/` folder.
*   **The robot says it doesn't know how to do that:** The Xiaozhi cloud may not have successfully discovered the tools. Restart the `mcp_pipe.py` script and check the "MCP Logs" inside the xiaozhi.me console to ensure tools like `rag_answer` and `rag_search` are registered.
*   **No response or errors in terminal:** Check the terminal running `mcp_pipe.py` for any Python exceptions. Ensure your `GROQ_API_KEY` is valid and hasn't hit its rate limit.