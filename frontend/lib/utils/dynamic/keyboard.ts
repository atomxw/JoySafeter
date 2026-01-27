/**
 * Keyboard utilities
 * Helper functions for keyboard interactions
 */

/**
 * Check if key combination is pressed
 */
export const isKeyCombo = (
  event: KeyboardEvent,
  key: string,
  ctrl: boolean = false,
  shift: boolean = false,
  alt: boolean = false
): boolean => {
  return (
    event.key === key &&
    event.ctrlKey === ctrl &&
    event.shiftKey === shift &&
    event.altKey === alt
  );
};

/**
 * Check if Enter key is pressed
 */
export const isEnterKey = (event: KeyboardEvent): boolean => {
  return event.key === 'Enter';
};

/**
 * Check if Escape key is pressed
 */
export const isEscapeKey = (event: KeyboardEvent): boolean => {
  return event.key === 'Escape';
};

/**
 * Check if Ctrl+Enter is pressed
 */
export const isCtrlEnter = (event: KeyboardEvent): boolean => {
  return isKeyCombo(event, 'Enter', true);
};

/**
 * Check if Shift+Enter is pressed
 */
export const isShiftEnter = (event: KeyboardEvent): boolean => {
  return isKeyCombo(event, 'Enter', false, true);
};

/**
 * Get keyboard shortcut display string
 */
export const getShortcutDisplay = (
  key: string,
  ctrl: boolean = false,
  shift: boolean = false,
  alt: boolean = false
): string => {
  const parts = [];
  if (ctrl) parts.push('Ctrl');
  if (shift) parts.push('Shift');
  if (alt) parts.push('Alt');
  parts.push(key);
  return parts.join('+');
};
