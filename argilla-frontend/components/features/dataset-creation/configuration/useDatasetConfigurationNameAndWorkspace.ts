import { useFetch } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { GetWorkspacesUseCase } from "~/v1/domain/usecases/get-workspaces-use-case";

export const useDatasetConfigurationNameAndWorkspace = () => {
  const workspaces = ref<any[]>([]);
  const getWorkspacesUseCase = useResolve(GetWorkspacesUseCase);

  useFetch(async () => {
    workspaces.value = await getWorkspacesUseCase.execute();
  });

  return {
    workspaces,
  };
};
