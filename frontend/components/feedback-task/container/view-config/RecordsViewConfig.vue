<template>
  <BaseDropdown
    class="view-config"
    :visible="dropdownIsVisible"
    @visibility="onChangeDropDownVisibility"
    ><template slot="dropdown-header"
      ><span
        :data-title="
          !dropdownIsVisible && $t('bulkAnnotation.recordsViewSettings')
        "
        ><svgicon
          class="view-config__icon"
          width="20"
          height="20"
          color="#989898"
          name="settings" /></span
    ></template>
    <template slot="dropdown-content">
      <div class="view-config__content">
        <span
          class="view-config__text"
          v-text="$t('bulkAnnotation.recordsHeight')"
        />
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
export default {
  data() {
    return {
      dropdownIsVisible: false,
      recordsViewConfig: {
        height: [
          {
            id: "fixedHeight",
          },
          {
            id: "defaultHeight",
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
  @include font-size(13px);
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    min-width: 200px;
    padding: $base-space;
  }
  :deep(.radio-button) {
    @include font-size(13px);
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
  @extend %has-tooltip--bottom;
  @extend %tooltip-mini;
}
</style>
