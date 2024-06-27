import type { ComputedRef } from "vue";
import { RoleService } from "~/v1/domain/services/RoleService";

export const useRole = (): RoleService & {
  isAdminOrOwnerRole: ComputedRef<boolean>;
} => {
  const { $auth } = useNuxtApp();

  const isAdminOrOwner = () => {
    const role = $auth.user.role;
    return role === "admin" || role === "owner";
  };

  const isAdminOrOwnerRole = computed(() => {
    return isAdminOrOwner();
  });

  return { isAdminOrOwnerRole, isAdminOrOwner };
};
