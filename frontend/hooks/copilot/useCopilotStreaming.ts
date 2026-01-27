/**
 * useCopilotStreaming - Hook for managing Copilot streaming state
 */

import { useState, useRef } from 'react'

export type StageType = 'thinking' | 'processing' | 'generating'

export function useCopilotStreaming() {
  const [streamingContent, setStreamingContent] = useState('')
  const [currentStage, setCurrentStage] = useState<{ stage: StageType; message: string } | null>(null)
  const [currentToolCall, setCurrentToolCall] = useState<{ tool: string; input: Record<string, unknown> } | null>(null)
  const [toolResults, setToolResults] = useState<Array<{ type: string; payload: Record<string, unknown>; reasoning?: string }>>([])
  const [expandedToolTypes, setExpandedToolTypes] = useState<Set<string>>(new Set())
  const [copiedStreaming, setCopiedStreaming] = useState(false)
  const streamingContentRef = useRef<HTMLDivElement>(null)

  const appendContent = (content: string) => {
    setStreamingContent((prev) => {
      const normalizedContent = content.replace(/\n{2,}/g, '\n')
      let newContent: string
      if (prev.endsWith('\n') && normalizedContent.startsWith('\n')) {
        newContent = prev + normalizedContent.replace(/^\n+/, '')
      } else {
        newContent = prev + normalizedContent
      }
      return newContent.replace(/\n{2,}/g, '\n')
    })
  }

  const addToolResult = (action: { type: string; payload: Record<string, unknown>; reasoning?: string }) => {
    setCurrentToolCall(null)
    setToolResults((prev) => [...prev, action])
  }

  const clearStreaming = () => {
    setStreamingContent('')
    setCurrentStage(null)
    setCurrentToolCall(null)
    setToolResults([])
    setExpandedToolTypes(new Set())
  }

  const toggleToolType = (type: string) => {
    setExpandedToolTypes((prev) => {
      const next = new Set(prev)
      if (next.has(type)) {
        next.delete(type)
      } else {
        next.add(type)
      }
      return next
    })
  }

  return {
    streamingContent,
    currentStage,
    currentToolCall,
    toolResults,
    expandedToolTypes,
    copiedStreaming,
    streamingContentRef,
    setStreamingContent,
    setCurrentStage,
    setCurrentToolCall,
    addToolResult,
    appendContent,
    clearStreaming,
    toggleToolType,
    setCopiedStreaming,
    setToolResults,
  }
}
