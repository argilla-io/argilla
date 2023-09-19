import "@nuxt/types";
import { Auth } from "@nuxtjs/auth-next";
import "vue";

declare module "*.vue" {
  import Vue from "vue";
  export default Vue;
}

declare module "@nuxt/types" {
  interface Context {
    $auth: Auth;
  }
}
