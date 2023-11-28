import { ref } from "vue-demi";
import { usePlatform } from "~/v1/infrastructure/services";

declare global {
  interface Window {
    showShortcutsHelper: boolean;
  }
}

export const useQuestionsViewModel = () => {
  const showShortcutsHelper = ref(window.showShortcutsHelper);
  const platform = usePlatform();

  const toggleShortcutsHelper = () => {
    window.showShortcutsHelper = showShortcutsHelper.value =
      !showShortcutsHelper.value;
  };

  const showKeyboardHelper = (event: KeyboardEvent) => {
    const { ctrlKey, metaKey } = event;

    if (platform.isMac) {
      if (metaKey) {
        toggleShortcutsHelper();
      }
    } else if (ctrlKey) {
      toggleShortcutsHelper();
    }
  };

  return { showKeyboardHelper, showShortcutsHelper };
};
