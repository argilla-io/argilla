export const useTranslate = () => {
  const context = useNuxtApp() as any;

  const t = (key: string, values?: any) => {
    return context.nuxt2Context.app.i18n.t(key, values) as string;
  };

  return t;
};
