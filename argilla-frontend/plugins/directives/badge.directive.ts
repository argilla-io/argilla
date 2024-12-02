import Vue from "vue";

// NOTE - to use this directive, add to your html element where to put a badge :
//  v-badge="{showBadge: true,  verticalPosition: 'top',  horizontalPosition: 'right'}"
//    => showBadge (Boolean) to show or not the badge : true or false
//    => verticalPosition (String) vertical position : 'top' or 'bottom'
//    => horizontalPosition (String) horizontal position : 'right' or 'left'
//    => size (String) height and size of the badge: '10px

Vue.directive("badge", {
  bind: (
    element,
    binding: {
      value: {
        showBadge: boolean;
        verticalPosition: string;
        horizontalPosition: string;
        backgroundColor: string;
        borderColor: string;
        size: string;
      };
    }
  ) => {
    const { showBadge } = binding.value;
    if (showBadge) {
      const {
        verticalPosition,
        horizontalPosition,
        backgroundColor,
        borderColor,
        size,
      } = binding.value;

      element.style.position = "relative";
      const badge = document.createElement("div");
      badge.setAttribute("id", `${element.id}Badge`);
      badge.style.position = "absolute";
      badge.style.backgroundColor = backgroundColor || "#ff675f";
      badge.style.width = size || "14px";
      badge.style.height = size || "14px";
      badge.style.borderRadius = "5em";
      badge.style.border = `2px ${borderColor ?? "transparent"} solid`;

      switch (verticalPosition) {
        case "top":
          badge.style.top = "-3px";
          break;
        case "bottom":
          badge.style.bottom = "-3px";
          break;
      }

      switch (horizontalPosition) {
        case "right":
          badge.style.right = "-3px";
          break;
        case "left":
          badge.style.left = "-3px";
          break;
      }

      element.appendChild(badge);
    }
  },
});
