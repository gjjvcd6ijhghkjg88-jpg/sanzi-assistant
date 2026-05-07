// 作用：定义前端和后端共享的问答数据类型，减少接口字段误用。
// 注：本文件是手写的业务类型；从 OpenAPI 自动生成的严格类型见 src/types/api.d.ts。

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

export type ErrorCode = 'validation_error' | 'not_found' | 'upstream_error' | 'internal_error';

export type ErrorPayload = {
  code: ErrorCode;
  message: string;
  trace_id: string;
  details?: Record<string, unknown> | null;
};

export type StreamEvent =
  | { event: 'meta'; data: { trace_id: string } }
  | { event: 'sources'; data: Source[] }
  | { event: 'delta'; data: { text: string } }
  | { event: 'suggestions'; data: string[] }
  | { event: 'done'; data: { mode: AskResponse['mode'] } }
  | { event: 'error'; data: ErrorPayload };
