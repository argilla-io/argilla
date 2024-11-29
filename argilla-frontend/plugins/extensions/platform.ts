import { Inject } from "@nuxt/types/app";
import { usePlatform } from "~/v1/infrastructure/services/usePlatform";

export default (_, inject: Inject) => {
  const platform = usePlatform();

  inject("platform", platform);
};
