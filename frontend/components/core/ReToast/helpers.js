const removeElement = (el) => {
  if (typeof el.remove !== 'undefined') {
    el.remove();
  } else {
    el.parentNode.removeChild(el);
  }
};

const hasWindow = () => typeof window !== 'undefined';

const HTMLElement = hasWindow() ? window.HTMLElement : Object;

export { removeElement, hasWindow, HTMLElement };
