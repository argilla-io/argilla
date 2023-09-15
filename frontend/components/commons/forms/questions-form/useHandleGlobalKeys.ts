import { Ref, onMounted, onUnmounted } from "vue-demi";

export const useHandleGlobalKeys = (
  userComesFromOutside: Ref<boolean>,
  focusOnFirstQuestionFromOutside: Function,
  onDraft: Function,
  onSubmit: Function,
  onClear: Function,
  onDiscard: Function
) => {
  const handleGlobalKeys = (event: KeyboardEvent) => {
    const { code, shiftKey, ctrlKey, metaKey } = event;

    if (code === "Tab" && userComesFromOutside.value) {
      focusOnFirstQuestionFromOutside(event);

      return;
    }

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
        if (shiftKey) onSubmit();
        break;
      }
      case "Space": {
        if (shiftKey) {
          event.preventDefault(); // TODO: Review this line
          onClear();
        }
        break;
      }
      case "Backspace": {
        if (shiftKey) onDiscard();
        break;
      }
      default:
    }
  };

  onMounted(() => {
    document.addEventListener("keydown", handleGlobalKeys);
  });
  onUnmounted(() => {
    document.removeEventListener("keydown", handleGlobalKeys);
  });
};
