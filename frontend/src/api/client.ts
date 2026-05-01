// 作用：封装后端 API 请求，集中处理基础地址和错误信息。

import type { AskRequest, AskResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/qa/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error('问答服务暂时不可用，请稍后重试。');
  }

  return response.json() as Promise<AskResponse>;
}

