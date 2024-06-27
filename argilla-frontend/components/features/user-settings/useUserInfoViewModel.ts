import { useResolve } from "ts-injecty";
import { GetWorkspacesUseCase } from "~/v1/domain/usecases/get-workspaces-use-case";

export const useUserInfoViewModel = () => {
  const getWorkspacesUseCase = useResolve(GetWorkspacesUseCase);

  const { status, data: workspaces } = useLazyAsyncData("user", () =>
    getWorkspacesUseCase.execute()
  );

  const isLoadingWorkspaces = computed(() => {
    return status.value !== "idle" && status.value !== "pending";
  });

  return {
    isLoadingWorkspaces,
    workspaces,
  };
};
