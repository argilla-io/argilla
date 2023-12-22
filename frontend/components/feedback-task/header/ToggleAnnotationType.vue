<template>
  <div class="annotation-type-switch">
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isFocusMode }"
      @click="switchFocusMode()"
      :data-title="$t('focus_mode')"
    >
      <svgicon name="focus-mode" />
    </button>
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isBulkMode }"
      @click="switchFocusMode()"
      :data-title="$t('bulk_mode')"
    >
      <svgicon name="bulk-mode" />
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
      if (this.recordCriteria.page.isFocusMode) {
        this.recordCriteria.page.bulkMode();
      } else {
        this.recordCriteria.page.focusMode();
      }

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
  background: $black-4;
}

.switch {
  position: relative;
  display: inline-block;
  min-height: $button-height - $gutter * 2;
  border: none;
  color: $black-54;
  background-color: transparent;
  border-radius: $border-radius - $gutter;
  cursor: pointer;
  outline: none;
  transition: background-color 0.4s;
  &:hover,
  &.active:not(:hover) {
    background-color: palette(white);
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
  @extend %has-tooltip--bottom;
  @extend %tooltip-mini;
}
</style>
