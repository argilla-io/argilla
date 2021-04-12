
export default ({ app }, inject) => {
  const highlightSearch = function(query, text){
    if (!query) {
      return text;
    }
    let q = query.replace(/^"|"$/g, '');
    return text
      .toString()
      .replace(
        new RegExp(q, "gi"),
        (match) => `<span class="highlight-text">${match}</span>`
      );
  }
  inject('highlightSearch', highlightSearch)
}