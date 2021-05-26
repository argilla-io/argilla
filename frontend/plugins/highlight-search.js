
export default ({ app }, inject) => {
  const highlightSearch = function(query, text){
    const escapedText = this.text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
    if (!query) {
      return escapedText;
    }
    let q = query.replace(/^"|"$/g, '');
    return escapedText
      .toString()
      .replace(
        new RegExp(q, "gi"),
        (match) => `<span class="highlight-text">${match}</span>`
      );
  }
  inject('highlightSearch', highlightSearch)
}