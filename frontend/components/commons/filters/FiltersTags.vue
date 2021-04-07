<template>
  <div class="filters__tags">
    <BiomeIsotipo
      v-if="fixedHeader"
      class="filters__tags__logo"
      :minimal="true"
    />
    <span v-for="(filter, index) in formattedFilters" :key="index">
      <span class="tag">
        <span>{{ filter.name }} = {{ filter.value }}</span>
        <i
          aria-hidden="true"
          tabindex="1"
          class="tag-icon"
          @click="clearFilter(filter)"
        />
      </span>
    </span>

    <span v-if="severalFiltersApplied" class="tag tag--all">
      <span>Clear all</span>
      <i
        aria-hidden="true"
        tabindex="1"
        class="tag-icon"
        @click="$emit('clearAll')"
      />
    </span>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
    fixedHeader: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    filters: [
      { id: "annotated_as", name: "Annotated as" },
      { id: "annotated_by", name: "Annotated by" },
      { id: "predicted_as", name: "Predicted as" },
      { id: "predicted_by", name: "Predicted by" },
      { id: "predicted", name: "Predicted" },
      { id: "confidence", name: "Confidence" },
      { id: "status", name: "Status" },
      { id: "multi_label", name: "Multilabel" },
      { id: "text", name: "Search" },
    ],
  }),
  computed: {
    formattedFilters() {
      const filters = this.filters.flatMap(({ id, name }) => {
        const value = this.dataset.query[id];
        if (value === undefined) {
          return [];
        }
        if (Array.isArray(value)) {
          return value.map((value) => ({ id, name, value }));
        }
        return [{ id, name, value }];
      });
      if (this.dataset.query.metadata) {
        const metadataFilters = Object.keys(
          this.dataset.query.metadata
        ).flatMap((key) => {
          const value = this.dataset.query.metadata[key] || [];
          return value.map((value) => ({
            group: "Metadata",
            id: key,
            name: `metadata.${key}`,
            value,
          }));
        });
        return [...filters, ...metadataFilters];
      }
      return filters;
    },
    severalFiltersApplied() {
      return this.formattedFilters.length > 1;
    },
  },
  methods: {
    clearFilter(filter) {
      if (filter.group === "Metadata") {
        this.$emit("clearMetaFilter", filter.id, filter.value);
      } else {
        this.$emit("clearFilter", filter.id, filter.value);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.filters {
  &__tags {
    // min-height: 40px;
    @extend %clearfix;
    position: relative;
    text-align: left;
    &--empty {
      border-bottom: none;
    }
    > * {
      width: auto;
    }
    &__logo {
      float: left;
      margin-right: 1.5em;
      margin-top: 0.5em;
      margin-left: 1.5em;
    }
    .fixed-header & {
      min-height: 40px;
      width: calc(100% - 250px);
      z-index: 1;
      border-bottom: 0;
      max-width: 930px;
      @include media(">xxl") {
        max-width: 1330px;
      }
    }
  }
}

.tags {
  min-height: 44px;
  display: block;
  padding: 10px 40px 0 8px;
  border-radius: 2px;
  border: 1px solid $line-light-color;
  background: $line-light-color;
  overflow: hidden;
  span {
    margin-right: 3px;
  }
}

.filters__tags__logo {
  float: left;
  margin-right: 1.5em;
  margin-top: 0.5em;
  margin-left: 1.5em;
}

// filters tag
.tag {
  position: relative;
  padding: 0.5em 1em;
  border-radius: 0;
  line-height: 1;
  min-height: 41px;
  background: $lighter-color;
  border-right: 1px solid $line-light-color;
  border-bottom: 1px solid $line-light-color;
  color: $secondary-color;
  float: left;
  display: flex;
  align-items: center;
  > span {
    display: inline-block;
    white-space: nowrap;
    overflow: hidden;
    max-width: 500px;
    text-overflow: ellipsis;
    line-height: 2em;
    vertical-align: middle;
  }
  &__field {
    font-weight: lighter;
    text-transform: uppercase;
  }
  &--all {
    color: $primary-color;
  }
}

.tag-icon {
  outline: 0;
  cursor: pointer;
  margin-left: 1em;
  font-weight: 700;
  font-style: initial;
  width: 22px;
  text-align: center;
  line-height: 22px;
  transition: all 0.2s ease;
  border-radius: 5px;
}

.tag-icon:after {
  content: "✕";
  font-weight: bold;
  color: $primary-color;
  font-size: 14px;
}
</style>
