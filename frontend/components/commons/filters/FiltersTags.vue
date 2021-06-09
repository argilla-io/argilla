<template>
  <div class="filters__tags">
    <RubrixIsotipo
      v-if="fixedHeader"
      class="filters__tags__logo"
      :minimal="true"
    />
    <span v-for="(filter, index) in formattedFilters" :key="index">
      <span class="tag">
        <span :title="`${filter.name} = ${filter.value}`">{{ filter.name }} = {{ filter.value }}</span>
        <i
          aria-hidden="true"
          tabindex="1"
          class="tag-icon"
          @click="clearFilter(filter)"
        />
      </span>
    </span>

    <span @click="$emit('clearAll')" v-if="severalFiltersApplied" class="tag tag--all">
      <span>Remove all</span>
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
    margin-top: 10px;
    width: calc(100% - 150px);
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
      margin-left: auto;
      z-index: 1;
      border-bottom: 0;
      margin-top: 3px;
      padding-right: 150px;
    }
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
  padding: 0.2em 1em;
  border-radius: 0;
  line-height: 1;
  min-height: 30px;
  background: palette(grey, smooth);
  color: $primary-color;
  float: left;
  display: flex;
  align-items: center;
  margin-right: 5px;
  margin-bottom: 5px;
  @include font-size(13px);
  .fixed-header & {
    margin-bottom: 3px;
  }
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
    cursor: pointer;
    color: $font-secondary;
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
