import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, MessageSquare } from 'lucide-react';
import DataTable from './DataTable';
import './App.css';
import PieChartComponent from './PieChartComponent';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Robust Python to JSON converter using character-by-character parsing
  const pythonToJSON = (pythonStr) => {
    try {
      let result = pythonStr;

      // Step 1: Replace Python datetime objects with ISO strings
      const datetimePattern = /datetime\.datetime\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2}),\s*(\d{1,2}),\s*(\d{1,2}),\s*(\d{1,2}),\s*(\d+),\s*tzinfo=datetime\.timezone\.utc\)/g;
      result = result.replace(datetimePattern, (match, year, month, day, hour, minute, second, microsecond) => {
        const m = month.padStart(2, '0');
        const d = day.padStart(2, '0');
        const h = hour.padStart(2, '0');
        const min = minute.padStart(2, '0');
        const s = second.padStart(2, '0');
        const ms = microsecond.padStart(6, '0').slice(0, 3);
        return `"${year}-${m}-${d}T${h}:${min}:${s}.${ms}Z"`;
      });

      // Step 2: Replace Python boolean and null values
      result = result.replace(/\bTrue\b/g, 'true');
      result = result.replace(/\bFalse\b/g, 'false');
      result = result.replace(/\bNone\b/g, 'null');

      // Step 3: Convert all single quotes to double quotes
      // This is the most robust approach - just replace ALL single quotes with double quotes
      // But we need to be careful with single quotes inside strings

      let inString = false;
      let stringChar = null;
      let output = '';
      let i = 0;

      while (i < result.length) {
        const char = result[i];
        const nextChar = result[i + 1];

        // Handle escape sequences
        if (char === '\\' && inString) {
          output += char;
          if (nextChar) {
            output += nextChar;
            i += 2;
            continue;
          }
        }

        // Handle quotes
        if ((char === '"' || char === "'") && result[i - 1] !== '\\') {
          if (!inString) {
            // Starting a string
            inString = true;
            stringChar = char;
            output += '"'; // Always use double quotes in JSON
          } else if (char === stringChar) {
            // Ending a string
            inString = false;
            stringChar = null;
            output += '"'; // Always use double quotes in JSON
          } else {
            // It's a different quote inside a string - escape it
            if (char === '"') {
              output += '\\"';
            } else {
              output += char;
            }
          }
        } else {
          output += char;
        }

        i++;
      }

      result = output;

      // Step 4: Parse the cleaned JSON
      const parsed = JSON.parse(result);
      return parsed;

    } catch (error) {
      console.error('Error in pythonToJSON:', error);
      console.log('Original string (first 1000 chars):', pythonStr.substring(0, 1000));
      console.log('Processed string (first 1000 chars):', result?.substring(0, 1000));
      return null;
    }
  };

  // Helper function to detect if content is table data
  const isTableData = (content) => {
    if (!content) return false;

    // Check if it's already a parsed array of objects
    if (Array.isArray(content) && content.length > 0 && typeof content[0] === 'object') {
      return true;
    }

    if (typeof content === 'object') {
      return Array.isArray(content) && content.length > 0 && typeof content[0] === 'object';
    }

    if (typeof content === 'string') {
      const trimmed = content.trim();
      if (trimmed.startsWith('[{') && (trimmed.includes('datetime.datetime') || trimmed.includes("'id':"))) {
        return true;
      }
    }

    return false;
  };
const isPieChartData = (content) => {
  return content.chart_type === 'pie' && Array.isArray(content.data);
};
  // Helper function to parse table data
  const parseTableData = (content) => {
    if (typeof content === 'object' && Array.isArray(content)) {
      return content;
    }

    if (typeof content === 'string') {
      try {
        const parsed = pythonToJSON(content);
        return parsed;
      } catch (error) {
        console.error('Error parsing table data:', error);
        return null;
      }
    }

    return null;
  };

  // Replace renderMessageContent with:
  const renderMessageContent = (msg) => {
      if (isPieChartData(msg.content)) {
    return (
      <PieChartComponent item={msg.content} />

    );
  }
    if (Array.isArray(msg.content) && msg.content.length && typeof msg.content[0] === 'string') {
      return (
        <ul className="string-list">
          {msg.content.map((str, idx) => (
            <li key={idx} className="string-list-item">{str}</li>
          ))}
        </ul>
      )
    }

    // Fallback: comma-separated plain string -> list
    if (
      typeof msg.content === 'string' &&
      msg.content.includes(',') &&
      !msg.content.includes('<') // avoid splitting HTML
    ) {
      const parts = msg.content.split(',').map(s => s.trim()).filter(Boolean);
      if (parts.length > 1) {
        return (
          <ul className="string-list">
            {parts.map((str, idx) => (
              <li key={idx} className="string-list-item">{str}</li>
            ))}
          </ul>
        )
      }
    }

    // Table detection
    if (isTableData(msg.content)) {
      const data = parseTableData(msg.content);
      if (data) {
        return <DataTable data={data} />;
      }
    }

    // Default paragraph
    return (
      <p
        className="leading-relaxed whitespace-pre-wrap"
        dangerouslySetInnerHTML={{ __html: msg.content }}
      />
    );
  };

  const handleSubmit = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const requestBody = {
        question: userMessage
      };

      if (threadId) {
        requestBody.thread_id = threadId;
      }

      const response = await fetch('http://127.0.0.1:8080/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.thread_id) {
        setThreadId(data.thread_id);
      }

      // Check if response contains table data
      let assistantMessage;
      let messageData = null;

      if (data.data && Array.isArray(data.data)) {
        // API returns data in separate property
        assistantMessage = data.answer || 'Here is the data:';
        messageData = data.data;
      } else if (isTableData(data.answer || data.response)) {
        // API returns stringified/Python representation in answer
        assistantMessage = data.answer || data.response;
      } else {
        // Regular text response
        assistantMessage = data.answer || data.response || JSON.stringify(data);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: assistantMessage,
        data: messageData
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
      console.error('API Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-blue-50 to-slate-200 flex">

      {/* Sidebar */}
      <div className="w-1/4 bg-white border-r border-slate-200 flex flex-col shadow-lg">
        <div className="p-6 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-md">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">AI Assistant</h1>
              <p className="text-sm text-slate-500">Powered by AI</p>
            </div>
          </div>
          <button className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all shadow-md hover:shadow-lg font-medium">
            + New Conversation
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-100 cursor-pointer hover:bg-blue-100 transition-colors">
              <p className="text-sm font-medium text-slate-800 truncate">Current Conversation</p>
              <p className="text-xs text-slate-500 mt-1">Active now</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-slate-200">
          <p className="text-xs text-slate-400 text-center">Thread ID: {threadId || 'Not started'}</p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">

        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5 shadow-sm">
          <div className="mx-auto flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Chat Assistant</h2>
              <p className="text-sm text-slate-500 mt-1">Ask me anything</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-600 font-medium">Online</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-50 to-blue-50">
          <div className="mx-auto px-8 py-8 space-y-6 max-w-[1600px]">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-in slide-in-from-bottom duration-300`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-br from-slate-600 to-slate-700'
                    : 'bg-gradient-to-br from-blue-500 to-cyan-500'
                }`}>
                  {msg.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>

                <div className={`flex-1 min-w-0 ${msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
                  <div
                    className={`p-4 rounded-2xl shadow-sm ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-slate-600 to-slate-700 text-white max-w-[600px]'
                        : 'bg-white text-slate-800 border border-slate-200'
                    }`}
                    style={msg.role === 'assistant' ? { maxWidth: '95%' } : {}}
                  >
                    {isTableData(msg.content) ? (
                      <div className="overflow-x-auto">
                        {renderMessageContent(msg)}
                      </div>
                    ) : (
                      renderMessageContent(msg)
                    )}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-4 animate-in slide-in-from-bottom duration-300">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-md">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-slate-200 px-8 py-6 shadow-lg">
          <div className="mx-auto">
            <div className="flex gap-4 items-end">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message... (Shift+Enter for new line)"
                  disabled={loading}
                  rows={1}
                  className="w-full px-6 py-4 bg-slate-50 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:opacity-50 disabled:bg-slate-100 transition-all resize-none overflow-hidden"
                  style={{
                    minHeight: '56px',
                    maxHeight: '200px',
                    height: 'auto'
                  }}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
                  }}
                />
              </div>
              <button
                onClick={handleSubmit}
                disabled={!input.trim() || loading}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-slate-400 disabled:to-slate-500 transition-all shadow-md hover:shadow-lg hover:scale-105 active:scale-95 flex items-center gap-2 font-semibold flex-shrink-0"
              >
                <Send className="w-5 h-5" />
                <span>Send</span>
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-3 text-center">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}