import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put the "(optional)" :
//  v-optional-field="true"

Vue.directive("optional-field", {
  bind: (element, binding, node) => {
    if (binding?.value) {
      const text = document.createTextNode(" (optional)");
      const textWrapper = document.createElement("span");
      textWrapper.style.fontSize = "0.8em";
      textWrapper.style.color = "rgba(0, 0, 0, 0.87)";
      textWrapper.style.fontWeight = "400";

      textWrapper.appendChild(text);

      node.context.$nextTick(() => {
        element.insertAdjacentElement("afterEnd", textWrapper);
      });
    }
  },
});
