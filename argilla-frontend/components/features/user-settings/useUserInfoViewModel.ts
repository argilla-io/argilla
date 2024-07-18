import { useResolve } from "ts-injecty";
import { GetWorkspacesUseCase } from "~/v1/domain/usecases/get-workspaces-use-case";
import { useUser } from "~/v1/infrastructure/services/useUser";

export const useUserInfoViewModel = () => {
  const { user } = useUser();
  const getWorkspacesUseCase = useResolve(GetWorkspacesUseCase);

  const { status, data: workspaces } = useLazyAsyncData("user", () =>
    getWorkspacesUseCase.execute()
  );

  const isLoadedWorkspaces = computed(() => {
    return status.value !== "idle" && status.value !== "pending";
  });

  return {
    isLoadedWorkspaces,
    workspaces,
    user,
  };
};
