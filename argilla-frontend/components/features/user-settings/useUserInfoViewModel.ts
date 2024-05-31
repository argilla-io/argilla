import { useFetch } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { GetWorkspacesUseCase } from "~/v1/domain/usecases/get-workspaces-use-case";

export const useUserInfoViewModel = () => {
  const isLoadingWorkspaces = ref(false);
  const workspaces = ref<any[]>([]);
  const getWorkspacesUseCase = useResolve(GetWorkspacesUseCase);

  useFetch(async () => {
    isLoadingWorkspaces.value = true;
    workspaces.value = await getWorkspacesUseCase.execute();
    isLoadingWorkspaces.value = false;
  });

  return {
    isLoadingWorkspaces,
    workspaces,
  };
};
