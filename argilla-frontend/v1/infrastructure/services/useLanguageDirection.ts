export const useLanguageDirection = () => {
  const isRTL = (text: string) => {
    const rtlCount = (
      text.match(/[\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC]/g) || []
    ).length;

    const ltrCount = (
      text.match(
        // eslint-disable-next-line no-misleading-character-class
        /[A-Za-z\u00C0-\u00C0\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF\u2C00-\uFB1C\uFDFE-\uFE6F\uFEFD-\uFFFF]/g
      ) || []
    ).length;

    return rtlCount > ltrCount;
  };

  return {
    isRTL,
  };
};
