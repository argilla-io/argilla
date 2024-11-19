import { NuxtI18nInstance } from "@nuxtjs/i18n";
import { useLocalStorage } from "./useLocalStorage";

type Context = {
  app: {
    i18n: {
      locales: NuxtI18nInstance["locales"];
      setLocale: NuxtI18nInstance["setLocale"];
    };
  };
};

export const useLanguageDetector = (context: Context) => {
  const { change } = useLanguageChanger(context);
  const { get } = useLocalStorage();

  const { i18n } = context.app;

  const detect = () => {
    return get("language") || navigator.language;
  };

  const exists = (language: string) => {
    return i18n.locales.some((l) => l.code === language);
  };

  const initialize = () => {
    const language = detect();

    if (exists(language)) {
      return change(language);
    }

    change("en");
  };

  return {
    initialize,
  };
};

export const useLanguageChanger = (context: Context) => {
  const { i18n } = context.app;

  const { set } = useLocalStorage();

  const change = (language: string) => {
    i18n.setLocale(language);

    set("language", language);
  };

  return {
    change,
    languages: i18n.locales.sort((a, b) => a.code.localeCompare(b.code)),
  };
};
