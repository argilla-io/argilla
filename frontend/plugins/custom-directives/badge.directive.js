// style for button to open formular
import Vue from "vue";

//NOTE - to use this directive, add to your html element where to put a badge :
//  v-badge="{showBadge: true,  verticalPosition: 'top',  horizontalPosition: 'right'}"
//    => showBadge (Boolean) to show or not the badge : true or false
//    => verticalPosition (String) vertical position : 'top' or 'bottom'
//    => horizontalPosition (String) horizontal position : 'right' or 'left'

Vue.directive("badge", {
  bind: (element, binding) => {
    if (binding.value.showBadge) {
      element.style.position = "relative";
      const badge = document.createElement("div");
      badge.style.position = "absolute";
      badge.style.backgroundColor = binding.value.backgroundColor || "#ff675f";
      badge.style.width = "10px";
      badge.style.height = "10px";
      badge.style.borderRadius = "5em";

      if (binding.value.verticalPosition === "top") {
        badge.style.top = "-7px";
      } else if (binding.value.verticalPosition === "bottom") {
        badge.style.bottom = "-7px";
      }

      if (binding.value.horizontalPosition === "right") {
        badge.style.right = "-7px";
      } else if (binding.value.horizontalPosition === "left") {
        badge.style.left = "-7px";
      }
      element.appendChild(badge);
    }
  },
});
