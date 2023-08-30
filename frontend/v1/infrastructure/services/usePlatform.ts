export const usePlatform = () => {
  const { userAgent } = window.navigator;

  return {
    isMac: userAgent.includes("Mac"),
  };
};
