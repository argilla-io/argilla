<template>
  <div>
    <div class="dataset-list__header">
      <h1 class="dataset-list__title" v-text="$t('home.argillaDatasets')" />
      <div class="dataset-list__filters">
        <BaseSearchBar
          @input="onSearch"
          :querySearch="querySearch"
          :placeholder="$t('searchDatasets')"
        />
        <DatasetsSort
          @on-change-direction="onChangeDirection"
          @on-change-field="onChangeField"
          :sorted-by-field="sortedByField"
          :sorted-order="sortedOrder"
          :sort-options="sortOptions"
        />
      </div>
    </div>
    <DatasetListCards
      v-if="datasets.length"
      ref="datasetList"
      :datasets="filteredDatasets"
    />
    <DatasetsEmpty v-else @on-click-card="cardAction" />
  </div>
</template>

<script>
export default {
  props: {
    datasets: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      querySearch: "",
      sortedOrder: "desc",
      sortedByField: "updatedAt",
      sortOptions: [
        { value: "name", label: this.$t("home.name") },
        { value: "updatedAt", label: this.$t("home.updatedAt") },
        { value: "createdAt", label: this.$t("home.createdAt") },
      ],
    };
  },
  computed: {
    filteredDatasets() {
      return this.sortedDatasets.filter((dataset) =>
        dataset.name.toLowerCase().includes(this.querySearch?.toLowerCase())
      );
    },
    sortedDatasets() {
      return this.datasets.sort((a, b) => {
        if (this.sortedOrder === "asc") {
          return a[this.sortedByField] > b[this.sortedByField] ? 1 : -1;
        }
        return a[this.sortedByField] < b[this.sortedByField] ? 1 : -1;
      });
    },
  },
  methods: {
    onSearch(event) {
      this.querySearch = event;
    },
    onChangeDirection(direction) {
      this.sortedOrder = direction;
    },
    onChangeField(field) {
      this.sortedByField = field;
    },
    cardAction(action) {
      this.$emit("on-click-card", action);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-list {
  &__header {
    display: flex;
    justify-content: space-between;
    gap: $base-space * 2;
    margin-bottom: $base-space * 2;
  }
  &__title {
    margin: 0;
    @include font-size(20px);
    font-weight: 500;
  }
  &__filters {
    display: flex;
    gap: $base-space;
  }
}
</style>
