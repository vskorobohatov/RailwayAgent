export interface DatabaseEvent {
  id: number;
  __table__: string;
  [key: string]: unknown;
}

export interface AddEventResponse {
  message: string;
  saved: Array<{ table: string; id: number }>;
  count: number;
}

export interface ListEventsResponse {
  events: DatabaseEvent[];
  count: number;
}

export interface ReportResponse {
  content: string;
  file_path: string;
}

export interface SseEvent {
  step: string;
  message: string;
  content?: string;
  file_path?: string;
}

export type TaskState = 'pending' | 'processing' | 'classifying' | 'saving' | 'completed' | 'failed' | 'cancelled';

export interface TaskStatus {
  task_id: string;
  status: TaskState;
  step: string;
  result: { message: string; count: number } | null;
  error: string | null;
}

export interface QueueTask {
  id: string;
  input_text: string;
  status: string;
  step: string;
  result: unknown;
  error: string | null;
  created_at: string;
}

export interface ListTasksResponse {
  tasks: QueueTask[];
  count: number;
}
