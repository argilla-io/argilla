// style for button to open formular
import Vue from "vue";

//NOTE - to use this directive, add to your html element where to put a badge :
//  v-badge="{showBadge: true,  verticalPosition: 'top',  horizontalPosition: 'right'}"
//    => showBadge (Boolean) to show or not the badge : true or false
//    => verticalPosition (String) vertical position : 'top' or 'bottom'
//    => horizontalPosition (String) horizontal position : 'right' or 'left'

Vue.directive("badge", {
  bind: (element, binding) => {
    const { showBadge } = binding.value;
    if (showBadge) {
      const { verticalPosition, horizontalPosition, backgroundColor } =
        binding.value;
      element.style.position = "relative";
      const badge = document.createElement("div");
      badge.style.position = "absolute";
      badge.style.backgroundColor = backgroundColor || "#ff675f";
      badge.style.width = "10px";
      badge.style.height = "10px";
      badge.style.borderRadius = "5em";

      if (verticalPosition === "top") {
        badge.style.top = "-7px";
      } else if (verticalPosition === "bottom") {
        badge.style.bottom = "-7px";
      }

      if (horizontalPosition === "right") {
        badge.style.right = "-7px";
      } else if (horizontalPosition === "left") {
        badge.style.left = "-7px";
      }
      element.appendChild(badge);
    }
  },
});
