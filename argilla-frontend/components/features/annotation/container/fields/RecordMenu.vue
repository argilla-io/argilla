<template>
  <div class="record-menu">
    <BaseDropdown
      :freezing-page="visibleMetadataInfo"
      :visible="dropdownIsVisible"
      @visibility="onVisibility"
    >
      <template slot="dropdown-header">
        <BaseButton
          class="record-menu__header"
          :aria-label="
            (dropdownIsVisible ? 'Collapse' : 'Expand') +
            ' Record Dropdown for Extra Information'
          "
        >
          <svgicon name="kebab" width="20" height="20" aria-hidden="true" />
        </BaseButton>
      </template>
      <template slot="dropdown-content">
        <RecordMetadataInfo v-if="visibleMetadataInfo" :record="record" />
        <ul v-else class="record-menu__content">
          <li>
            <BaseButton @on-click="viewMetadata">
              {{ $t("viewMetadata") }}
            </BaseButton>
          </li>
          <li>
            <BaseButton @on-click="copyRecord">
              {{ $t("copyRecord") }}
            </BaseButton>
          </li>
        </ul>
      </template>
    </BaseDropdown>
  </div>
</template>

<script>
import "assets/icons/kebab";
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      dropdownIsVisible: false,
      visibleMetadataInfo: false,
    };
  },
  methods: {
    viewMetadata() {
      this.visibleMetadataInfo = true;
    },
    copyRecord() {
      this.dropdownIsVisible = false;
      this.$copyToClipboard(
        this.record.fields
          .map((field) => `${field.title}\n${field.content}`)
          .join("\n")
      );
    },
    onVisibility(isVisible) {
      this.visibleMetadataInfo = false;
      this.dropdownIsVisible = isVisible;
    },
  },
};
</script>

<style lang="scss" scoped>
.record-menu {
  &__header {
    padding: 0;
    color: var(--fg-secondary);
    margin-right: -$base-space;
    &:hover {
      color: var(--fg-primary);
    }
  }
  &__content {
    list-style: none;
    padding: $base-space;
    margin: 0;
    li {
      border-radius: $border-radius-s;
      transition: background-color 0.3s ease;
      &:hover {
        background: var(--bg-opacity-4);
        cursor: pointer;
        transition: background-color 0.3s ease;
      }
    }
    .button {
      display: block;
      max-width: 200px;
      text-align: left;
      padding: $base-space;
      font-weight: normal;
      @include truncate;
    }
  }
  :deep(.dropdown__header) {
    &:hover {
      background: none;
    }
  }
  :deep(.dropdown__content) {
    min-width: 100%;
    left: auto;
    right: 100%;
    top: 0;
  }
}
</style>
