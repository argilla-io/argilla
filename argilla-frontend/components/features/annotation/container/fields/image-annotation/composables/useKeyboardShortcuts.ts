import { onMounted, onUnmounted, Ref } from "vue-demi";
import { ANNOTATION_SHORTCUTS, matchesKey } from "../utils/keyboardShortcuts";

export interface KeyboardShortcutHandlers {
  // Edit mode handlers
  onExitEditMode?: () => void;
  onNextAnnotation?: () => void;
  onPreviousAnnotation?: () => void;
  onDeleteInEditMode?: () => void;

  // Idle mode handlers
  onExitHoleDrawingMode?: () => void;

  // Interaction handlers
  onInteractionKeyDown?: (e: KeyboardEvent) => {
    shouldComplete?: boolean;
    shouldCancel?: boolean;
    shouldContinue?: boolean;
  } | void;
}

export interface KeyboardShortcutState {
  mode: Ref<
    | { kind: "idle" }
    | { kind: "drawing" }
    | { kind: "edit"; annotationIndex: number }
  >;
  activeInteraction: Ref<{ onKeyDown: (e: KeyboardEvent) => any } | null>;
  holeDrawingModeActive: Ref<boolean>;
  annotationCount: Ref<number>;
}

/**
 * Composable for managing keyboard shortcuts in image annotation
 * Handles edit mode, idle mode, and interaction shortcuts
 */
export const useKeyboardShortcuts = (
  state: KeyboardShortcutState,
  handlers: KeyboardShortcutHandlers
) => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Priority 1: Active interaction (drawing)
    if (state.activeInteraction.value) {
      const result = state.activeInteraction.value.onKeyDown(e);
      if (handlers.onInteractionKeyDown && result) {
        handlers.onInteractionKeyDown(e);
      }
      return;
    }

    // Priority 2: Edit mode shortcuts
    if (state.mode.value.kind === "edit") {
      if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
        e.preventDefault();
        handlers.onExitEditMode?.();
      } else if (matchesKey(e, ANNOTATION_SHORTCUTS.NEXT)) {
        e.preventDefault();
        handlers.onNextAnnotation?.();
      } else if (matchesKey(e, ANNOTATION_SHORTCUTS.PREVIOUS)) {
        e.preventDefault();
        handlers.onPreviousAnnotation?.();
      } else if (matchesKey(e, ANNOTATION_SHORTCUTS.DELETE)) {
        e.preventDefault();
        handlers.onDeleteInEditMode?.();
      }
      return;
    }

    // Priority 3: Idle mode shortcuts
    if (state.mode.value.kind === "idle") {
      if (
        matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL) &&
        state.holeDrawingModeActive.value
      ) {
        e.preventDefault();
        handlers.onExitHoleDrawingMode?.();
      }
    }
  };

  onMounted(() => {
    window.addEventListener("keydown", handleKeyDown);
  });

  onUnmounted(() => {
    window.removeEventListener("keydown", handleKeyDown);
  });

  return {
    handleKeyDown,
  };
};
