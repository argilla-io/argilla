<template>
  <div class="filters" v-click-outside="onClickOutside">
    <div class="filters__tabs">
      <p
        v-for="group in groups"
        :key="group"
        :class="{ active: initialVisibleGroup === group || itemsAppliedOnGroup(group) }"
        @click="selectGroup(group)"
      >
        {{ group }}
        <span v-if="itemsAppliedOnGroup(group)">({{
          itemsAppliedOnGroup(group)
        }})</span>
      </p>
    </div>
    <div v-for="group in groups" :key="group">
      <div v-if="initialVisibleGroup === group" :class="['filters__tabs__content', filterList.filter((f) => f.group === group).length > 6 ? 'filters__tabs__content--large' : '']">
        <span
          v-for="filter in filterList.filter((f) => f.group === group)"
          :key="filter.id"
        >
          <SelectFilter
            v-if="filter.type === 'select'"
            class="filter"
            :filter="filter"
            @apply="onApply"
          />
          <FilterConfidence
            v-else
            class="filter"
            :filter="filter"
            @apply="onApply"
          />
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => ({
    initialVisibleGroup: undefined,
    filters: [
      {
        key: "predicted_as",
        name: "Predicted as",
        type: "select",
        group: "Predictions",
        placeholder: "Select labels"
      },
      {
        key: "predicted",
        name: "Predicted ok",
        type: "select",
        group: "Predictions",
        placeholder: "Select yes/no"
      },
      {
        key: "confidence",
        name: "Confidence",
        type: "confidence",
        group: "Predictions"
      },
      {
        key: "predicted_by",
        name: "Predicted by",
        type: "select",
        group: "Predictions",
        placeholder: "Select agents"
      },
      {
        key: "annotated_as",
        name: "Annotated as",
        type: "select",
        group: "Annotations",
        placeholder: "Select labels"
      },
      {
        key: "annotated_by",
        name: "Annotated by",
        type: "select",
        group: "Annotations",
        placeholder: "Select labels"
      },
      {
        key: "status",
        name: "Status",
        type: "select",
        group: "Status",
        placeholder: "Select options"
      },
    ],
  }),
  computed: {
    groups() {
      return [...new Set(this.filterList.map((f) => f.group))];
    },
    isMultiLabelRecord() {
      return this.dataset.results.records.some((record) => record.multi_label);
    },
    filterList() {
      const aggregations = this.dataset.results.aggregations;
      const filters = this.filters
        .map((filter) => {
          function isZero(number) {
            return number === 0;
          }
          return {
            ...filter,
            id: filter.key,
            options: aggregations[filter.key],
            selected: this.dataset.query[filter.key],
            disabled:
              (filter.key === "confidence" && this.isMultiLabelRecord) ||
              !aggregations[filter.key] ||
              !Object.entries(aggregations[filter.key]).length ||
              Object.values(aggregations[filter.key]).every(isZero),
          };
        })
        .filter(({ disabled }) => !disabled);

      const metadataFilters = Object.keys(aggregations.metadata).map((key) => {
        return {
          key: key,
          name: key,
          type: "select",
          group: "Metadata",
          placeholder: "Select options",
          id: key,
          options: aggregations.metadata[key],
          selected: this.dataset.query.metadata
            ? this.dataset.query.metadata[key] || []
            : [],
        };
      });
      const sortedMetadataFilters = metadataFilters.sort((a, b) =>
        a.key.toLowerCase() > b.key.toLowerCase() ? 1 : -1
      );
      return [...filters, ...sortedMetadataFilters];
    },
  },
  methods: {
    onClickOutside() {
      this.initialVisibleGroup = undefined;
    },
    itemsAppliedOnGroup(group) {
      return this.filterList
        .filter((f) => f.group === group)
        .flatMap((f) => f.selected)
        .filter((f) => f).length;
    },
    selectGroup(group) {
      this.initialVisibleGroup = group;
    },
    setInitialGroup() {
      if (!this.groups.includes(this.initialVisibleGroup)) {
        this.initialVisibleGroup = this.groups[0];
      }
    },
    onApply(filter, values) {
      this.initialVisibleGroup = undefined;
      if (filter.group === "Metadata") {
        this.$emit("applyMetaFilter", { filter: filter.key, values });
      } else {
        this.$emit("applyFilter", { filter: filter.key, values });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$number-size: 18px;
.filters {
  $this: &;
  position: relative;
  display: inline-block;
  width: 100%;
  z-index: 2;
  &__tabs {
    display: flex;
    &__content {
      width: 450px;
      position: absolute;
      top: calc(100% + 1em);
      box-shadow: 0 5px 11px 0 rgba(0,0,0,0.50);
      background: $lighter-color;
      padding: 3em 3em 2em 3em;
      border-radius: 5px;
      max-height: 550px;
      &--large {
        width: 910px;
        max-height: 80vh;
        overflow: auto;
        & > span {
          display: inline-block;
          width: 50%;
          &:nth-child(2n+1) {
            padding-right: 1em;
          }
        }
      }
    }
    p {
      cursor: pointer;
      position: relative;
      margin-bottom: 0;
      margin-top: 0;
      padding: 0.8em 1em;
      border-radius: 5px;
      margin-right: 1em;
      color: $font-secondary;
      @include font-size(15px);
      &:last-child {
        margin-right: 0;
      }
      &.active {
        background: palette(grey, smooth);
        color: $primary-color;
      }
    }
  }
}

.filter {
  display: block;
  margin-bottom: 1em;
  &__sort {
    // max-width: 144px;
    min-width: 150px;
    margin-right: 0;
    margin-left: 1em;
  }
}
</style>
