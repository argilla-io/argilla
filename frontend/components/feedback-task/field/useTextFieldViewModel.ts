import { computed, ComputedRef } from "vue-demi";

const replaceHtmlChars = (text: string): string => {
  return text
    .toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
};

export const useTextFieldViewModel = (props: {
  fieldText: string;
  stringToHighlight: string;
  useMarkdown: boolean;
}) => {
  const text: ComputedRef<string> = computed(() => {
    if (props.useMarkdown) return props.fieldText;

    const sanitizeSentence = replaceHtmlChars(props.fieldText);

    return highlightText(sanitizeSentence, props.stringToHighlight);
  });

  const highlightText = (sentence: string, stringToMatch: string): string => {
    const htmlHighlightText = (text: string) => {
      return `<span class="highlight-text">${text}</span>`;
    };

    const createFindWordsRegex = () => {
      return new RegExp(`${replaceHtmlChars(stringToMatch)}`, "gmi");
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
