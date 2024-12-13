import Vue from "vue";
import BaseFixedTooltip from "@/components/base/base-tooltip/BaseFixedTooltip.vue";

Vue.directive("tooltip", {
  bind: (element, binding) => {
    const tooltipDiv = new Vue({
      render(h) {
        return h(BaseFixedTooltip, {
          props: {
            content: binding.value.content,
            top: this.top,
            left: this.left,
            open: binding.value.open,
            triggerElement: element,
          },
        });
      },
    }).$mount();

    document.body.appendChild(tooltipDiv.$el);
  },
});
