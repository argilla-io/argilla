import { ComputedRef, computed } from "vue-demi";
import { useUser } from "./useUser";
import { RoleService } from "~/v1/domain/services/RoleService";

export const useRole = (): RoleService & {
  isAdminOrOwnerRole: ComputedRef<boolean>;
} => {
  const { getUser } = useUser();

  const isAdminOrOwner = () => {
    const user = getUser();

    return user.isAdminOrOwner;
  };

  const isAdminOrOwnerRole = computed(() => {
    return isAdminOrOwner();
  });

  return { isAdminOrOwnerRole, isAdminOrOwner };
};
