import { useRole } from "@/v1/infrastructure/services";

export const useDatasetEmptyViewModel = () => {
  const { isAdminOrOwnerRole } = useRole();

  return {
    isAdminOrOwnerRole,
  };
};
