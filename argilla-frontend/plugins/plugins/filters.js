import Vue from "vue";

const locale = [
  ...(navigator.languages || []),
  navigator.language,
  navigator.browserLanguage,
  navigator.userLanguage,
  navigator.systemLanguage,
].filter(Boolean);

Vue.filter("formatNumber", (value) => {
  return new Intl.NumberFormat(locale.length ? locale[0] : "en").format(value);
});
