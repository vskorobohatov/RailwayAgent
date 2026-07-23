import { ListEventsResponse, ListTasksResponse, ReportResponse, SseEvent, TaskStatus } from '../types';

const BASE_URL = '/api';

export interface SubmitTaskResponse {
  task_id: string;
}

export async function submitEvent(text: string): Promise<SubmitTaskResponse> {
  const response = await fetch(`${BASE_URL}/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
    throw new Error(error.detail || 'Неизвестная ошибка');
  }

  return response.json();
}

export async function getTaskStatus(task_id: string): Promise<TaskStatus> {
  const response = await fetch(`${BASE_URL}/tasks/${task_id}`);

  if (!response.ok) {
    throw new Error('Не удалось получить статус задачи');
  }

  return response.json();
}

export async function getEvents(): Promise<ListEventsResponse> {
  const response = await fetch(`${BASE_URL}/events`);

  if (!response.ok) {
    throw new Error('Не удалось загрузить события');
  }

  return response.json();
}

export async function generateReport(): Promise<ReportResponse> {
  const response = await fetch(`${BASE_URL}/reports`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
    throw new Error(error.detail || 'Неизвестная ошибка');
  }

  return response.json();
}

export async function generateReportStream(
  onEvent: (event: SseEvent) => void,
): Promise<void> {
  const response = await fetch(`${BASE_URL}/reports/stream`);

  if (!response.ok) {
    throw new Error('Не удалось начать генерацию отчёта');
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Поток недоступен');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE lines from buffer
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep last incomplete line

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent(data);
        } catch {
          // Skip malformed SSE data lines
        }
      }
    }
  }

  // Process any remaining buffer
  if (buffer.startsWith('data: ')) {
    try {
      const data = JSON.parse(buffer.slice(6));
      onEvent(data);
    } catch {
      // Skip malformed SSE data lines
    }
  }
}

export async function listTasks(): Promise<ListTasksResponse> {
  const response = await fetch(`${BASE_URL}/tasks`);
  if (!response.ok) throw new Error('Не удалось загрузить задачи');
  return response.json();
}

export async function cancelTask(task_id: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/tasks/${task_id}/cancel`, { method: 'POST' });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Ошибка');
  }
}

export async function retryTask(task_id: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/tasks/${task_id}/retry`, { method: 'POST' });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Ошибка');
  }
}
