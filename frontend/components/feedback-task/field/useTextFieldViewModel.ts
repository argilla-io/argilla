import { computed, ComputedRef, ref } from "vue-demi";

export const useTextFieldViewModel = (props: {
  fieldText: string;
  stringToHighlight: string;
  useMarkdown: boolean;
}) => {
  const text: ComputedRef<string> = computed(() => {
    if (props.stringToHighlight.length === 0 || !props.useMarkdown)
      return props.fieldText;

    const newText = ref(props.fieldText);

    const splittedStringToHightlight = props.stringToHighlight.split(/\s+/);

    splittedStringToHightlight.forEach((word) => {
      if (word.includes("`")) return;

      newText.value = getHighlightedSentenceFor(word, newText.value);
    });

    return newText.value;
  });

  const getHighlightedSentenceFor = (aWord: string, aText: string) => {
    const wordsWithoutMarkown = getWordsWithoutMarkown(aText);

    if (!wordsWithoutMarkown?.toLowerCase().includes(aWord?.toLowerCase()))
      return aText;

    const specialChars = /[`!@#$%^&*()_\-+=[\]{};':"\\|,.<>/?~ ]/;

    const escapeCharacters = aWord.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

    const regexExactWord = specialChars.test(aWord)
      ? new RegExp(`${escapeCharacters}`, "gi")
      : new RegExp(`\\b${escapeCharacters}\\b`, "gi");

    return aText.replace(regexExactWord, (match) => htmlHighlightFor(match));
  };

  const getWordsWithoutMarkown = (aText: string) => {
    const regexToSeparateMarkdown = /[^`]+|`[^`]*`/g;

    const matchesWithoutMarkdown = aText
      .match(regexToSeparateMarkdown)
      ?.filter((match) => !match.includes("`"))
      .join("");

    return matchesWithoutMarkdown;
  };

  const htmlHighlightFor: (aText: string) => string = (aText: string) =>
    `<span class="highlight-text">${aText}</span>`;

  return { text };
};
