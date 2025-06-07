export default function ChatList({ chats, onSelect }) {
  return (
    <div className="w-1/3 border-r overflow-y-auto bg-gray-50">
      <h2 className="text-xl font-bold p-4">Chats</h2>
      {chats.map(chat => (
        <div
          key={chat.jid}
          onClick={() => onSelect(chat)}
          className="p-4 cursor-pointer hover:bg-gray-200 border-b"
        >
          <div className="font-semibold">{chat.name || chat.jid}</div>
          <div className="text-sm text-gray-600 truncate">
            {chat.last_message}
          </div>
        </div>
      ))}
    </div>
  );
}
