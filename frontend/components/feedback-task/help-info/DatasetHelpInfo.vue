<template>
  <div>
    <base-button
      title="Info"
      class="help-info__action-button"
      :class="buttonClass"
      @click="showHelpModal()"
    >
      <svgicon name="support" width="18" height="18" />Help</base-button
    >
    <lazy-base-modal
      modal-class="modal-auto"
      modal-position="modal-top-right"
      :modal-custom="true"
      :modal-visible="isModalVisible"
      @close-modal="close()"
    >
      <dataset-help-info-content />
      <div class="help-info__buttons">
        <base-button class="primary" @click="close()">Ok, got it!</base-button>
      </div>
    </lazy-base-modal>
  </div>
</template>

<script>
import "assets/icons/support";
export default {
  data() {
    return {
      isModalVisible: false,
    };
  },
  computed: {
    buttonClass() {
      return this.isModalVisible ? "--active" : null;
    },
  },
  methods: {
    showHelpModal() {
      this.isModalVisible = !this.isModalVisible;
    },
    close() {
      this.isModalVisible = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.help-info {
  &__action-button {
    padding: 0;
    color: $primary-color;
    &:hover,
    &.--active {
      color: darken($primary-color, 15%);
    }
  }
  &__buttons {
    display: flex;
    justify-content: right;
  }
}
</style>