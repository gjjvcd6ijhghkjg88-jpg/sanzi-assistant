// 作用：应用主组件，组织头部、问答区和资料来源区，并维护终端模式。

import { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { Header } from './components/Header';
import { SourcePanel } from './components/SourcePanel';
import { useChat } from './hooks/useChat';
import type { Platform } from './types';

export default function App() {
  const [platform, setPlatform] = useState<Platform>('pc');
  const chat = useChat(platform);

  return (
    <main className={`app-shell ${platform}`}>
      <Header platform={platform} onPlatformChange={setPlatform} />
      <div className="workspace">
        <ChatPanel
          messages={chat.messages}
          isLoading={chat.isLoading}
          error={chat.error}
          onSubmit={chat.submit}
        />
        <SourcePanel message={chat.latestAssistantMessage} />
      </div>
    </main>
  );
}
