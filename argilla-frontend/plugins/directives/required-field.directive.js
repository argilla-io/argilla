import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put a asterisk :
//  v-required-field="{ show: true, color: 'blue'}"
//    => color (String) the color of the asterisk : black by default

Vue.directive("required-field", {
  bind: (element, binding, node) => {
    if (binding?.value) {
      const { color, show } = binding?.value ?? { show: true, color: "black" };

      if (!show) return;

      const text = document.createTextNode(" *");
      const textWrapper = document.createElement("span");
      textWrapper.setAttribute("title", "Required response");
      textWrapper.style.color = color;
      textWrapper.appendChild(text);

      node.context.$nextTick(() => {
        element.insertAdjacentElement("afterEnd", textWrapper);
      });
    }
  },
});
