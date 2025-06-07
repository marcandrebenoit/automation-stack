const BASE_URL = "/run_tool";

const authHeader = {
  Authorization: "Basic " + btoa("mcpadmin:mcppass"), // update with .env or prompt in production
  "Content-Type": "application/json"
};

export async function listChats() {
  const res = await fetch(BASE_URL, {
    method: "POST",
    headers: authHeader,
    body: JSON.stringify({
      tool: "list_chats",
      params: { limit: 10, include_last_message: true }
    })
  });
  return await res.json();
}

export async function listMessages(chat_jid) {
  const res = await fetch(BASE_URL, {
    method: "POST",
    headers: authHeader,
    body: JSON.stringify({
      tool: "list_messages",
      params: { chat_jid }
    })
  });
  return await res.json();
}

export async function sendMessage(recipient, message) {
  const res = await fetch(BASE_URL, {
    method: "POST",
    headers: authHeader,
    body: JSON.stringify({
      tool: "send_message",
      params: { recipient, message }
    })
  });
  return await res.json();
}
