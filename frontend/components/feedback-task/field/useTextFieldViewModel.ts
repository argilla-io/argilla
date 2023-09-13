import { computed, ComputedRef, ref } from "vue-demi";

type TSentenceInfo = {
  substring: string;
  index_min: number;
  index_max: number;
  hasBacktick: boolean;
};

export const useTextFieldViewModel = (props: {
  fieldText: string;
  stringToHighlight: string;
  useMarkdown: boolean;
}) => {
  const text: ComputedRef<string> = computed(() => {
    const newText = ref(
      props.useMarkdown
        ? props.fieldText
        : sanitizeHtmlToRenderText(props.fieldText)
    );

    if (props.stringToHighlight.length === 0) return newText.value;

    const splittedStringToHightlight = props.stringToHighlight.split(/\s+/);

    splittedStringToHightlight.forEach((word) => {
      if (word.includes("`")) return;

      newText.value = getHighlightedSentenceFor(word, newText.value);
    });

    return newText.value;
  });

  const getHighlightedSentenceFor = (aWord: string, aText: string) => {
    const sentenceInfos: TSentenceInfo[] = getSentenceInfosFor(aText);

    const specialChars = /[`!@#$%^&*()_\-+=[\]{};':"\\|,.<>/?~ ]/;

    const escapeCharacters = aWord.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

    const regexExactWord = specialChars.test(aWord)
      ? new RegExp(`${escapeCharacters}`, "gi")
      : new RegExp(`\\b${escapeCharacters}\\b`, "gi");

    return aText.replace(regexExactWord, (match, index) => {
      const matchInfo: TSentenceInfo = sentenceInfos.find(
        (info) => index >= info.index_min && index <= info.index_max
      );

      if (!matchInfo || (matchInfo.hasBacktick && props.useMarkdown))
        return match;

      return htmlHighlightFor(match);
    });
  };

  const getSentenceInfosFor = (aText: string): TSentenceInfo[] => {
    const regexToSeparateMarkdown = /[^`]+|`[^`]*`/g;

    const matchesWithoutMarkdown: RegExpMatchArray = aText.match(
      regexToSeparateMarkdown
    );

    const sentenceInfos: TSentenceInfo[] = matchesWithoutMarkdown.map(
      (substring, index) => {
        return {
          substring,
          index_min: index,
          index_max: index + substring.length,
          hasBacktick: substring.includes("`"),
        };
      }
    );

    return sentenceInfos;
  };

  const htmlHighlightFor: (aText: string) => string = (aText: string) =>
    `<span class="highlight-text">${aText}</span>`;

  const sanitizeHtmlToRenderText = (text: string) => {
    return text
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  };

  return { text };
};
