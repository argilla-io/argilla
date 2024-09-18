import { NuxtI18nInstance } from "@nuxtjs/i18n";

type Context = {
  app: {
    i18n: {
      locales: NuxtI18nInstance["locales"];
      setLocale: NuxtI18nInstance["setLocale"];
    };
  };
};

export const useLanguageDetector = (context: Context) => {
  const { i18n } = context.app;

  const change = (language: string) => {
    i18n.setLocale(language);
  };

  const detect = () => {
    return navigator.language;
  };

  const exists = (language: string) => {
    return i18n.locales.some((l) => l.code === language);
  };

  const initialize = () => {
    const language = detect();

    if (exists(language)) {
      return change(language);
    }

    const languageCode = language.split("-")[0];

    if (exists(languageCode)) {
      return change(languageCode);
    }
  };

  return {
    initialize,
  };
};
