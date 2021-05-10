<template>
  <div class="metadata">
    <p
      v-for="name in inputs"
      :key="name.index"
      class="metadata__title"
      :title="name"
    >
      <span v-if="!Array.isArray(name)">{{ name | truncate(100) }}</span>
    </p>
    <div class="metadata__container">
      <div v-for="(value, key) in sortedMetadataItems" :key="key">
        <div
          :class="[
            'metadata__blocks',
            { '--selected': isFilterSelected(key, value) },
            { '--disabled': isFilterApplied(key, value) },
          ]"
        >
          <div class="metadata__block">
            {{ key }}
            <div class="metadata__block__item">
              {{ value }}
            </div>
          </div>
          <ReButton
            class="metadata__block__button button-clear"
            @click="addFilter(key, value)"
          >
            Filter
          </ReButton>
        </div>
      </div>
    </div>
    <div class="metadata__buttons">
      <ReButton
        class="button-tertiary--small button-tertiary--outline"
        @click="$emit('cancel')"
      >
        Cancel
      </ReButton>
      <ReButton
        :disabled="disableButton"
        class="button-primary--small"
        @click="applySelectedFilters()"
      >
        Apply
      </ReButton>
    </div>
  </div>
</template>

<script>
export default {
  filters: {
    truncate(string, value) {
      if (string.length > value) {
        return `${string.substring(0, value)}...`;
      }
      return string;
    },
  },
  props: {
    metadataItems: {
      type: Object,
      required: true,
    },
    inputs: {
      type: Object,
      required: true,
    },
    appliedFilters: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => ({
    selectedKeys: [],
    metadata: {},
    disableButton: true,
  }),
  computed: {
    sortedMetadataItems() {    
      return Object.keys(this.metadataItems).sort().reduce((r, k) => (r[k] = this.metadataItems[k], r), {});
    },
  },
  methods: {
    addFilter(key, value) {
      let meta = { ...this.metadata };
      meta[key] ? (meta[key] = undefined) : (meta[key] = value);
      this.metadata = Object.fromEntries(
        Object.entries(meta).filter(([key, value]) => value)
      );
      this.disableButton = false;
    },
    applySelectedFilters() {
      this.$emit(
        "metafilterApply",
        Object.fromEntries(
          Object.entries(this.metadata).map(([k, v]) => [
            k,
            (this.appliedFilters[k] || []).concat([v]),
          ])
        )
      );
      this.disableButton = true;
    },
    isFilterSelected(key, value) {
      return this.metadata[key] || [].indexOf(value) !== -1 ? true : false;
    },
    isFilterApplied(key, value) {
      return this.appliedFilters && this.appliedFilters[key]
        ? this.appliedFilters[key].includes(value)
        : false;
    },
  },
};
</script>

<style lang="scss" scoped>
.metadata {
  position: relative;
  max-width: 500px;
  margin: auto;
  pointer-events: all;
  &__title {
    color: $font-dark-color;
    font-weight: 600;
    margin-top: 0;
    margin-right: 2em;
    white-space: pre-line;
    display: none;
    &:nth-child(-n + 5) {
      display: block;
    }
  }
  &__container {
    max-height: 50vh;
    overflow-y: auto;
    margin-right: -1em;
    padding-right: 1em;
  }
  &__blocks {
    display: flex;
    border-bottom: 1px solid $line-smooth-color;
    align-items: center;
    &.--selected {
      color: $secondary-color;
    }
    &.--disabled {
      color: $secondary-color;
      opacity: 0.4;
      pointer-events: none;
    }
  }
  &__block {
    padding: 1em 0;
    margin-right: 0.5em;
    &__item {
      word-break: break-word;
      min-width: 200px;
      text-align: left;
      white-space: pre-line;
      &:first-child {
        color: $font-dark-color;
        margin-bottom: 0.5em;
        .--selected & {
          color: $secondary-color;
        }
      }
    }
    &__button {
      .--selected & {
        color: $secondary-color;
      }
      margin: auto 0 auto auto;
      overflow: visible;
    }
  }
  &__buttons {
    display: block;
    text-align: right;
    margin-top: 2em;
    .re-button {
      margin-bottom: 0;
    }
  }
}
</style>
