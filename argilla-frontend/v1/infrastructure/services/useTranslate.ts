import { useContext } from "@nuxtjs/composition-api";

export const useTranslate = () => {
  const context = useContext();

  const t = (key: string, values?: any) => {
    return context.app.i18n.t(key, values) as string;
  };

  const tc = (key: string, choice: number) => {
    return context.app.i18n.tc(key, choice) as string;
  };

  return { t, tc };
};
