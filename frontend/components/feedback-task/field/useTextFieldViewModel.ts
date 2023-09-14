import { computed, ComputedRef } from "vue-demi";

const replaceHtmlChars = (text: string): string => {
  return text
    .toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replaceAll("/*", "&#x2F;&#42;")
    .replaceAll("*/", "&#42;&#x2F;");
};

export const useTextFieldViewModel = (props: {
  fieldText: string;
  stringToHighlight: string;
  useMarkdown: boolean;
}) => {
  const text: ComputedRef<string> = computed(() => {
    if (props.useMarkdown) return props.fieldText;

    const sanitizeSentence = replaceHtmlChars(props.fieldText);
    const sanitizeStringToHighlight = replaceHtmlChars(props.stringToHighlight);

    return highlightText(sanitizeSentence, sanitizeStringToHighlight);
  });

  const highlightText = (sentence: string, sentenceToMatch: string): string => {
    const htmlHighlightText = (text: string) => {
      return `<span class="highlight-text">${text}</span>`;
    };

    const createFindWordsRegex = () => {
      const betweenSpecialSymbols = sentenceToMatch
        .split(" ")
        .map((word) => `(?!\\w)${word}(?!\\w)`)
        .join("|");

      const exactMatchWord = sentenceToMatch
        .split(" ")
        .map((word) => `\\b${word}\\b`)
        .join("|");

      return new RegExp(`${betweenSpecialSymbols}|${exactMatchWord}`, "gmi");
    };

    const replaceText = () => {
      return sentence.replace(createFindWordsRegex(), (matched) =>
        matched ? htmlHighlightText(matched) : matched
      );
    };

    return replaceText();
  };

  return { text };
};
