import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put the "(optional)" :
//  v-has-suggestions-field='{ show: false, tooltip: 'text' }'

Vue.directive("has-suggestions", {
  bind: (element, binding) => {
    if (binding?.value.show) {
      const emoji = document.createTextNode("✨ ");
      const emojiWrapper = document.createElement("span");
      emojiWrapper.setAttribute("data-title", binding?.value.tooltip);
      emojiWrapper.style.fontSize = "1.2em";
      emojiWrapper.appendChild(emoji);
      element.prepend(emojiWrapper);
    }
  },
});
