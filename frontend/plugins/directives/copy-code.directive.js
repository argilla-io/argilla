import Vue from "vue";
import BaseCodeVue from "~/components/base/base-code/BaseCode.vue";

Vue.directive("copy-code", {
  bind: (el, _, node) => {
    const preElements = el.getElementsByTagName("PRE");

    for (const pre of preElements) {
      const code = pre.children[0] ? pre.children[0].innerText : pre.innerText;

      const container = document.createElement("div");
      container.style.position = "relative";

      const baseCodeComponent = Vue.extend(BaseCodeVue);
      const instance = new baseCodeComponent({
        propsData: { code },
        $copyToClipboard: node.context.$copyToClipboard,
      });

      instance.$mount();

      pre.parentNode.replaceChild(container, pre);

      container.appendChild(pre);
      container.appendChild(instance.$el);
    }
  },
});
