import { useContext } from "@nuxtjs/composition-api";
import { ComputedRef, computed } from "vue-demi";
import { RoleService } from "~/v1/domain/services/RoleService";

export const useRole = (): RoleService & {
  isAdminOrOwnerRole: ComputedRef<boolean>;
} => {
  const { $auth } = useContext();

  const isAdminOrOwner = () => {
    const role = $auth.user.role;
    return role === "admin" || role === "owner";
  };

  const isAdminOrOwnerRole = computed(() => {
    return isAdminOrOwner();
  });

  return { isAdminOrOwnerRole, isAdminOrOwner };
};
