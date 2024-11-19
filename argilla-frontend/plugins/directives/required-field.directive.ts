import Vue from "vue";

// NOTE - to use this directive, add to your html text element where to put a asterisk :
//  v-required-field="{ show: true, color: 'blue'}"
//  => color (String) the color of the asterisk : black by default

Vue.directive("required-field", {
  bind(element, binding: { value: { show: boolean; color: string } }) {
    const span = document.createElement("span");
    span.textContent = " *";
    span.style.color = binding.value.color;
    span.setAttribute("title", "Required response");
    span.setAttribute("role", "mark");
    element.appendChild(span);
    span.style.display = binding.value.show ? "inline" : "none";
  },
  update(element, binding) {
    const span = element.querySelector("span");
    if (span) {
      span.style.display = binding.value.show ? "inline" : "none";
    }
  },
});
