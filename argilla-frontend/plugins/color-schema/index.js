export default (_, inject) => {
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";

  const getInitialTheme = localStorage.getItem("theme") || systemTheme;

  const updateTheme = (theme) => {
    localStorage.setItem("theme", theme);
    if (theme !== "system") {
      document.documentElement.setAttribute("data-theme", theme);
    } else {
      document.documentElement.setAttribute("data-theme", systemTheme);
    }
  };

  inject("colorSchema", (theme) => {
    updateTheme(theme);
    systemTheme;
  });

  const init = () => {
    updateTheme(getInitialTheme);
  };

  if (process.client) {
    window.onNuxtReady(() => {
      init();
    });
  }
};
