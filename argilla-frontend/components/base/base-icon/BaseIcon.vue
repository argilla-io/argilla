<template>
  <svgicon
    :name="iconName"
    :width="iconWidth"
    :height="iconHeight"
    :color="iconColor"
    aria-hidden="true"
  />
</template>

<script>
import "assets/icons";
export default {
  props: {
    iconName: {
      type: String,
      required: true,
    },
    iconWidth: {
      type: String,
      default: "16px",
    },
    iconHeight: {
      type: String,
      default: "16px",
    },
    iconColor: {
      type: String,
      default: "#4d4d4d",
    },
  },
};
</script>
