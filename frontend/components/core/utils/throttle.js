const debounce = (callback, limit) => {
  let wait = false;

  return () => {
    if (!wait) {
      callback.call();
      wait = true;

      window.setTimeout(() => {
        wait = false;
      }, limit);
    }
  };
};

export default debounce;
