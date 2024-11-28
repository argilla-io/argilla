<template>
  <div class="export-to-hub">
    <BaseButton
      class="primary export-to-hub__button"
      :loading="isExporting"
      :disabled="isExporting"
      @click.prevent="exportToHub"
    >
      Export to hub
    </BaseButton>
  </div>
</template>

<script>
import { useExportToHubViewModel } from "./useExportToHubViewModel";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return useExportToHubViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.export-to-hub {
  position: relative;
  margin-left: auto;
  margin-right: 0;

  &__button.button {
    background: hsl(0, 1%, 18%);
    &:hover {
      background: hsl(0, 1%, 22%);
    }
  }
}
</style>
