import { useContext } from "@nuxtjs/composition-api";
import { useLanguageChanger } from "~/v1/infrastructure/services";

export const useUserSettingsLanguageViewModel = () => {
  const context = useContext();
  const { change, languages } = useLanguageChanger(context);

  return {
    change,
    languages,
  };
};
