import Vue from "vue";

const locale = [
  ...(navigator.languages || []),
  navigator.language,
  navigator.browserLanguage,
  navigator.userLanguage,
  navigator.systemLanguage,
].filter(Boolean);

Vue.filter("formatNumber", function (value) {
  return new Intl.NumberFormat(locale.length ? locale[0] : "en").format(value);
});

Vue.filter("percent", function (value, min, max) {
  const formatter = new Intl.NumberFormat(locale.length ? locale[0] : "en", {
    style: "percent",
    minimumFractionDigits: min !== undefined ? min : 2,
    maximumFractionDigits: max !== undefined ? max : 3,
  });
  return formatter.format(value);
});

Vue.filter("capitalize", function (value) {
  const textInLowerCase = value.toLowerCase();
  const capitalize = ([firstLetter, ...restOfWord]) =>
    firstLetter.toUpperCase() + restOfWord.join("");

  return capitalize(textInLowerCase);
});
