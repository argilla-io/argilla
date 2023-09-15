type TBeforeUnload = {
  confirm: () => void;
  destroy: () => void;
};

const useBeforeUnload: () => TBeforeUnload = () => {
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

export { TBeforeUnload, useBeforeUnload };
