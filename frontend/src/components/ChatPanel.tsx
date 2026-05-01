// 作用：渲染聊天消息、输入框、发送按钮和推荐追问入口。

import { FormEvent, useState } from 'react';
import { Loader2, SendHorizontal } from 'lucide-react';
import type { ChatMessage } from '../types';

type ChatPanelProps = {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string;
  onSubmit: (question: string) => void;
};

export function ChatPanel({ messages, isLoading, error, onSubmit }: ChatPanelProps) {
  const [input, setInput] = useState('');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(input);
    setInput('');
  }

  return (
    <section className="chat-panel" aria-label="智能问答">
      <div className="message-list">
        {messages.map((message) => (
          <article className={`message ${message.role}`} key={message.id}>
            <div className="message-label">{message.role === 'user' ? '我' : '助手'}</div>
            <div className="message-bubble">
              {message.content.split('\n').map((line) => (
                <p key={line}>{line}</p>
              ))}
              {message.mode === 'local_fallback' && (
                <span className="mode-badge">本地知识库回答</span>
              )}
              {message.suggestions && (
                <div className="suggestions">
                  {message.suggestions.map((suggestion) => (
                    <button type="button" key={suggestion} onClick={() => onSubmit(suggestion)}>
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </article>
        ))}
        {isLoading && (
          <article className="message assistant">
            <div className="message-label">助手</div>
            <div className="message-bubble loading-line">
              <Loader2 size={18} className="spin" />
              正在检索资料并组织回答
            </div>
          </article>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          value={input}
          rows={2}
          maxLength={500}
          onChange={(event) => setInput(event.target.value)}
          placeholder="输入三资管理相关问题，例如：村集体资金支出怎么审批？"
        />
        <button type="submit" disabled={!input.trim() || isLoading} title="发送问题">
          <SendHorizontal size={20} />
        </button>
      </form>
    </section>
  );
}

