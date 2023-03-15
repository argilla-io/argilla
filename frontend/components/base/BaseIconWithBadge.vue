<template>
  <BaseButton
    class="icon-with-badge"
    :data-title="tooltip"
    @on-click="onClickIcon"
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
      <svgicon :name="icon" width="22" height="22" color="white" />
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
  },
  methods: {
    onClickIcon() {
      this.$emit("click-icon");
    },
  },
};
</script>
