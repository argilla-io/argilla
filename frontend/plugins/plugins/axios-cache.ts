import { loadCache } from "@/v1/infrastructure/repositories/AxiosCache";

export default ({ $axios }) => {
  loadCache($axios);
};
