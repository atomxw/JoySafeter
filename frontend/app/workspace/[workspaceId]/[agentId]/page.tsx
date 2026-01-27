'use client'

import AgentBuilder from './AgentBuilder'

/**
 * Agent 详情页
 *
 * 这是 agent 的主页面，用于显示和编辑 agent 配置
 *
 * 路由: /workspace/[workspaceId]/[agentId]
 */
export default function AgentPage() {
  return <AgentBuilder />
}
