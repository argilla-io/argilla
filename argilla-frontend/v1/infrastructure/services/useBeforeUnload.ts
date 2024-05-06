export const useBeforeUnload = () => {
  const confirm = () => {
    window.onbeforeunload = () => true;
  };

  const destroy = () => {
    window.onbeforeunload = undefined;
  };

  return {
    confirm,
    destroy,
  };
};
