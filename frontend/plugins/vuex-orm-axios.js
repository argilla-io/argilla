import { Model } from "@vuex-orm/core";

export default ({ $axios }) => {
  Model.setAxios($axios);
};
