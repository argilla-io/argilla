<template>
  <div>
    <ReTopbarBrand>
      <ReBreadcrumbs :breadcrumbs="[{ link: '/', name: 'Datasets' }]" />
    </ReTopbarBrand>
    <div class="container">
      <div class="interactions">
        <ReSearchBar @input="onSearch" />
        <ReButton class="button-primary" @click="$fetch">
          <svgicon name="refresh" width="20" height="14" /> Refresh
        </ReButton>
      </div>
      <ReLoading v-if="$fetchState.pending" />
      <Error
        v-if="$fetchState.error"
        link="/"
        where="datasets"
        :error="$fetchState.error"
      />
      <div v-else>
        <ReTableInfo
          :data="datasets"
          :sorted-order="sortedOrder"
          :sorted-by-field="sortedByField"
          :actions="actions"
          :columns="tableColumns"
          :query-search="querySearch"
          :global-actions="false"
          search-on="name"
          :show-modal="showModal"
          @sort-column="onSortColumns"
          @onActionClicked="onActionClicked"
          @close-modal="closeModal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ObservationDataset } from "@/models/Dataset";
import { mapActions } from "vuex";
export default {
  layout: "app",
  data: () => ({
    querySearch: undefined,
    tableColumns: [
      { name: "Name", field: "name", class: "table-info__title", type: "link" },
      { name: "Tags", field: "tags", class: "text", type: "object" },
      { name: "Task", field: "task", class: "task", type: "task" },
      { name: "Created at", field: "created_at", class: "date", type: "date" },
      {
        name: "Updated at",
        field: "last_updated",
        class: "date",
        type: "date",
      },
    ],
    actions: [
      { name: "delete", icon: "delete", tooltip: "Delete" },
      { name: "copy", icon: "copy", tooltip: "Copy link" },
    ],
    externalLinks: [
      {
        tooltip: "Go to MLflow",
        title: "MLflow",
        link: { name: "mlflow", params: { id: "0" } },
      },
    ],
    sortedOrder: "desc",
    sortedByField: "last_updated",
    showModal: undefined,
  }),
  async fetch() {
    await this.fetchDatasets();
  },
  computed: {
    datasets() {
      return ObservationDataset.all();
    },
  },
  methods: {
    ...mapActions({
      fetchDatasets: "entities/datasets/fetchAll",
      _deleteDataset: "entities/datasets/deleteDataset",
    }),
    onActionClicked(action, rowId) {
      switch (action) {
        case "delete":
          this.showConfirmDatasetDeletion(rowId);
          break;
        case "copy":
          this.copyUrl(rowId);
          break;
        case "confirm-delete":
          this.deleteDataset(rowId);
          break;
        case undefined:
          this.$router.push(rowId);
          break;
        default:
          console.warn(action);
      }
    },
    onSearch(event) {
      this.querySearch = event;
    },
    copyUrl(id) {
      const route = `${window.origin}${this.$route.path}${id}`;
      const textToCopy = route;
      const myTemporaryInputElement = document.createElement("input");
      myTemporaryInputElement.type = "text";
      myTemporaryInputElement.className = "hidden-input";
      myTemporaryInputElement.value = textToCopy;
      document.body.appendChild(myTemporaryInputElement);
      myTemporaryInputElement.select();
      document.execCommand("Copy");
    },
    showConfirmDatasetDeletion(id) {
      this.showModal = id;
    },
    deleteDataset(id) {
      this._deleteDataset({ name: id });
      this.closeModal();
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    closeModal() {
      this.showModal = undefined;
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0.2em;
  padding-bottom: 0;
  &--intro {
    padding-top: 2em;
    margin-bottom: 1.5em;
    &:after {
      border-bottom: 1px solid $line-light-color;
      content: "";
      margin-bottom: 1.5em;
      position: absolute;
      left: 0;
      right: 0;
    }
  }
}

.interactions {
  display: flex;
  align-items: flex-end;
  margin: 2em 0 1em 0;
  .re-button {
    margin-left: auto;
    margin-bottom: 0;
  }
}

.title {
  display: inline-block;
  font-weight: lighter;
  margin-right: 1em;
  margin-bottom: 2em;
  @include font-size(18px);
}
</style>
