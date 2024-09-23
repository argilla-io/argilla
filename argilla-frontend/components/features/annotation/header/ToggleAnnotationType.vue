<template>
  <div class="annotation-type-switch">
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isFocusMode }"
      @click="switchFocusMode()"
      :data-title="$t('focus_mode')"
    >
      <svgicon name="focus-mode" width="18" />
    </button>
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isBulkMode }"
      @click="switchBulkMode()"
      :data-title="$t('bulk_mode')"
    >
      <svgicon name="bulk-mode" width="18" />
    </button>
  </div>
</template>

<script>
import "assets/icons/focus-mode";
import "assets/icons/bulk-mode";
export default {
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  methods: {
    switchFocusMode() {
      this.recordCriteria.page.focusMode();

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
    switchBulkMode() {
      this.recordCriteria.page.bulkMode();

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
  },
};
</script>

<style scoped lang="scss">
$button-height: $base-space * 4;
$gutter: 2px;
.annotation-type-switch {
  display: flex;
  align-items: center;
  padding: $gutter;
  border-radius: $border-radius;
  background: var(--bg-opacity-4);
}

.switch {
  position: relative;
  display: inline-block;
  min-height: $button-height - $gutter * 2;
  border: none;
  color: var(--fg-secondary);
  background-color: transparent;
  border-radius: $border-radius - $gutter;
  cursor: pointer;
  outline: none;
  transition: background-color 0.4s;
  .svg-icon {
    fill: var(--bg-opacity-20);
  }
  &:hover,
  &.active:not(:hover) {
    background-color: var(--bg-accent-grey-2);
    .svg-icon {
      fill: var(--bg-opacity-54);
    }
  }
  &.active:not(:hover) {
    .annotation-type-switch:hover & {
      background-color: transparent;
    }
  }
}
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
