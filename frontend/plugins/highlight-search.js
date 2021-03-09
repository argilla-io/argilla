
export default ({ app }, inject) => {
  const highlightSearch = function(query, text){
    if (!query) {
      return text;
    }
    return text
      .toString()
      .replace(
        new RegExp(query, "gi"),
        (match) => `<span class="highlight-text">${match}</span>`
      );
  }
  inject('highlightSearch', highlightSearch)
}