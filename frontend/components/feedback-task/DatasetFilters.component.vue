<template>
  <div class="filters">
    <span class="filters__component">
      <SearchBarBase
        v-model="searchInput"
        :placeholder="'Introduce a query'"
        :additionalInfo="additionalInfoForSearchComponent"
      />
    </span>
    <span class="filters__component">
      <StatusFilter :options="statusOptions" v-model="selectedStatus" />
    </span>
    <div class="draft">
      <BaseSpinner v-if="draftSaving" />
      <p v-if="draftSaving">Saving...</p>
      <p v-if="!draftSaving && isSavedDraft">
        Saved
        <BaseDate
          :date="updatedAt"
          :format="'date-relative-now'"
          :updateEverySecond="10"
        />
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "DatasetFiltersComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      selectedStatus: null,
      searchInput: null,
      totalRecords: null,
      updatedAt: null,
      isSavedDraft: false,
      draftSaving: false,
    };
  },
  beforeMount() {
    this.selectedStatus = this.selectedStatus ?? this.statusFromRoute;
    this.searchInput = this.searchInput ?? this.searchFromRoute;

    this.$root.$on("reset-status-filter", () => {
      this.selectedStatus = this.statusFromRoute;
    });
    this.$root.$on("reset-search-filter", () => {
      this.searchInput = this.searchFromRoute;
    });
    this.$root.$on("total-records", (totalRecords) => {
      this.totalRecords = totalRecords;
    });
    this.$root.$on("record-changed", (record) => {
      this.updatedAt = record.updatedAt;
      this.isSavedDraft = record.isSavedDraft;
    });
    this.$root.$on("record-saving", (draftSaving) => {
      this.draftSaving = draftSaving;
    });
  },
  computed: {
    additionalInfoForSearchComponent() {
      if (!this.totalRecords || this.totalRecords === 0) return null;

      if (this.totalRecords === 1) return `${this.totalRecords} record`;
      return `${this.totalRecords} records`;
    },
    statusFromRoute() {
      return this.$route.query?._status;
    },
    searchFromRoute() {
      return this.$route.query?._search;
    },
  },
  watch: {
    selectedStatus(newValue) {
      this.$root.$emit("status-filter-changed", newValue);
    },
    searchInput(searchInput) {
      this.$root.$emit("search-filter-changed", searchInput);
    },
  },
  created() {
    this.statusOptions = [
      {
        id: "pending",
        name: "Pending",
      },
      {
        id: "submitted",
        name: "Submitted",
      },
      {
        id: "discarded",
        name: "Discarded",
      },
    ];
  },
  beforeDestroy() {
    this.$root.$off("reset-status-filter");
    this.$root.$off("reset-search-filter");
    this.$root.$off("total-records");
    this.$root.$off("record-changed");
    this.$root.$off("record-saving");
  },
};
</script>

<style lang="scss" scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: $base-space * 2;
  align-items: center;
  padding: $base-space * 2 0;
}
.search-area {
  width: clamp(300px, 30vw, 800px);
}
.draft {
  display: flex;
  flex-direction: row;
  gap: 5px;
  align-items: center;
  height: 10px;
  @include font-size(13px);
  color: $primary-color;
}
</style>
