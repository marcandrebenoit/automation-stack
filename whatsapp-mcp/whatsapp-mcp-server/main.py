from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse ,Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, date
from dotenv import load_dotenv
import secrets
import os
import json

load_dotenv()

# ========== BASIC AUTH ==========
security = HTTPBasic()
AUTH_USER = os.getenv("MCP_AUTH_USER", "yourusername")
AUTH_PASS = os.getenv("MCP_AUTH_PASS", "yourpassword")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username, AUTH_USER) and
            secrets.compare_digest(credentials.password, AUTH_PASS)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ========== APP INIT ==========
app = FastAPI()
tools: Dict[str, Callable] = {}
tool_descriptions: Dict[str, Dict[str, Any]] = {}

# ========== SERIALIZER ==========
def serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        return serialize(vars(obj))
    else:
        return obj

# ========== TOOL REGISTRATION ==========
def register_tool(name: str, description: str = "", params: Optional[Dict[str, str]] = None):
    def decorator(func: Callable):
        tools[name] = func
        tool_descriptions[name] = {
            "description": description,
            "params": params or {}
        }
        return func
    return decorator

# ========== SCHEMA ==========
class ToolRequest(BaseModel):
    tool: str = Field(..., example="list_chats")
    params: Dict[str, Any] = Field(
        default_factory=lambda: {
            "limit": 5,
            "include_last_message": True
        },
        example={
            "limit": 5,
            "include_last_message": True
        }
    )

# ========== STATIC UI ==========
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

@app.get("/ui", include_in_schema=False)
async def serve_ui_root():
    return FileResponse("ui/index.html")

# ========== TOOL ROUTES ==========
@app.get("/tools")
async def list_tools():
    return tool_descriptions

@app.post("/run_tool")
async def run_tool(
    data: ToolRequest,
    username: str = Depends(verify_credentials)
):
    try:
        tool_name = data.tool
        params = data.params

        tool_func = tools.get(tool_name)
        if not tool_func:
            return JSONResponse(content={"error": f"Tool '{tool_name}' not found"}, status_code=400)

        result = tool_func(**params)
        return JSONResponse(content=serialize(result))

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ========== WHATSAPP MCP TOOLS ==========
from whatsapp import (
    list_chats as whatsapp_list_chats,
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media
)

@register_tool("list_chats", "List recent WhatsApp chats", {
    "query": "Optional name or content search",
    "limit": "Number of chats to return",
    "page": "Page number",
    "include_last_message": "Include last message content",
    "sort_by": "Sort field (e.g. last_active)"
})
def list_chats(query: Optional[str] = None, limit: int = 20, page: int = 0,
               include_last_message: bool = True, sort_by: str = "last_active") -> List[Dict[str, Any]]:
    return whatsapp_list_chats(query, limit, page, include_last_message, sort_by)

@register_tool("search_contacts", "Search contacts by name or phone", {
    "query": "Search string"
})
def search_contacts(query: str) -> List[Dict[str, Any]]:
    return whatsapp_search_contacts(query)

@register_tool("list_messages", "List messages from a chat or contact", {
    "chat_jid": "Chat ID",
    "sender_phone_number": "Filter by sender",
    "query": "Search in message text",
    "limit": "Number of messages",
    "include_context": "Include message context"
})
def list_messages(after: Optional[str] = None, before: Optional[str] = None,
                  sender_phone_number: Optional[str] = None, chat_jid: Optional[str] = None,
                  query: Optional[str] = None, limit: int = 20, page: int = 0,
                  include_context: bool = True, context_before: int = 1, context_after: int = 1
) -> List[Dict[str, Any]]:
    return whatsapp_list_messages(after, before, sender_phone_number, chat_jid, query,
                                  limit, page, include_context, context_before, context_after)

@register_tool("get_chat", "Get full chat info by jid", {
    "chat_jid": "Chat ID",
    "include_last_message": "Include last message"
})
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    return whatsapp_get_chat(chat_jid, include_last_message)

@register_tool("get_direct_chat_by_contact", "Get 1-on-1 chat with contact", {
    "sender_phone_number": "Phone number"
})
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    return whatsapp_get_direct_chat_by_contact(sender_phone_number)

@register_tool("get_contact_chats", "Get all chats for contact jid", {
    "jid": "WhatsApp JID",
    "limit": "Pagination limit",
    "page": "Pagination page"
})
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    return whatsapp_get_contact_chats(jid, limit, page)

@register_tool("get_last_interaction", "Returns date of last message in chat", {
    "jid": "Chat JID"
})
def get_last_interaction(jid: str) -> str:
    return whatsapp_get_last_interaction(jid)

@register_tool("get_message_context", "Get context around a message", {
    "message_id": "Target message ID",
    "before": "Messages before",
    "after": "Messages after"
})
def get_message_context(message_id: str, before: int = 5, after: int = 5) -> Dict[str, Any]:
    return whatsapp_get_message_context(message_id, before, after)

@register_tool("send_message", "Send text message", {
    "recipient": "Recipient JID",
    "message": "Message body"
})
def send_message(recipient: str, message: str) -> Dict[str, Any]:
    if not recipient:
        return {"success": False, "message": "Recipient must be provided"}
    success, status_message = whatsapp_send_message(recipient, message)
    return {"success": success, "message": status_message}

@register_tool("send_file", "Send a file attachment", {
    "recipient": "Recipient JID",
    "media_path": "Local file path"
})
def send_file(recipient: str, media_path: str) -> Dict[str, Any]:
    success, status_message = whatsapp_send_file(recipient, media_path)
    return {"success": success, "message": status_message}

@register_tool("send_audio_message", "Send an audio voice message", {
    "recipient": "Recipient JID",
    "media_path": "Path to audio file"
})
def send_audio_message(recipient: str, media_path: str) -> Dict[str, Any]:
    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {"success": success, "message": status_message}

@register_tool("download_media", "Download media from a message", {
    "message_id": "Message ID",
    "chat_jid": "Chat JID"
})
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    file_path = whatsapp_download_media(message_id, chat_jid)
    if file_path:
        return {"success": True, "message": "Media downloaded successfully", "file_path": file_path}
    else:
        return {"success": False, "message": "Failed to download media"}



@app.get("/openai-tools", tags=["agent"])
def get_openai_tool_schema():
    openai_tools = []

    for name, meta in tool_descriptions.items():
        params_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param, desc in meta["params"].items():
            # Default everything to string — adjust logic if needed for types
            params_schema["properties"][param] = {
                "type": "string",
                "description": desc
            }
            params_schema["required"].append(param)

        openai_tools.append({
            "name": name,
            "description": meta["description"],
            "parameters": params_schema
        })

    return JSONResponse(content=openai_tools)


# ========== DEV SERVER ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
