class BeforeUnload {
  confirm() {
    window.onbeforeunload = () => "";
  }

  destroy() {
    window.onbeforeunload = undefined;
  }
}

export const useBeforeUnload = () => {
  return new BeforeUnload();
};
