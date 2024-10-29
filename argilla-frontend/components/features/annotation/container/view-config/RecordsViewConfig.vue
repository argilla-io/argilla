<template>
  <BaseDropdown
    class="view-config"
    :visible="dropdownIsVisible"
    @visibility="onChangeDropDownVisibility"
    ><template slot="dropdown-header"
      ><BaseButton
        class="view-config__button"
        :data-title="
          !dropdownIsVisible && $t('bulkAnnotation.recordsViewSettings')
        "
      >
        <svgicon
          class="view-config__icon"
          width="20"
          height="20"
          name="change-height"
          aria-hidden="true"/></BaseButton
    ></template>
    <template slot="dropdown-content">
      <div class="view-config__content">
        <BaseRadioButton
          v-for="option in recordsViewConfig.height"
          :key="option.id"
          :id="option.id"
          :name="option.id"
          :value="option.id"
          v-model="recordHeightValue"
        >
          {{ $t(`bulkAnnotation.${option.id}`) }}
        </BaseRadioButton>
      </div></template
    ></BaseDropdown
  >
</template>

<script>
import "assets/icons/change-height";
export default {
  data() {
    return {
      dropdownIsVisible: false,
      recordsViewConfig: {
        height: [
          {
            id: "defaultHeight",
          },
          {
            id: "fixedHeight",
          },
        ],
      },
    };
  },
  props: {
    recordHeight: {
      type: String,
      default: false,
    },
  },
  model: {
    prop: "recordHeight",
    event: "change",
  },
  computed: {
    recordHeightValue: {
      get() {
        return this.recordHeight;
      },
      set(newValue) {
        this.$emit("change", newValue);
      },
    },
  },
  methods: {
    onChangeDropDownVisibility(isVisible) {
      this.dropdownIsVisible = isVisible;
    },
  },
};
</script>

<style lang="scss" scoped>
.view-config {
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space * 2;
    min-width: 200px;
    padding: $base-space;
  }
  &__button.button {
    padding: 0;
  }
  :deep(.radio-button) {
    margin: 0;
  }
  :deep(.dropdown__header) {
    &:hover {
      background: transparent;
    }
  }
}
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
