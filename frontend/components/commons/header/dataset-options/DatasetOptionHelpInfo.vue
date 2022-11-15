<template>
  <div>
    <base-button
      title="Info"
      :class="`dataset-option__button ${buttonClass}`"
      @click="showHelpInfo()"
    >
      <svgicon name="info" width="30" height="30"
    /></base-button>
    <component
      :visible="visible"
      @on-close="close()"
      :is="currentTaskHelpInfo"
    />
  </div>
</template>

<script>
export default {
  props: {
    task: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visible: false,
    };
  },
  computed: {
    currentTaskHelpInfo() {
      return `${this.task}HelpInfo`;
    },
    buttonClass() {
      return this.visible ? "--active" : null;
    },
  },
  methods: {
    showHelpInfo() {
      this.visible = !this.visible;
    },
    close() {
      this.visible = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-option {
  &__button {
    padding: calc($base-space / 4);
    &:hover,
    &.--active {
      background: $black-4;
    }
  }
}
</style>
