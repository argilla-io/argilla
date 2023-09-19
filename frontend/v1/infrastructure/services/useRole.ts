import { useContext } from "@nuxtjs/composition-api";
import { computed } from "vue-demi";

export const useRole = () => {
  const { $auth } = useContext();
  const isAdminOrOwnerRole = computed(() => {
    const role = $auth.user.role;
    return role === "admin" || role === "owner";
  });

  return { isAdminOrOwnerRole };
};
