import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put the "(optional)" :
//  v-has-suggestions-field="true"

Vue.directive("has-suggestions", {
  bind: (element, binding) => {
    if (binding?.value) {
      const emoji = document.createTextNode("✨ ");
      const emojiWrapper = document.createElement("span");
      emojiWrapper.style.fontSize = "1.2em";
      textWrapper.appendChild(emoji);
      element.prepend(emojiWrapper);
    }
  },
});
