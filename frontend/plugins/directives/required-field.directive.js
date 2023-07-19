import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put a asterisk :
//  v-required-field="{ color: 'blue'}"
//    => color (String) the color of the asterisk : black by default

Vue.directive("required-field", {
  bind: (element, binding) => {
    if (binding?.value) {
      const { color } = binding?.value ?? { color: "black" };

      const text = document.createTextNode(" *");
      const textWrapper = document.createElement("span");
      textWrapper.style.color = color;
      textWrapper.appendChild(text);
      element.appendChild(textWrapper);
    }
  },
});
