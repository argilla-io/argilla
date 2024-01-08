import { useContext } from "@nuxtjs/composition-api";

export const useTranslate = () => {
  const context = useContext();

  const t = (key: string) => {
    return context.app.i18n.t(key) as string;
  };

  return t;
};
