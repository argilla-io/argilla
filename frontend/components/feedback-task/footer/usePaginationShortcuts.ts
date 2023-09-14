import { onMounted, onUnmounted, ref } from "vue-demi";
import { usePlatform } from "@/v1/infrastructure/services/usePlatform";

export const usePaginationShortcuts = () => {
  const prevButton = ref(null);
  const nextButton = ref(null);

  onMounted(() => {
    document.addEventListener("keydown", onPressKeyboardShortCut);
  });

  onUnmounted(() => {
    document.removeEventListener("keydown", onPressKeyboardShortCut);
  });

  const stopPropagationForNativeBehavior = (event: Event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const onPressKeyboardShortCut = (event: KeyboardEvent) => {
    const { code, ctrlKey, metaKey } = event;

    if (usePlatform().isMac) {
      if (!metaKey) return;
    } else if (!ctrlKey) return;

    switch (code) {
      case "ArrowRight": {
        stopPropagationForNativeBehavior(event);
        const elem = nextButton.value.$el;
        elem.click();
        break;
      }
      case "ArrowLeft": {
        stopPropagationForNativeBehavior(event);
        const elem = prevButton.value.$el;
        elem.click();
        break;
      }
      default:
      // Do nothing => the code is not registered as shortcut
    }
  };

  return { prevButton, nextButton };
};
