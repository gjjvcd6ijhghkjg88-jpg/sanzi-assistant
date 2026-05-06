// 作用：封装后端 API 请求。同源相对路径由 Vite proxy 转发，避免跨域；流式接口使用 fetch + ReadableStream 消费 SSE。

import type { AskRequest, AskResponse, ErrorPayload, Source, StreamEvent } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

function url(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export class ApiError extends Error {
  code: ErrorPayload['code'];
  traceId: string;
  status: number;
  details?: ErrorPayload['details'];

  constructor(status: number, payload: ErrorPayload) {
    super(payload.message);
    this.code = payload.code;
    this.traceId = payload.trace_id;
    this.status = status;
    this.details = payload.details;
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let payload: ErrorPayload;
  try {
    payload = (await response.json()) as ErrorPayload;
  } catch {
    payload = {
      code: 'internal_error',
      message: '问答服务暂时不可用，请稍后重试。',
      trace_id: '',
    };
  }
  return new ApiError(response.status, payload);
}

export async function askQuestion(payload: AskRequest, signal?: AbortSignal): Promise<AskResponse> {
  const response = await fetch(url('/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return response.json() as Promise<AskResponse>;
}

export type StreamHandlers = {
  onMeta?: (traceId: string) => void;
  onSources?: (sources: Source[]) => void;
  onDelta?: (text: string) => void;
  onSuggestions?: (suggestions: string[]) => void;
  onDone?: (mode: AskResponse['mode']) => void;
  onError?: (error: ApiError) => void;
};

/**
 * 以 SSE 方式消费 /chat/stream。内部用 fetch + ReadableStream 按行解析 `event:` / `data:`，
 * 保证在 proxy/网关下也能稳定工作（比 EventSource 更可控，且原生支持 POST body）。
 */
export async function askQuestionStream(
  payload: AskRequest,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(url('/chat/stream'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok || !response.body) {
    const error = !response.ok
      ? await parseError(response)
      : new ApiError(response.status, {
          code: 'internal_error',
          message: '流式响应不可用。',
          trace_id: '',
        });
    handlers.onError?.(error);
    throw error;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      dispatchEvent(rawEvent, handlers);
      boundary = buffer.indexOf('\n\n');
    }
  }

  if (buffer.trim()) {
    dispatchEvent(buffer, handlers);
  }
}

function dispatchEvent(raw: string, handlers: StreamHandlers): void {
  let eventName = 'message';
  const dataLines: string[] = [];

  for (const line of raw.split('\n')) {
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  }

  if (dataLines.length === 0) {
    return;
  }

  let data: unknown;
  try {
    data = JSON.parse(dataLines.join('\n'));
  } catch {
    return;
  }

  const event = { event: eventName, data } as StreamEvent;
  switch (event.event) {
    case 'meta':
      handlers.onMeta?.((event.data as { trace_id: string }).trace_id);
      break;
    case 'sources':
      handlers.onSources?.(event.data as Source[]);
      break;
    case 'delta':
      handlers.onDelta?.((event.data as { text: string }).text);
      break;
    case 'suggestions':
      handlers.onSuggestions?.(event.data as string[]);
      break;
    case 'done':
      handlers.onDone?.((event.data as { mode: AskResponse['mode'] }).mode);
      break;
    case 'error': {
      const payload = event.data as ErrorPayload;
      handlers.onError?.(new ApiError(200, payload));
      break;
    }
  }
}
