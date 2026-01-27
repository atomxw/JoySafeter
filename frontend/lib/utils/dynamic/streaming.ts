/**
 * Streaming utilities
 * Helper functions for handling streaming responses
 */

import type { StreamingEvent } from '@/types/dynamic/tool';

/**
 * Parse SSE (Server-Sent Events) stream
 */
export const parseSSEStream = async function* (
  response: Response
): AsyncGenerator<StreamingEvent> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error('Response body is not readable');

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data as StreamingEvent;
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    }

    if (buffer) {
      if (buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.slice(6));
          yield data as StreamingEvent;
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
};

/**
 * Accumulate chunks into complete message
 */
export const accumulateChunks = (chunks: string[]): string => {
  return chunks.join('');
};

/**
 * Format streaming event for display
 */
export const formatStreamingEvent = (event: StreamingEvent): string => {
  switch (event.type) {
    case 'thinking':
      return `💭 Thinking: ${event.data}`;
    case 'tool_call':
      return `🔧 Tool Call: ${JSON.stringify(event.data)}`;
    case 'tool_result':
      return `✅ Tool Result: ${JSON.stringify(event.data)}`;
    case 'message_chunk':
      return event.data as string;
    case 'complete':
      return '✓ Complete';
    case 'error':
      return `❌ Error: ${JSON.stringify(event.data)}`;
    default:
      return JSON.stringify(event);
  }
};

/**
 * Detect if event is error
 */
export const isErrorEvent = (event: StreamingEvent): boolean => {
  return event.type === 'error';
};

/**
 * Detect if event is complete
 */
export const isCompleteEvent = (event: StreamingEvent): boolean => {
  return event.type === 'complete';
};
