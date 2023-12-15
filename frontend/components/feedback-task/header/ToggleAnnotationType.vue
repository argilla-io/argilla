<template>
  <div class="annotation-type-switch">
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isFocusMode }"
      @click="switchFocusMode()"
    >
      Focus
    </button>
    <button
      class="switch"
      :class="{ active: recordCriteria.page.isBulkMode }"
      @click="switchFocusMode()"
    >
      Bulk
    </button>
  </div>
</template>

<script>
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
.annotation-type-switch {
  display: flex;
  align-items: center;
  border-radius: $border-radius;
  overflow: hidden;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 30px;
  background-color: $black-4;
  border: none;
  color: $black-54;
  cursor: pointer;
  outline: none;
  transition: background-color 0.4s;
}

.switch.active {
  background-color: $black-54;
  color: palette(white);
}
</style>
