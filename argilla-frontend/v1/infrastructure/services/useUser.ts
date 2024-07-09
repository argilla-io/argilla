import { User } from "~/v1/domain/entities/user/User";

export const useUser = () => {
  const { $auth } = useNuxtApp();

  const getUser = () => {
    // eslint-disable-next-line camelcase
    const { id, username, first_name, last_name, role, api_key } = $auth.user;

    return new User(id, username, first_name, last_name, role, api_key);
  };

  const user = computed(() => {
    return getUser();
  });

  return {
    getUser,
    user,
  };
};
