import Vue from 'vue'

Vue.filter("formatNumber", function (value) {
  const locale = [
    ...(navigator.languages || []),
    navigator.language,
    navigator.browserLanguage,
    navigator.userLanguage,
    navigator.systemLanguage
  ].filter(Boolean)
  return new Intl.NumberFormat(locale.length ? locale[0] : 'en').format(value);
});
