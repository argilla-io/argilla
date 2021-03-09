<template>
  <div class="filters">
    <div class="filters__tabs">
      <p
        v-for="group in groups"
        :key="group"
        :class="{ active: initialVisibleGroup === group }"
        @click="selectGroup(group)"
      >
        {{ group }}
        <span v-if="itemsAppliedOnGroup(group)" class="filters__tabs__number">{{
          itemsAppliedOnGroup(group)
        }}</span>
      </p>
    </div>
    <div v-for="group in groups" :key="group">
      <div v-if="initialVisibleGroup === group">
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
    initialVisibleGroup: "Predictions",
    filters: [
      {
        key: "predicted_as",
        name: "Predicted as",
        type: "select",
        group: "Predictions",
      },
      {
        key: "predicted",
        name: "Predicted",
        type: "select",
        group: "Predictions",
      },
      {
        key: "confidence",
        name: "Confidence",
        type: "confidence",
        group: "Predictions",
      },
      {
        key: "predicted_by",
        name: "Predicted by",
        type: "select",
        group: "Predictions",
      },
      {
        key: "annotated_as",
        name: "Annotated as",
        type: "select",
        group: "Annotations",
      },
      {
        key: "status",
        name: "Status",
        type: "select",
        group: "Annotations",
      },
      {
        key: "annotated_by",
        name: "Annotated by",
        type: "select",
        group: "Annotations",
      },
    ],
  }),
  watch: {
    groups() {
      this.setInitialGroup();
    }
  },
  computed: {
    groups() {
      return [...new Set(this.filterList.map((f) => f.group))];
    },
    filterList() {
      const aggregations = this.dataset.results.aggregations;
      const filters = this.filters
        .map((filter) => {
          return {
            ...filter,
            id: filter.key,
            options: aggregations[filter.key],
            selected: this.dataset.query[filter.key],
            disabled:
              !aggregations[filter.key] ||
              !Object.entries(aggregations[filter.key]).length,
          };
        })
        .filter(({ disabled }) => !disabled);

      const metadataFilters = Object.keys(aggregations.metadata).map((key) => {
        return {
          key: key,
          name: key,
          type: "select",
          group: "Metadata",
          id: key,
          options: aggregations.metadata[key],
          selected: this.dataset.query.metadata
            ? this.dataset.query.metadata[key] || []
            : [],
        };
      });

      return [...filters, ...metadataFilters];
    },
  },
  mounted() {
    this.setInitialGroup()
  },
  methods: {
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
  display: inline-block;
  width: 100%;
  z-index: 2;
  &__tabs {
    display: flex;
    &__number {
      position: relative;
      color: $font-medium-color;
      z-index: 1;
      position: absolute;
      height: $number-size;
      width: $number-size;
      text-align: center;
      top: -5px;
      right: -5px;
      @include font-size(10px);
      &:before {
        content: "";
        box-shadow: $shadow;
        background: $lighter-color;
        border-radius: 50%;
        height: $number-size;
        width: $number-size;
        position: absolute;
        right: 0;
        z-index: -1;
      }
    }
    p {
      cursor: pointer;
      position: relative;
      margin-top: 0;
      padding: 0.3em 1em;
      border: 1px solid $line-smooth-color;
      margin-right: -1px;
      &:last-child {
        margin-right: 0;
      }
      &.active {
        border: 1px solid $secondary-color;
        background: $secondary-color;
        color: $lighter-color;
      }
    }
  }
}

.filter {
  vertical-align: bottom;
  float: left;
  margin-bottom: 0;
  text-align: left;
  position: relative;
  padding-right: 1em;
  min-width: 135px;
  width: 25%;
  margin-bottom: 1em;
  max-width: 200px;
  &__sort {
    // max-width: 144px;
    min-width: 150px;
    margin-right: 0;
    margin-left: 1em;
  }
}
</style>
