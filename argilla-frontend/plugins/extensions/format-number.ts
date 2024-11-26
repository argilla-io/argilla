import Vue from "vue";

declare global {
  interface Navigator {
    languages: string[];
    userLanguage: string;
    systemLanguage: string;
  }
}

const locale = [
  ...(navigator.languages || []),
  navigator.language,
  navigator.userLanguage,
  navigator.systemLanguage,
].filter(Boolean);

Vue.filter("formatNumber", (value) => {
  return new Intl.NumberFormat(locale.length ? locale[0] : "en").format(value);
});
