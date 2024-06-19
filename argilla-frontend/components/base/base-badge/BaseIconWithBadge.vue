<template>
  <BaseButton
    class="icon-with-badge"
    :data-title="tooltip"
    @on-click="onClickIcon"
    :tabIndex="-1"
  >
    <i
      :key="showBadge"
      class="icon-wrapper"
      v-badge="{
        showBadge: showBadge,
        verticalPosition: badgeVerticalPosition,
        horizontalPosition: badgeHorizontalPosition,
        borderColor: badgeBorderColor,
      }"
    >
      <svgicon
        :name="icon"
        :width="badgeSize"
        :height="badgeSize"
        :color="iconColor"
      />
    </i>
  </BaseButton>
</template>

<script>
export default {
  props: {
    url: {
      type: String,
    },
    icon: {
      type: String,
    },
    iconColor: {
      type: String,
      default: () => "white",
    },
    tooltip: {
      type: String,
    },
    showBadge: {
      type: Boolean,
      default: false,
    },
    badgeVerticalPosition: {
      type: String,
    },
    badgeHorizontalPosition: {
      type: String,
    },
    badgeBorderColor: {
      type: String,
    },
    badgeSize: {
      type: String,
      default: "22",
    },
  },
  methods: {
    onClickIcon() {
      this.$emit("click-icon");
    },
  },
};
</script>
