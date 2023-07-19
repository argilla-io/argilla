import Vue from "vue";

const sparkIcon = {
  add: (element, binding) => {
    const emoji = document.createTextNode("✨ ");
    const emojiWrapper = document.createElement("span");
    emojiWrapper.setAttribute("data-title", binding?.value.tooltip);
    emojiWrapper.style.fontSize = "1.2em";
    emojiWrapper.appendChild(emoji);
    element.prepend(emojiWrapper);
  },
  remove: (element) => {
    element.removeChild(element.childNodes[0]);
  },
};

Vue.directive("prefix-star", {
  update: (element, binding) => {
    if (binding?.value.show) {
      sparkIcon.add(element, binding);
    } else {
      sparkIcon.remove(element);
    }
  },
  bind: (element, binding) => {
    if (binding?.value.show) {
      sparkIcon.add(element, binding);
    }
  },
});
