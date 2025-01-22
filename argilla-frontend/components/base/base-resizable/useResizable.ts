import { useDebounce, useLocalStorage } from "~/v1/infrastructure/services";

export const useResizable = ({ id }: { id: string }) => {
  const debounce = useDebounce(300);
  const { get, set } = useLocalStorage();

  const getPosition = () => {
    const layout = get("layout");

    if (!layout) return;

    return layout[id];
  };

  const setPosition = async (position: unknown) => {
    debounce.stop();

    await debounce.wait();

    const layout = get<Record<string, unknown>>("layout");

    set("layout", {
      ...layout,
      [id]: position,
    });
  };

  return {
    debounce,
    getPosition,
    setPosition,
  };
};
