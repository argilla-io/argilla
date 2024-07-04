import { useRoutes } from "~/v1/infrastructure/services/useRoutes";
import { useUser } from "~/v1/infrastructure/services/useUser";

export const useAvatarTooltipViewModel = () => {
  const { goToSignIn } = useRoutes();
  const { user } = useUser();

  return {
    goToSignIn,
    user,
  };
};
