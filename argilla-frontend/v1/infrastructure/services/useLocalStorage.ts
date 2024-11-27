import {
  ILocalStorageService,
  Options,
} from "~/v1/domain/services/ILocalStorageService";

const STORAGE_KEY = "argilla";

const EMPTY_OBJECT = "{}";

export const useLocalStorage = (): ILocalStorageService => {
  const get = (key: Options) => {
    const storage = localStorage.getItem(STORAGE_KEY);

    if (!storage) return null;

    try {
      const parsed = JSON.parse(storage);

      return parsed[key];
    } catch (error) {
      return undefined;
    }
  };

  const set = (key: Options, value: any) => {
    const storage = localStorage.getItem(STORAGE_KEY) ?? EMPTY_OBJECT;
    try {
      const parsed = JSON.parse(storage);

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          ...parsed,
          [key]: value,
        })
      );
    } catch {}
  };

  const pop = (key: Options) => {
    const value = get(key);

    set(key, null);

    return value;
  };

  return {
    get,
    set,
    pop,
  };
};
