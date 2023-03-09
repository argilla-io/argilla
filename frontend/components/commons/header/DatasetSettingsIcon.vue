<template>
  <BaseIconWithBadge
    tooltip="Dataset settings"
    :show-badge="visibleBadge"
    badge-vertical-position="top"
    badge-horizontal-position="right"
    badge-border-color="#212121"
    icon="settings"
    @click-icon="onClickSettingsIcon"
  />
</template>

<script>
export default {
  props: {
    visibleBadge: {
      type: Boolean,
    },
  },
  methods: {
    onClickSettingsIcon() {
      this.$emit("click-settings-icon");
    },
  },
};
</script>
<style lang="scss" scoped>
.button-settings {
  margin-right: $base-space;
  &[data-title] {
    position: relative;
    overflow: visible;
    @extend %has-tooltip--bottom;
    &:before,
    &:after {
      margin-top: calc($base-space/2);
    }
  }
}
</style>
