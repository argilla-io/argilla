import { useRunningEnvironment } from "~/v1/infrastructure/services/useRunningEnvironment";
import { useRole } from "@/v1/infrastructure/services";

export const usePersistentStorageViewModel = () => {
  const { hasPersistentStorageWarning } = useRunningEnvironment();
  const { isAdminOrOwnerRole } = useRole();

  return {
    hasPersistentStorageWarning,
    isAdminOrOwnerRole,
  };
};
