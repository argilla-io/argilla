<template>
  <div>
    <base-button
      title="Info"
      class="dataset-option__button"
      :class="buttonClass"
      @click="showHelpInfo()"
    >
      <svgicon name="support" width="18" height="18" />Help</base-button
    >
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
    padding: 0;
    color: $primary-color;
    &:hover,
    &.--active {
      color: darken($primary-color, 10%);
    }
  }
}
</style>
