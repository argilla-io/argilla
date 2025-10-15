/**
 * Keyboard shortcut definitions for image annotation.
 */
export const ANNOTATION_SHORTCUTS = {
  CANCEL: ["Escape"],
  COMPLETE: ["Enter"],
  NEXT: ["ArrowRight", "n", "N"],
  PREVIOUS: ["ArrowLeft", "p", "P"],
  DELETE: ["Delete", "Backspace"],
} as const;

/**
 * Check if a keyboard event matches any of the specified keys.
 * Handles case-insensitive matching for single character keys.
 *
 * @param e - The keyboard event
 * @param keys - Array of key strings to match against
 * @returns True if the event key matches any of the specified keys
 */
export const matchesKey = (
  e: KeyboardEvent,
  keys: readonly string[]
): boolean => {
  return keys.some((k) =>
    k.length === 1 ? e.key.toLowerCase() === k.toLowerCase() : e.key === k
  );
};
