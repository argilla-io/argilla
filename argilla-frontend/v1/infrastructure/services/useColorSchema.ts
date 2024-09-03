import { ref } from "vue";
export const useColorSchema = () => {
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";

  const currentTheme = ref(localStorage.getItem("theme") || "system");

  const setTheme = (theme: string) => {
    currentTheme.value = theme;
    localStorage.setItem("theme", theme);
    if (theme !== "system") {
      document.documentElement.setAttribute("data-theme", theme);
    } else {
      document.documentElement.setAttribute("data-theme", systemTheme);
    }
  };

  const initialize = () => {
    setTheme(currentTheme.value);
  };

  return {
    currentTheme,
    setTheme,
    initialize,
  };
};
