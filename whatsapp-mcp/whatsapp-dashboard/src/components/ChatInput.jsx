import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim()) {
      onSend(text);
      setText("");
    }
  };

  return (
    <div className="p-4 border-t flex">
      <input
        className="flex-1 border px-3 py-2 rounded"
        placeholder="Type your message..."
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => e.key === "Enter" && handleSend()}
      />
      <button
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded"
        onClick={handleSend}
      >
        Send
      </button>
    </div>
  );
}
