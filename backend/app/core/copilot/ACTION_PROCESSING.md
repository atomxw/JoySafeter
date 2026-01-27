# Action Processing Logic Consistency

This document describes the action processing logic used in both frontend and backend, and ensures they remain synchronized.

## Overview

Action processing is implemented in two places:
- **Backend**: `backend/app/services/copilot_service.py::_process_actions` (Python)
- **Frontend**: `frontend/utils/copilot/actionProcessor.ts::ActionProcessor.processActions` (TypeScript)

Both implementations process the same action types and should produce equivalent results (modulo UI-specific properties).

## Action Types

### CREATE_NODE

**Backend:**
- Creates node with `id` from payload or generates `ai_{timestamp}`
- Sets `type: "custom"`
- Sets `position` from payload or defaults to `{x: 0, y: 0}`
- Sets `data.label` from payload or defaults to "Node"
- Sets `data.type` from payload
- Sets `data.config` from payload or `{}`

**Frontend:**
- Creates node with `id` from payload or generates `ai_{Date.now()}`
- Sets `type: "custom"`
- Sets `position` from payload or defaults to `{x: 0, y: 0}`
- Uses `nodeRegistry.get(type)` to get default config
- Sets `data.label` from payload or uses registry default
- Sets `data.type` from payload
- Merges registry default config with payload config

**Differences:**
- Frontend uses `nodeRegistry` for default config (UI-specific)
- Backend directly uses payload config
- **This is acceptable** - frontend needs registry for UI rendering

### CONNECT_NODES

**Backend:**
- Checks if edge already exists (by source and target)
- Creates edge with `id: f"e-{source}-{target}"`
- Sets `source` and `target` from payload

**Frontend:**
- Checks if edge already exists (by source and target)
- Creates edge with `id: e-${source}-${target}`
- Sets `source` and `target` from payload
- Adds UI properties: `animated: true`, `style: { stroke: '#cbd5e1', strokeWidth: 1.5 }`

**Differences:**
- Frontend adds UI-specific properties (animated, style)
- **This is acceptable** - these are presentation-only

### DELETE_NODE

**Backend:**
- Filters out node with matching `id`
- Filters out edges where `source == id` or `target == id`

**Frontend:**
- Filters out node with matching `id`
- Filters out edges where `source == id` or `target == id`

**Differences:**
- None - logic is identical

### UPDATE_CONFIG

**Backend:**
- Finds node by `id` using index lookup (O(1))
- Merges existing config with payload config: `{**existing_config, **config}`
- Logs warning if node not found

**Frontend:**
- Maps over nodes to find matching `id`
- Merges existing config with payload config: `{ ...nodeData.config, ...action.payload.config }`

**Differences:**
- Backend uses index for O(1) lookup (more efficient)
- Frontend uses array map (acceptable for smaller datasets)
- **Both produce same result** - config merge is identical

### UPDATE_POSITION

**Backend:**
- Finds node by `id` using index lookup (O(1))
- Updates `position` from payload
- Logs warning if node not found

**Frontend:**
- Maps over nodes to find matching `id`
- Updates `position` from payload

**Differences:**
- Backend uses index for O(1) lookup (more efficient)
- Frontend uses array map (acceptable for smaller datasets)
- **Both produce same result**

## Consistency Guarantees

### Data Structure
- Both use the same action payload structure
- Both produce equivalent graph state (nodes and edges)
- Frontend adds UI-specific properties (animated, style) which don't affect data consistency

### Edge Cases
- Both handle missing IDs by generating new ones
- Both check for duplicate edges before creating
- Both handle missing nodes gracefully (backend logs warning, frontend silently skips)

### Validation
- Backend validates actions before processing (via `action_validator.py`)
- Frontend relies on TypeScript types for validation
- Both should reject invalid actions before processing

## Testing Recommendations

To ensure consistency, consider:
1. **Shared test cases**: Define test cases in a language-agnostic format (JSON/YAML)
2. **Round-trip tests**: Process actions on backend, send to frontend, verify UI matches
3. **Edge case coverage**: Test missing IDs, duplicate edges, invalid node references

## Maintenance Notes

When modifying action processing logic:
1. **Update both implementations** - changes must be synchronized
2. **Update this document** - reflect any logic changes
3. **Add tests** - ensure both implementations handle new cases
4. **Consider shared spec** - if logic becomes complex, consider a shared specification file

## Current Status

✅ **CREATE_NODE**: Consistent (frontend uses registry for UI, acceptable)
✅ **CONNECT_NODES**: Consistent (frontend adds UI properties, acceptable)
✅ **DELETE_NODE**: Identical logic
✅ **UPDATE_CONFIG**: Consistent (different lookup methods, same result)
✅ **UPDATE_POSITION**: Consistent (different lookup methods, same result)

All action types are functionally consistent. Frontend adds UI-specific properties which don't affect data consistency.
