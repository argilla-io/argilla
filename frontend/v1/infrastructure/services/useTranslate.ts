import { useContext } from "@nuxtjs/composition-api";

export const useTranslate = () => {
  const context = useContext();

  const t = (key: string, values?: any) => {
    return context.app.i18n.t(key, values) as string;
  };

  return t;
};
