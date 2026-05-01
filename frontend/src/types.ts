// 作用：定义前端和后端共享的问答数据类型，减少接口字段误用。

export type Platform = 'pc' | 'mobile';

export type Source = {
  id: string;
  title: string;
  category: string;
  excerpt: string;
};

export type AskRequest = {
  question: string;
  platform: Platform;
  session_id?: string;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
  suggestions: string[];
  trace_id: string;
  mode: 'llm' | 'local_fallback';
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  suggestions?: string[];
  mode?: AskResponse['mode'];
};

