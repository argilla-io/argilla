import { onMounted, onUnmounted, ref } from "vue-demi";

export const usePaginationShortcuts = () => {
  const prevButton = ref(null);
  const nextButton = ref(null);

  onMounted(() => {
    document.addEventListener("keydown", onPressKeyboardShortCut);
  });

  onUnmounted(() => {
    document.removeEventListener("keydown", onPressKeyboardShortCut);
  });

  const onPressKeyboardShortCut = ({ code }) => {
    switch (code) {
      case "ArrowRight": {
        const elem = nextButton.value.$el;
        elem.click();
        break;
      }
      case "ArrowLeft": {
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
