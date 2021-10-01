import Vue from 'vue'

const locale = [
  ...(navigator.languages || []),
  navigator.language,
  navigator.browserLanguage,
  navigator.userLanguage,
  navigator.systemLanguage
].filter(Boolean)

Vue.filter("formatNumber", function (value) {
  return new Intl.NumberFormat(locale.length ? locale[0] : 'en').format(value);
});

Vue.filter("percent", function (value) {
  const formatter = new Intl.NumberFormat(locale.length ? locale[0] : 'en', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return formatter.format(value)
});
