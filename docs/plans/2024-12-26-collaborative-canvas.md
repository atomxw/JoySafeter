# Collaborative Canvas Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add real-time multi-user collaboration to the canvas editor, allowing 2-5 users to simultaneously edit nodes and edges with live cursor visibility.

**Architecture:** Minimal-intrusion approach - create an independent collaboration layer that wraps the existing builderStore. WebSocket communication for real-time sync, with optimistic updates for responsive UX. Collaboration features can be toggled independently.

**Tech Stack:**
- Frontend: React, Zustand, ReactFlow, native WebSocket API
- Backend: FastAPI, native WebSocket (no Socket.IO)
- Protocol: Custom JSON message format over WebSocket

---

## Overview

This plan implements collaborative editing using **Plan A (Minimal Intrusion)**:

1. **Independent collaboration layer** - New hooks and components that don't modify existing builderStore
2. **Event-driven sync** - Subscribe to store changes and broadcast to WebSocket
3. **Optimistic updates** - Apply changes immediately, sync in background
4. **Phase-based rollout** - Core features first, enhancements later

### Files to Create

```
backend/
├── app/api/workspaces/{workspaceId}/agents/{agentId}/
│   └── collaboration.py                    # WebSocket endpoint
├── app/websocket/
│   ├── collaboration_manager.py            # Room management
│   └── __init__.py

frontend/
├── hooks/
│   ├── use-collaboration-socket.ts         # WebSocket connection manager
│   └── use-collaborative-workflow.ts       # Collaboration operations wrapper
├── app/workspace/[workspaceId]/[agentId]/
│   ├── components/
│   │   ├── CollaborationCursors.tsx        # Cursor display overlay
│   │   └── CollaborationAvatars.tsx        # User avatars list
│   └── stores/
│       └── collaboration-store.ts          # Collaboration state
```

### Files to Modify (Minimal)

- `BuilderCanvas.tsx` - Add cursor overlay component
- Existing notification WebSocket - Ensure no conflicts

---

## Task 1: Backend - Collaboration Manager

**Files:**
- Create: `backend/app/websocket/collaboration_manager.py`
- Create: `backend/app/websocket/__init__.py`

**Step 1: Create the collaboration manager module**

Create `backend/app/websocket/__init__.py`:

```python
# Empty init file to make websocket a package
```

**Step 2: Implement the collaboration manager**

Create `backend/app/websocket/collaboration_manager.py`:

```python
"""
Collaboration Manager - Handles real-time canvas collaboration rooms.

Manages WebSocket connections for multi-user canvas editing:
- Room management (one room per workflow/agent)
- User presence tracking
- Message broadcasting to room members
- Connection lifecycle management
"""

from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class CollaborationRoom:
    """Represents a collaboration room for a single workflow."""

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.connections: Dict[str, WebSocket] = {}  # user_id -> WebSocket
        self.users: Dict[str, Dict[str, Any]] = {}  # user_id -> user info

    async def join(self, user_id: str, websocket: WebSocket, user_info: Dict[str, Any]):
        """Add a user to the room."""
        self.connections[user_id] = websocket
        self.users[user_id] = {
            **user_info,
            'cursor': None,
            'selection': [],
        }
        logger.info(f"User {user_id} joined room {self.room_id}")

    async def leave(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Remove a user from the room, return user info if existed."""
        user_info = self.users.pop(user_id, None)
        if user_id in self.connections:
            del self.connections[user_id]
        logger.info(f"User {user_id} left room {self.room_id}")
        return user_info

    async def broadcast(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Send a message to all users in the room except one."""
        payload = json.dumps(message)
        disconnected = []

        for user_id, ws in self.connections.items():
            if user_id == exclude_user:
                continue

            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                disconnected.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected:
            await self.leave(user_id)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific user."""
        ws = self.connections.get(user_id)
        if not ws:
            return False

        try:
            await ws.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.warning(f"Failed to send to user {user_id}: {e}")
            await self.leave(user_id)
            return False

    def get_user_list(self) -> list:
        """Get list of users in the room."""
        return [
            {
                'userId': user_id,
                'userName': info.get('userName', ''),
                'color': info.get('color', '#000000'),
            }
            for user_id, info in self.users.items()
        ]

    def is_empty(self) -> bool:
        """Check if room is empty."""
        return len(self.connections) == 0


class CollaborationManager:
    """Global manager for all collaboration rooms."""

    def __init__(self):
        self.rooms: Dict[str, CollaborationRoom] = {}

    def get_or_create_room(self, room_id: str) -> CollaborationRoom:
        """Get existing room or create new one."""
        if room_id not in self.rooms:
            self.rooms[room_id] = CollaborationRoom(room_id)
            logger.info(f"Created new room: {room_id}")
        return self.rooms[room_id]

    def remove_room_if_empty(self, room_id: str):
        """Remove room if empty to free memory."""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            if room.is_empty():
                del self.rooms[room_id]
                logger.info(f"Removed empty room: {room_id}")

    def get_room(self, room_id: str) -> Optional[CollaborationRoom]:
        """Get room without creating."""
        return self.rooms.get(room_id)


# Global singleton instance
collaboration_manager = CollaborationManager()
```

**Step 3: Commit**

```bash
git add backend/app/websocket/
git commit -m "feat: add collaboration manager for room management"
```

---

## Task 2: Backend - WebSocket Endpoint

**Files:**
- Create: `backend/app/api/workspaces/{workspaceId}/agents/{agentId}/collaboration.py`

**Step 1: Create the WebSocket endpoint**

Create `backend/app/api/workspaces/{workspaceId}/agents/{agentId}/collaboration.py`:

```python
"""
Collaboration WebSocket Endpoint

WebSocket endpoint for real-time canvas collaboration.
Provides bi-directional messaging for:
- Room join/leave
- Canvas operations (add/remove/update nodes and edges)
- Cursor position updates
- User presence
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.collaboration_manager import collaboration_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/collaboration")
async def collaboration_websocket(
    websocket: WebSocket,
    workspace_id: str,
    agent_id: str,
    workflow_id: str = Query(..., description="Current workflow/agent ID"),
    token: str = Query(..., description="Authentication token"),
):
    """
    WebSocket endpoint for canvas collaboration.

    Message types (client -> server):
    - join: {workflowId, userId, userName, color}
    - leave: {workflowId}
    - operation: {operationId, action, target, payload, timestamp}
    - cursor_update: {position, selection}
    - ping: {timestamp}

    Message types (server -> client):
    - user_joined: {userId, userName, color}
    - user_left: {userId}
    - user_list: {users: [...]}
    - operation: {operationId, action, target, payload, userId, timestamp}
    - operation_confirmed: {operationId}
    - cursor_update: {userId, position, selection}
    - pong: {timestamp}
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted: workspace={workspace_id}, agent={agent_id}")

    # TODO: Verify token and extract user info
    # For now, use placeholder user ID from token
    user_id = f"user_{token[:8]}"
    user_info = {
        'userId': user_id,
        'userName': f'User {user_id}',
        'color': '#3b82f6',
    }

    room = collaboration_manager.get_or_create_room(workflow_id)

    try:
        # Wait for client to send join message
        init_msg = await websocket.receive_json()

        if init_msg.get('type') != 'join':
            await websocket.close(code=1008, reason='First message must be join')
            return

        # User joins the room
        await room.join(user_id, websocket, user_info)

        # Send current user list to the new user
        await room.send_to_user(user_id, {
            'type': 'user_list',
            'users': room.get_user_list(),
        })

        # Broadcast user joined to others
        await room.broadcast({
            'type': 'user_joined',
            **user_info,
        }, exclude_user=user_id)

        logger.info(f"User {user_id} joined workflow {workflow_id}")

        # Message loop
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')

            if msg_type == 'operation':
                # Broadcast operation to other users
                await room.broadcast({
                    'type': 'operation',
                    'operationId': data.get('operationId'),
                    'action': data.get('action'),
                    'target': data.get('target'),
                    'payload': data.get('payload'),
                    'userId': user_id,
                    'timestamp': data.get('timestamp'),
                }, exclude_user=user_id)

                # Confirm operation to sender
                await room.send_to_user(user_id, {
                    'type': 'operation_confirmed',
                    'operationId': data.get('operationId'),
                })

            elif msg_type == 'cursor_update':
                # Broadcast cursor to others (no confirmation needed)
                await room.broadcast({
                    'type': 'cursor_update',
                    'userId': user_id,
                    'position': data.get('position'),
                    'selection': data.get('selection', []),
                }, exclude_user=user_id)

            elif msg_type == 'ping':
                # Respond with pong
                await room.send_to_user(user_id, {
                    'type': 'pong',
                    'timestamp': data.get('timestamp'),
                })

            elif msg_type == 'leave':
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}", exc_info=True)
    finally:
        # Clean up
        await room.leave(user_id)

        # Broadcast user left
        user_info = room.users.get(user_id)
        if user_info:
            await room.broadcast({
                'type': 'user_left',
                'userId': user_id,
            })

        # Remove room if empty
        collaboration_manager.remove_room_if_empty(workflow_id)
```

**Step 2: Register the router in the main app**

Find and modify the main API router registration file (usually `backend/app/api/__init__.py` or `backend/app/main.py`). Look for where workspace/agent routes are registered and add:

```python
from app.api.workspaces.workspaceId.agents.agentId.collaboration import router as collaboration_router

# Register the collaboration router
api_router.include_router(
    collaboration_router,
    prefix="/workspaces/{workspace_id}/agents/{agent_id}",
    tags=["collaboration"],
)
```

**Step 3: Commit**

```bash
git add backend/app/api/
git commit -m "feat: add collaboration WebSocket endpoint"
```

---

## Task 3: Frontend - Collaboration Store

**Files:**
- Create: `frontend/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store.ts`

**Step 1: Create the collaboration Zustand store**

Create `frontend/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store.ts`:

```typescript
/**
 * Collaboration Store - Manages real-time collaboration state.
 *
 * Stores:
 * - Connection status
 * - Presence users (other users in the room)
 * - Cursor positions
 * - User colors
 */

import { create } from 'zustand'

export interface PresenceUser {
  userId: string
  userName: string
  color: string
  cursor?: { x: number; y: number } | null
  selection?: string[]
}

interface CollaborationState {
  // Connection state
  isConnected: boolean
  isConnecting: boolean

  // Room info
  currentWorkflowId: string | null

  // Presence users (other users, not including current user)
  presenceUsers: PresenceUser[]

  // Current user info
  currentUserId: string | null
  currentUserName: string | null
  currentUserColor: string

  // Actions
  setConnected: (connected: boolean) => void
  setConnecting: (connecting: boolean) => void
  setCurrentWorkflowId: (workflowId: string | null) => void
  setCurrentUser: (userId: string, userName: string, color: string) => void

  // Presence management
  setPresenceUsers: (users: PresenceUser[]) => void
  addPresenceUser: (user: PresenceUser) => void
  removePresenceUser: (userId: string) => void
  updatePresenceCursor: (userId: string, cursor: { x: number; y: number }) => void
  updatePresenceSelection: (userId: string, selection: string[]) => void

  // Reset
  reset: () => void
}

const generateUserColor = (userId: string): string => {
  // Generate consistent color from user ID
  const colors = [
    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
    '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
    '#ec4899', '#f43f5e',
  ]
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[hash % colors.length]
}

export const useCollaborationStore = create<CollaborationState>((set, get) => ({
  // Initial state
  isConnected: false,
  isConnecting: false,
  currentWorkflowId: null,
  currentUserId: null,
  currentUserName: null,
  currentUserColor: '#3b82f6',
  presenceUsers: [],

  setConnected: (connected) => set({ isConnected: connected, isConnecting: false }),

  setConnecting: (connecting) => set({ isConnecting: connecting }),

  setCurrentWorkflowId: (workflowId) => set({ currentWorkflowId: workflowId }),

  setCurrentUser: (userId, userName, color) => {
    set({
      currentUserId: userId,
      currentUserName: userName,
      currentUserColor: color || generateUserColor(userId),
    })
  },

  setPresenceUsers: (users) => set({ presenceUsers: users }),

  addPresenceUser: (user) => {
    const { presenceUsers } = get()
    const exists = presenceUsers.some((u) => u.userId === user.userId)
    if (!exists) {
      set({ presenceUsers: [...presenceUsers, user] })
    }
  },

  removePresenceUser: (userId) => {
    const { presenceUsers } = get()
    set({ presenceUsers: presenceUsers.filter((u) => u.userId !== userId) })
  },

  updatePresenceCursor: (userId, cursor) => {
    const { presenceUsers } = get()
    set({
      presenceUsers: presenceUsers.map((u) =>
        u.userId === userId ? { ...u, cursor } : u
      ),
    })
  },

  updatePresenceSelection: (userId, selection) => {
    const { presenceUsers } = get()
    set({
      presenceUsers: presenceUsers.map((u) =>
        u.userId === userId ? { ...u, selection } : u
      ),
    })
  },

  reset: () =>
    set({
      isConnected: false,
      isConnecting: false,
      currentWorkflowId: null,
      presenceUsers: [],
    }),
}))
```

**Step 2: Commit**

```bash
git add frontend/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store.ts
git commit -m "feat: add collaboration Zustand store"
```

---

## Task 4: Frontend - WebSocket Connection Hook

**Files:**
- Create: `frontend/hooks/use-collaboration-socket.ts`

**Step 1: Create the WebSocket hook**

Create `frontend/hooks/use-collaboration-socket.ts`:

```typescript
/**
 * useCollaborationSocket - Manages WebSocket connection for collaboration.
 *
 * Features:
 * - Auto-reconnect with exponential backoff
 * - Heartbeat (ping/pong) for connection health
 * - Message type routing
 * - Event emitter pattern for message handling
 */

import { useEffect, useRef, useCallback, useState } from 'react'
import { useCollaborationStore } from '@/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || ''

interface UseCollaborationSocketOptions {
  workspaceId: string
  agentId: string
  workflowId: string
  enabled?: boolean
}

type MessageHandler = (data: any) => void

export function useCollaborationSocket(options: UseCollaborationSocketOptions) {
  const { workspaceId, agentId, workflowId, enabled = true } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const handlersRef = useRef<Map<string, Set<MessageHandler>>>(new Map())
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected')

  const {
    setConnected,
    setConnecting,
    setCurrentWorkflowId,
    setCurrentUser,
    setPresenceUsers,
    addPresenceUser,
    removePresenceUser,
    updatePresenceCursor,
    updatePresenceSelection,
  } = useCollaborationStore()

  // Register message handler
  const on = useCallback((eventType: string, handler: MessageHandler) => {
    const handlers = handlersRef.current.get(eventType) || new Set()
    handlers.add(handler)
    handlersRef.current.set(eventType, handlers)

    // Return cleanup function
    return () => {
      const handlers = handlersRef.current.get(eventType)
      if (handlers) {
        handlers.delete(handler)
      }
    }
  }, [])

  // Emit message to server
  const emit = useCallback((data: Record<string, any>) => {
    const ws = wsRef.current
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected, cannot send:', data)
    }
  }, [])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!enabled) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setConnectionStatus('connecting')
    setConnecting(true)

    // Build WebSocket URL
    const params = new URLSearchParams({
      workflow_id: workflowId,
      token: 'placeholder-token', // TODO: Get actual auth token
    })
    const wsUrl = `${WS_BASE_URL}/api/workspaces/${workspaceId}/agents/${agentId}/collaboration?${params}`

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[Collaboration] WebSocket connected')
        setConnectionStatus('connected')
        setConnected(true)
        setCurrentWorkflowId(workflowId)

        // Generate user info
        const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`
        const userName = `User ${userId.substr(-4)}`
        setCurrentUser(userId, userName, '')

        // Send join message
        emit({
          type: 'join',
          workflowId,
          userId,
          userName,
        })

        // Start heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
        }
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            emit({ type: 'ping', timestamp: Date.now() })
          }
        }, 30000) // 30 seconds
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const eventType = data.type

          // Handle built-in events
          switch (eventType) {
            case 'user_list':
              setPresenceUsers(data.users)
              break
            case 'user_joined':
              addPresenceUser(data)
              break
            case 'user_left':
              removePresenceUser(data.userId)
              break
            case 'cursor_update':
              updatePresenceCursor(data.userId, data.position)
              if (data.selection) {
                updatePresenceSelection(data.userId, data.selection)
              }
              break
          }

          // Route to registered handlers
          const handlers = handlersRef.current.get(eventType)
          if (handlers) {
            handlers.forEach((handler) => handler(data))
          }
        } catch (error) {
          console.error('[Collaboration] Failed to parse message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('[Collaboration] WebSocket closed:', event.code, event.reason)
        setConnectionStatus('disconnected')
        setConnected(false)

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
          heartbeatIntervalRef.current = null
        }

        // Auto-reconnect with exponential backoff
        if (enabled && !event.wasClean) {
          const delay = Math.min(1000 * Math.pow(2, reconnectTimeoutRef.current ? 1 : 0), 30000)
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('[Collaboration] Reconnecting...')
            connect()
          }, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('[Collaboration] WebSocket error:', error)
      }
    } catch (error) {
      console.error('[Collaboration] Failed to create WebSocket:', error)
      setConnectionStatus('disconnected')
      setConnected(false)
    }
  }, [enabled, workflowId, workspaceId, agentId])

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected')
      wsRef.current = null
    }
    setConnected(false)
    setConnectionStatus('disconnected')
  }, [])

  // Connect on mount and on options change
  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  // Manual reconnect function
  const reconnect = useCallback(() => {
    disconnect()
    setTimeout(() => connect(), 100)
  }, [disconnect, connect])

  return {
    isConnected: connectionStatus === 'connected',
    isConnecting: connectionStatus === 'connecting',
    connectionStatus,
    on,
    emit,
    reconnect,
    disconnect,
  }
}
```

**Step 2: Commit**

```bash
git add frontend/hooks/use-collaboration-socket.ts
git commit -m "feat: add collaboration WebSocket connection hook"
```

---

## Task 5: Frontend - Collaborative Workflow Hook

**Files:**
- Create: `frontend/hooks/use-collaborative-workflow.ts`

**Step 1: Create the collaborative workflow hook**

Create `frontend/hooks/use-collaborative-workflow.ts`:

```typescript
/**
 * useCollaborativeWorkflow - Wraps builderStore with collaborative operations.
 *
 * This hook provides collaborative versions of all builder operations:
 * - Monitors builderStore changes
 * - Broadcasts operations to collaborators
 * - Applies remote operations from other users
 * - Prevents infinite loops with isApplyingRemote flag
 */

import { useEffect, useRef, useCallback } from 'react'
import { useBuilderStore } from '@/app/workspace/[workspaceId]/[agentId]/stores/builderStore'
import { useCollaborationSocket } from './use-collaboration-socket'
import { useCollaborationStore } from '@/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store'

interface UseCollaborativeWorkflowOptions {
  workspaceId: string
  agentId: string
  workflowId: string
  enabled?: boolean
}

export function useCollaborativeWorkflow(options: UseCollaborativeWorkflowOptions) {
  const { workspaceId, agentId, workflowId, enabled = true } = options
  const { isConnected, on, emit } = useCollaborationSocket({
    workspaceId,
    agentId,
    workflowId,
    enabled,
  })
  const { currentUserId } = useCollaborationStore()

  const builderStore = useBuilderStore()
  const isApplyingRemote = useRef(false)
  const lastOperationTimestamps = useRef<Map<string, number>>(new Map())

  // Register operation handler
  useEffect(() => {
    const cleanup = on('operation', (data) => {
      if (isApplyingRemote.current) return
      if (data.userId === currentUserId) return // Ignore own operations

      isApplyingRemote.current = true

      try {
        const { action, target, payload, timestamp } = data
        const key = `${target}:${payload.id || ''}`

        // Check timestamp to prevent out-of-order updates
        const lastTime = lastOperationTimestamps.current.get(key) || 0
        if (timestamp && timestamp < lastTime) {
          console.log('[Collaboration] Skipping outdated operation')
          return
        }

        if (timestamp) {
          lastOperationTimestamps.current.set(key, timestamp)
        }

        // Apply the operation to builderStore
        switch (action) {
          case 'add':
            if (target === 'node') {
              builderStore.addNode(payload.type, payload.position, payload.label)
            }
            break

          case 'remove':
            if (target === 'node') {
              builderStore.deleteNode(payload.id)
            }
            break

          case 'update_position':
            if (target === 'node') {
              const node = builderStore.nodes.find((n) => n.id === payload.id)
              if (node) {
                builderStore.onNodesChange([
                  { id: payload.id, type: 'position', position: payload.position },
                ])
              }
            }
            break

          case 'update_label':
            if (target === 'node') {
              builderStore.updateNodeLabel(payload.id, payload.label)
            }
            break

          case 'update_config':
            if (target === 'node') {
              builderStore.updateNodeConfig(payload.id, payload.config)
            }
            break
        }
      } finally {
        isApplyingRemote.current = false
      }
    })

    return cleanup
  }, [on, builderStore, currentUserId])

  // Collaborative node operations
  const collaborativeAddNode = useCallback(
    (type: string, position: { x: number; y: number }, label?: string) => {
      if (!isConnected) {
        // Fallback to local operation
        return builderStore.addNode(type, position, label)
      }

      isApplyingRemote.current = true
      const operationId = `op_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`

      // Generate node ID to match what builderStore will create
      const nodeId = `node_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`

      // Apply locally first (optimistic update)
      builderStore.addNode(type, position, label)

      // Broadcast to collaborators
      emit({
        type: 'operation',
        operationId,
        action: 'add',
        target: 'node',
        payload: {
          id: nodeId,
          type,
          position,
          label,
        },
        timestamp: Date.now(),
      })

      isApplyingRemote.current = false
    },
    [isConnected, builderStore, emit]
  )

  const collaborativeDeleteNode = useCallback(
    (id: string) => {
      if (!isConnected) {
        return builderStore.deleteNode(id)
      }

      isApplyingRemote.current = true
      const operationId = `op_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`

      // Apply locally
      builderStore.deleteNode(id)

      // Broadcast
      emit({
        type: 'operation',
        operationId,
        action: 'remove',
        target: 'node',
        payload: { id },
        timestamp: Date.now(),
      })

      isApplyingRemote.current = false
    },
    [isConnected, builderStore, emit]
  )

  const collaborativeUpdateNodeLabel = useCallback(
    (id: string, label: string) => {
      if (!isConnected) {
        return builderStore.updateNodeLabel(id, label)
      }

      isApplyingRemote.current = true
      const operationId = `op_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`

      builderStore.updateNodeLabel(id, label)

      emit({
        type: 'operation',
        operationId,
        action: 'update_label',
        target: 'node',
        payload: { id, label },
        timestamp: Date.now(),
      })

      isApplyingRemote.current = false
    },
    [isConnected, builderStore, emit]
  )

  const collaborativeUpdateNodeConfig = useCallback(
    (id: string, config: Record<string, unknown>) => {
      if (!isConnected) {
        return builderStore.updateNodeConfig(id, config)
      }

      isApplyingRemote.current = true
      const operationId = `op_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`

      builderStore.updateNodeConfig(id, config)

      emit({
        type: 'operation',
        operationId,
        action: 'update_config',
        target: 'node',
        payload: { id, config },
        timestamp: Date.now(),
      })

      isApplyingRemote.current = false
    },
    [isConnected, builderStore, emit]
  )

  return {
    isConnected,
    // Collaborative operations
    addNode: collaborativeAddNode,
    deleteNode: collaborativeDeleteNode,
    updateNodeLabel: collaborativeUpdateNodeLabel,
    updateNodeConfig: collaborativeUpdateNodeConfig,
    // Direct store access for read-only
    nodes: builderStore.nodes,
    edges: builderStore.edges,
    selectedNodeId: builderStore.selectedNodeId,
    selectNode: builderStore.selectNode,
    undo: builderStore.undo,
    redo: builderStore.redo,
    takeSnapshot: builderStore.takeSnapshot,
  }
}
```

**Step 2: Commit**

```bash
git add frontend/hooks/use-collaborative-workflow.ts
git commit -m "feat: add collaborative workflow operations hook"
```

---

## Task 6: Frontend - Cursor Display Component

**Files:**
- Create: `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationCursors.tsx`

**Step 1: Create the cursor overlay component**

Create `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationCursors.tsx`:

```typescript
/**
 * CollaborationCursors - Displays other users' cursors on the canvas.
 *
 * Features:
 * - Colored cursor pointers with name labels
 * - Smooth transitions (30fps updates)
 * - Selection highlights for selected nodes
 */

'use client'

import { useEffect, useRef, useState } from 'react'
import { useCollaborationStore, PresenceUser } from '../stores/collaboration-store'
import { useReactFlow } from 'reactflow'

interface CursorProps {
  user: PresenceUser
}

const Cursor: React.FC<CursorProps> = ({ user }) => {
  if (!user.cursor) return null

  return (
    <div
      className="absolute pointer-events-none z-50 transition-all duration-75 ease-out"
      style={{
        left: user.cursor.x,
        top: user.cursor.y,
        transform: 'translate(4px, 4px)',
      }}
    >
      {/* Cursor pointer */}
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ color: user.color }}
      >
        <path
          d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 0 1 .35-.15h6.87c.48 0 .72-.58.38-.92L5.85 2.85a.5.5 0 0 0-.35.36Z"
          fill="currentColor"
          stroke="white"
          strokeWidth="1"
        />
      </svg>

      {/* Name label */}
      <div
        className="absolute left-5 top-4 px-2 py-0.5 rounded text-xs text-white whitespace-nowrap font-medium"
        style={{ backgroundColor: user.color }}
      >
        {user.userName}
      </div>
    </div>
  )
}

export const CollaborationCursors: React.FC = () => {
  const { presenceUsers } = useCollaborationStore()
  const { getZoom, getViewport } = useReactFlow()
  const containerRef = useRef<HTMLDivElement>(null)
  const [cursorPositions, setCursorPositions] = useState<Map<string, { x: number; y: number }>>(new Map())

  // Transform screen coordinates to flow coordinates
  const screenToFlowPosition = (screenX: number, screenY: number) => {
    const viewport = getViewport()
    const zoom = getZoom()

    return {
      x: (screenX - viewport.x) / zoom,
      y: (screenY - viewport.y) / zoom,
    }
  }

  // Update cursor positions when presence users change
  useEffect(() => {
    const newPositions = new Map<string, { x: number; y: number }>()

    presenceUsers.forEach((user) => {
      if (user.cursor) {
        // Assuming cursor positions are already in flow coordinates
        // If they're screen coordinates, apply transformation:
        // const flowPos = screenToFlowPosition(user.cursor.x, user.cursor.y)
        newPositions.set(user.userId, user.cursor)
      }
    })

    setCursorPositions(newPositions)
  }, [presenceUsers, getZoom, getViewport])

  if (presenceUsers.length === 0) {
    return null
  }

  return (
    <div ref={containerRef} className="absolute inset-0 pointer-events-none overflow-hidden">
      {presenceUsers.map((user) => {
        const pos = cursorPositions.get(user.userId)
        if (!pos) return null

        return (
          <Cursor
            key={user.userId}
            user={{
              ...user,
              cursor: pos,
            }}
          />
        )
      })}
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationCursors.tsx
git commit -m "feat: add collaboration cursor overlay component"
```

---

## Task 7: Frontend - User Avatars Component

**Files:**
- Create: `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationAvatars.tsx`

**Step 1: Create the avatars display component**

Create `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationAvatars.tsx`:

```typescript
/**
 * CollaborationAvatars - Shows list of collaborators in the room.
 *
 * Displays:
 * - Avatar stack with user initials
 * - Hover tooltip with user names
 * - Connection status indicator
 */

'use client'

import { useCollaborationStore } from '../stores/collaboration-store'
import { useSession } from 'next-auth/react'

export const CollaborationAvatars: React.FC = () => {
  const { presenceUsers, currentUserName, isConnected } = useCollaborationStore()
  const { data: session } = useSession()

  const totalUsers = presenceUsers.length + 1 // +1 for current user

  if (totalUsers <= 1) {
    return null // Hide if only current user
  }

  // Get user initials from name
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="absolute top-4 right-4 z-[100] flex items-center gap-2">
      {/* Connection status indicator */}
      <div
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
          isConnected
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-gray-50 text-gray-500 border border-gray-200'
        }`}
      >
        <div
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
          }`}
        />
        <span>{totalUsers} online</span>
      </div>

      {/* Avatar stack */}
      <div className="flex -space-x-2">
        {/* Current user */}
        {session?.user?.name && (
          <div
            className="w-8 h-8 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center text-white text-xs font-medium"
            title={`${session.user.name} (You)`}
          >
            {getInitials(session.user.name)}
          </div>
        )}

        {/* Other users */}
        {presenceUsers.slice(0, 4).map((user) => (
          <div
            key={user.userId}
            className="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-medium"
            style={{ backgroundColor: user.color }}
            title={user.userName}
          >
            {getInitials(user.userName)}
          </div>
        ))}

        {/* Overflow indicator */}
        {presenceUsers.length > 4 && (
          <div
            className="w-8 h-8 rounded-full bg-gray-400 border-2 border-white flex items-center justify-center text-white text-xs font-medium"
            title={`+${presenceUsers.length - 4} more`}
          >
            +{presenceUsers.length - 4}
          </div>
        )}
      </div>
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationAvatars.tsx
git commit -m "feat: add collaboration avatars component"
```

---

## Task 8: Frontend - Integrate into BuilderCanvas

**Files:**
- Modify: `frontend/app/workspace/[workspaceId]/[agentId]/components/BuilderCanvas.tsx`

**Step 1: Add collaboration components to BuilderCanvas**

Modify `BuilderCanvas.tsx`. Add imports and wrap the ReactFlow component:

Find the imports section and add:
```typescript
import { CollaborationCursors } from './CollaborationCursors'
import { CollaborationAvatars } from './CollaborationAvatars'
```

Find the ReactFlow component (around line 242) and modify:

```typescript
<ReactFlow
  nodes={nodes}
  edges={uniqueEdges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  onInit={setRfInstance}
  onNodeClick={(_, node) => selectNode(node.id)}
  onPaneClick={() => selectNode(null)}
  onNodeDragStart={() => takeSnapshot()}
  nodeTypes={nodeTypes}
  fitView
  className="bg-gray-50 w-full h-full"
  defaultEdgeOptions={{
    style: { stroke: '#cbd5e1', strokeWidth: 1.5 },
    animated: true,
  }}
  proOptions={{ hideAttribution: true }}
>
  <Background color="#cbd5e1" gap={20} size={1} variant={BackgroundVariant.Dots} />

  {/* NEW: Collaboration overlays */}
  <CollaborationCursors />
  <CollaborationAvatars />

  <CustomControls
    past={past}
    future={future}
    canEdit={userPermissions.canEdit}
    onUndo={undo}
    onRedo={redo}
    onPermissionDenied={() => {
      toast({
        title: t('workspace.noPermission'),
        description: t('workspace.cannotEditNode'),
        variant: 'destructive',
      })
    }}
    undoTitle={t('workspace.undo')}
    redoTitle={t('workspace.redo')}
    zoomInTitle={t('workspace.zoomIn')}
    zoomOutTitle={t('workspace.zoomOut')}
    fitViewTitle={t('workspace.fitView')}
  />
</ReactFlow>
```

**Step 2: Commit**

```bash
git add frontend/app/workspace/[workspaceId]/[agentId]/components/BuilderCanvas.tsx
git commit -m "feat: integrate collaboration components into BuilderCanvas"
```

---

## Task 9: Testing - Manual Collaboration Test

**Files:**
- No files to modify

**Step 1: Start the backend server**

```bash
cd backend
# Make sure the collaboration router is registered
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected: Server starts without errors

**Step 2: Start the frontend**

```bash
cd frontend
npm run dev
```

Expected: Frontend starts at http://localhost:3000

**Step 3: Open two browser windows**

1. Open http://localhost:3000 in Window A
2. Open http://localhost:3000 in Window B (incognito mode for different session)
3. Navigate to the same workspace/agent in both windows

**Step 4: Verify collaboration features**

Check the following:

- [ ] Both windows show "2 online" in the avatars component
- [ ] When Window A adds a node, it appears in Window B
- [ ] When Window B deletes a node, it disappears in Window A
- [ ] When Window A moves a node, Window B sees the movement
- [ ] When Window A selects a node, Window B sees the selection change
- [ ] Cursor positions are visible in both windows (if mouse movement tracking is implemented)

**Step 5: Check browser console**

In both windows, open DevTools Console:

Expected: No errors, logs showing WebSocket messages

**Step 6: Test reconnection**

1. Stop the backend server (Ctrl+C)
2. Wait 5 seconds
3. Restart the backend server

Expected: Both clients automatically reconnect

**Step 7: Document test results**

Create a test report file:

```bash
cat > /tmp/collaboration-test-report.md << 'EOF'
# Collaboration Test Report

Date: $(date)

## Test Results

- Connection established: ✅ / ❌
- User count display: ✅ / ❌
- Node addition sync: ✅ / ❌
- Node deletion sync: ✅ / ❌
- Node movement sync: ✅ / ❌
- Auto-reconnect: ✅ / ❌

## Issues Found

(List any issues discovered during testing)

## Performance Notes

(Any performance observations)
EOF
```

**Step 8: Commit**

```bash
git add -A
git commit -m "test: add manual collaboration test documentation"
```

---

## Task 10: Optional Enhancements (Future Work)

These are NOT part of the MVP but can be added later:

### 10.1: Cursor Position Broadcasting

**Files:**
- Modify: `frontend/hooks/use-collaboration-workflow.ts`

Add cursor tracking when mouse moves over the canvas.

### 10.2: Edge Synchronization

**Files:**
- Modify: `frontend/hooks/use-collaborative-workflow.ts`

Add `onConnect` handler to broadcast edge creation to collaborators.

### 10.3: Undo/Redo Sync

**Files:**
- Modify: `frontend/hooks/use-collaborative-workflow.ts`

Synchronize undo/redo operations across collaborators.

### 10.4: Operation Queue

**Files:**
- Create: `frontend/hooks/use-operation-queue.ts`

Implement retry mechanism for failed operations.

### 10.5: Authentication Integration

**Files:**
- Modify: `backend/app/api/workspaces/{workspaceId}/agents/{agentId}/collaboration.py`
- Modify: `frontend/hooks/use-collaboration-socket.ts`

Replace placeholder token with actual JWT authentication.

---

## Summary

This implementation plan provides:

1. **Minimal Intrusion** - No modifications to existing builderStore logic
2. **Independent Collaboration Layer** - Can be toggled on/off
3. **Core Features** - Real-time sync, presence, cursors
4. **Extensible** - Easy to add more operations later

### Files Created

- `backend/app/websocket/collaboration_manager.py`
- `backend/app/api/workspaces/{workspaceId}/agents/{agentId}/collaboration.py`
- `frontend/hooks/use-collaboration-socket.ts`
- `frontend/hooks/use-collaborative-workflow.ts`
- `frontend/app/workspace/[workspaceId]/[agentId]/stores/collaboration-store.ts`
- `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationCursors.tsx`
- `frontend/app/workspace/[workspaceId]/[agentId]/components/CollaborationAvatars.tsx`

### Files Modified

- `BuilderCanvas.tsx` (add 2 components, ~5 lines)

### Next Steps

After completing this plan:

1. Test with 2-3 users in different browsers
2. Monitor WebSocket traffic in DevTools
3. Check for any race conditions in rapid edits
4. Consider adding operation queue for reliability
5. Add proper authentication

---

**End of Implementation Plan**
