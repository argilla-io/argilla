import { ref } from "vue-demi";
import { useFetch } from "@nuxtjs/composition-api";
import { useRunningEnvironment } from "@/v1/infrastructure/services/useRunningEnvironment";
import { useRole } from "@/v1/infrastructure/services";

export const usePersistentStorageViewModel = () => {
  const showBanner = ref(false);
  const { hasPersistentStorageWarning } = useRunningEnvironment();
  const { isAdminOrOwnerRole } = useRole();

  useFetch(async () => {
    try {
      showBanner.value = await hasPersistentStorageWarning();
    } catch (error) {}
  });

  return {
    showBanner,
    isAdminOrOwnerRole,
  };
};
