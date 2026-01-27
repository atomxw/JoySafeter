# Three-Panel Chat Layout Design

## Overview

Design document for implementing a Suna-inspired three-panel chat interface layout.

## Architecture

```
ChatInterface
├── Left Sidebar Panel (ResizablePanel)
│   ├── Agent/Project Selector
│   ├── New Chat Button
│   ├── Conversation Groups (Today/This Month/Older)
│   └── User Profile & Settings
│
├── Main Chat Panel (ResizablePanel)
│   ├── Header (Title + Status + Tool Toggle)
│   ├── ThreadContent (Messages, flex-col-reverse)
│   └── ChatInput (Fixed at bottom)
│
└── Right Tool Panel (ResizablePanel)
    ├── Tab Navigation (Tools/Files/Terminal)
    ├── Tool Navigation Controls
    └── Content View
```

## Panel Specifications

### Left Sidebar
- **Collapsed**: 64px (icon-only)
- **Expanded**: 256px
- **Resizable**: Yes
- **Collapsible**: Yes
- **Keyboard Shortcut**: Cmd/Ctrl+B

### Main Chat Area
- **Default Size**: 100% (no tool panel) / 50% (tool panel open)
- **Min Size**: 100% (no tool panel) / 30% (tool panel open)
- **Max Size**: 100% (no tool panel) / 70% (tool panel open)

### Right Tool Panel
- **Default Size**: 50%
- **Min Size**: 35%
- **Max Size**: 70%
- **Auto-open**: When tool calls are present
- **Keyboard Shortcut**: Cmd/Ctrl+K

## State Management

### sidebar-store.ts
```typescript
interface SidebarState {
  isCollapsed: boolean
  setIsCollapsed: (value: boolean) => void
  toggle: () => void
}
```

### tool-panel-store.ts
```typescript
interface ToolPanelState {
  isOpen: boolean
  activeView: 'tools' | 'files' | 'terminal' | 'browser'
  selectedToolIndex: number
  selectedFilePath: string | null
  suiteMode: boolean
  setIsOpen: (value: boolean) => void
  setActiveView: (view: string) => void
  setSelectedToolIndex: (index: number) => void
  setSelectedFilePath: (path: string | null) => void
  setSuiteMode: (value: boolean) => void
}
```

## Components

### Existing (to be enhanced)
- `ChatSidebar.tsx` - Integrate with ResizablePanel, add agent selector
- `ToolExecutionPanel.tsx` - Add multi-view tabs, tool navigation
- `ChatInterface.tsx` - Three-panel layout with ResizablePanelGroup

### New Components
- `FileBrowser.tsx` - File tree viewer
- `CodeViewer.tsx` - Code viewer with syntax highlighting
- `ToolNavigation.tsx` - Tool navigation controls (prev/next, dropdown)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd/Ctrl+B | Toggle left sidebar |
| Cmd/Ctrl+K | Toggle tool panel |
| Cmd/Ctrl+[ | Previous tool |
| Cmd/Ctrl+] | Next tool |
| Escape | Close tool panel |

## Implementation Tasks

1. Create Zustand stores for state management
2. Update ChatSidebar to integrate with ResizablePanel
3. Enhance ToolExecutionPanel with multi-view tabs
4. Create FileBrowser component
5. Create CodeViewer component with syntax highlighting
6. Create ToolNavigation component
7. Update ChatInterface with three-panel layout
8. Add keyboard shortcuts support
