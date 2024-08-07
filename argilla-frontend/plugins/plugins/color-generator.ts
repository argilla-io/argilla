import { Inject } from "@nuxt/types/app";
import { Color } from "~/v1/domain/entities/color/Color";

export default (_, inject: Inject) => {
  inject("color", Color);
};
