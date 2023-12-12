import { onBeforeMount, onBeforeUnmount, ref } from "vue-demi";
import { usePlatform } from "~/v1/infrastructure/services";
import { useLocalStorage } from "~/v1/infrastructure/services/useLocalStorage";

const KEY_PRESSED_TIMEOUT_IN_MS = 350;

export const useQuestionsViewModel = () => {
  const { get, set } = useLocalStorage();
  const showShortcutsHelper = ref(get("showShortcutsHelper") ?? true);
  const platform = usePlatform();
  let timeout = null;

  const toggleShortcutsHelper = () => {
    showShortcutsHelper.value = !showShortcutsHelper.value;

    set("showShortcutsHelper", showShortcutsHelper.value);
  };

  const longPressToggleShortcutsHelper = () => {
    timeout = setTimeout(() => {
      toggleShortcutsHelper();
    }, KEY_PRESSED_TIMEOUT_IN_MS);
  };

  const trackOnKeyDown = (event: KeyboardEvent) => {
    const { code } = event;

    const isCtrlKeyPressed = code === "ControlLeft" || code === "ControlRight";
    const isMetaKeyPressed = code === "MetaLeft" || code === "MetaRight";

    if (!isCtrlKeyPressed && !isMetaKeyPressed) return;

    if (platform.isMac) {
      if (isMetaKeyPressed) {
        longPressToggleShortcutsHelper();
      }
    } else if (isCtrlKeyPressed) {
      longPressToggleShortcutsHelper();
    }
  };

  const trackOnKeyUp = () => {
    clearTimeout(timeout);
  };

  onBeforeMount(() => {
    document.addEventListener("keydown", trackOnKeyDown);
    document.addEventListener("keyup", trackOnKeyUp);
  });

  onBeforeUnmount(() => {
    document.removeEventListener("keydown", trackOnKeyDown);
    document.removeEventListener("keyup", trackOnKeyUp);
  });

  return { showShortcutsHelper };
};
