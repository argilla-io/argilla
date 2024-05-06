import { Inject } from "@nuxt/types/app";
import { useLanguageDirection } from "~/v1/infrastructure/services/useLanguageDirection";

export default (_, inject: Inject) => {
  const language = useLanguageDirection();

  inject("language", language);
};
