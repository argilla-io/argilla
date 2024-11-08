<template>
  <div>
    <div class="dataset-list__header">
      <h1 class="dataset-list__title" v-text="$t('home.argillaDatasets')" />
      <BaseSearchBar
        @input="onSearch"
        :querySearch="querySearch"
        :placeholder="$t('searchDatasets')"
      />
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
          return a[this.sortedByField] - b[this.sortedByField];
        }

        return b[this.sortedByField] - a[this.sortedByField];
      });
    },
    activeWorkspace() {
      const workspaces = this.$route.query.workspaces?.split(",") ?? [];
      return [{ column: "workspace", values: workspaces }];
    },
  },
  methods: {
    onSearch(event) {
      this.querySearch = event;
    },
    onSort(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
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
}
</style>
