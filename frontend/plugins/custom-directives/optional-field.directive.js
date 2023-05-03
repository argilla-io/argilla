import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put the "(optional)" :
//  v-optional-field="true"

Vue.directive("optional-field", {
  bind: (element, binding) => {
    if (binding?.value) {
      const text = document.createTextNode(" (optional)");
      const textWrapper = document.createElement("span");
      textWrapper.style.fontSize = "0.9rem";

      textWrapper.appendChild(text);
      element.appendChild(textWrapper);
    }
  },
});
