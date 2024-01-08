<template>
  <BaseIconWithBadge
    class="button-settings"
    :tooltip="$t('settings.title')"
    :show-badge="showBadge"
    badge-vertical-position="top"
    badge-horizontal-position="right"
    badge-border-color="#212121"
    icon="settings"
  />
</template>

<script>
export default {
  name: "DatasetSettingsIconFeedbackTaskComponent",
  props: {
    showBadge: {
      type: Boolean,
      default: false,
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
