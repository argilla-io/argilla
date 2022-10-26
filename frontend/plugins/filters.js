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

Vue.filter("percent", function (value, min = 2, max = 3) {
  const browserLanguage = locale[0] || "en";
  const formatterOptions = {
    style: "percent",
    minimumFractionDigits: min,
    maximumFractionDigits: max,
  };

  const formatter = new Intl.NumberFormat(browserLanguage, formatterOptions);
  return formatter.format(value);
});

Vue.filter("capitalize", function (value) {
  const capitalize = ([firstLetter, ...restOfWord]) =>
    firstLetter.toUpperCase() + restOfWord.join("");

  return capitalize(value);
});
