import { onMounted, onUnmounted } from "vue";

export function useGlobalShortcuts(
  onDraft: Function,
  onSubmit: Function,
  onClear: Function,
  onDiscard: Function
) {
  const onPressKeyboardShortCut = (event) => {
    const { code, shiftKey, ctrlKey, metaKey } = event;
    switch (code) {
      case "KeyS": {
        if (ctrlKey || metaKey) {
          event.preventDefault();
          event.stopPropagation();
          onDraft();
        }
        break;
      }
      case "Enter": {
        onSubmit();
        break;
      }
      case "Space": {
        if (shiftKey) onClear();
        break;
      }
      case "Backspace": {
        onDiscard();
        break;
      }
      default:
    }
  };
  onMounted(() => {
    document.addEventListener("keydown", onPressKeyboardShortCut);
  });
  onUnmounted(() => {
    document.removeEventListener("keydown", onPressKeyboardShortCut);
  });
}
