export const usePlatform = () => {
  const { userAgent } = window.navigator;

  return {
    isMac: userAgent.includes("Mac"),
    isMobile:
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        userAgent
      ),
  };
};
