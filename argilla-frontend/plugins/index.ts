import { Context } from "@nuxt/types";
import { Inject } from "@nuxt/types/app";

declare const require: {
  context(
    directory: string,
    useSubdirectories: boolean,
    regExp: RegExp
  ): {
    keys(): string[];
    (id: string);
  };
};

export default (context: Context, inject: Inject) => {
  const importing = require.context("./", true, /^\.\/.*\.(ts|js)$/);

  importing
    .keys()
    .filter((key) => key !== "./index.ts")
    .forEach((key) => {
      const module = importing(key);

      if (module.default) {
        module.default(context, inject);
      }
    });
};
