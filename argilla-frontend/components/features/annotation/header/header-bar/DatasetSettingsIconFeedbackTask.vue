<template>
  <BaseIconWithBadge
    class="button-settings"
    :tooltip="$t('settings.title')"
    :show-badge="showBadge"
    badge-vertical-position="top"
    badge-horizontal-position="right"
    badge-border-color="#212121"
    badge-size="20"
    icon="settings"
    :aria-label="$t('settings.title')"
  />
</template>

<script>
export default {
  name: "DatasetSettingsIconFeedbackTask",
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
  padding: $base-space;
  overflow: visible;
  flex-shrink: 0;
  &[data-title] {
    @include tooltip-mini("bottom");
  }
}
</style>
