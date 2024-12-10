export const useClipboard = () => {
  const unsecuredCopy = (text) => {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand("copy");
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Unable to copy to clipboard", err);
    }

    document.body.removeChild(textArea);
  };

  const copy = function (text) {
    if (window.isSecureContext && navigator.clipboard) {
      navigator.clipboard.writeText(text);
    } else {
      unsecuredCopy(text);
    }
  };

  return { copy };
};
