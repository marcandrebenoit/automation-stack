export default function MessageList({ messages }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 bg-white">
      {messages.map((msg, i) => (
        <div key={i} className="mb-4">
          <div className="text-xs text-gray-500 mb-1">
            {msg.sender_name || msg.sender_phone_number || "Unknown"} —{" "}
            {new Date(msg.timestamp).toLocaleString()}
          </div>
          <div className="bg-gray-100 rounded p-2">
            {msg.text ? msg.text : <i className="text-gray-400">(No text)</i>}
          </div>
        </div>
      ))}
    </div>
  );
}
