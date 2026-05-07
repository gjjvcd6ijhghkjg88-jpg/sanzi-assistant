// 作用：管理问答消息流、加载状态、错误状态和推荐追问提交逻辑。

import { useMemo, useState } from 'react';
import { askQuestion } from '../api/client';
import type { ChatMessage, Platform } from '../types';

const initialMessages: ChatMessage[] = [
  {
    id: 'welcome',
    role: 'assistant',
    content:
      '你好，我是三资管理助手。你可以问我资金支出、资产处置、资源发包、平台录入和公开公示相关问题。',
    suggestions: ['村集体资金支出怎么审批？', '资源发包要准备哪些材料？', '平台归档需要上传什么？'],
  },
];

function createId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function useChat(platform: Platform) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const latestAssistantMessage = useMemo(
    () => [...messages].reverse().find((message) => message.role === 'assistant'),
    [messages],
  );

  async function submit(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError('');
    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: createId('user'),
      role: 'user',
      content: trimmed,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const result = await askQuestion({
        question: trimmed,
        platform,
        session_id: 'local-demo-session',
      });

      const assistantMessage: ChatMessage = {
        id: result.trace_id,
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
        suggestions: result.suggestions,
        mode: result.mode,
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '请求失败，请稍后重试。');
    } finally {
      setIsLoading(false);
    }
  }

  return {
    messages,
    isLoading,
    error,
    latestAssistantMessage,
    submit,
  };
}
