import { usePlatform } from "~/v1/infrastructure/services";
import { ImplicitStorage, useStoreFor } from "~/v1/store/create";

class ShortcutsHelper {
  public showShortcutsHelper = false;

  public toggleShortcutsHelper = () => {
    this.showShortcutsHelper = !this.showShortcutsHelper;
  };
}
const useShowShortcutsHelper = useStoreFor<
  ShortcutsHelper,
  ImplicitStorage<ShortcutsHelper>
>(ShortcutsHelper);

export const useQuestionsViewModel = () => {
  const { state: shortcutsHelper, save } = useShowShortcutsHelper();

  const platform = usePlatform();
  const showKeyboardHelper = (event: KeyboardEvent) => {
    const { ctrlKey, metaKey } = event;

    if (platform.isMac) {
      if (metaKey) {
        shortcutsHelper.toggleShortcutsHelper();
      }
    } else if (ctrlKey) {
      shortcutsHelper.toggleShortcutsHelper();
    }

    save(shortcutsHelper);
  };

  return { showKeyboardHelper, shortcutsHelper };
};
