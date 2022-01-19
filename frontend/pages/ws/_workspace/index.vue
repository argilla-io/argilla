<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div>
    <ReLoading v-if="$fetchState.pending" />
    <div v-else class="wrapper">
      <div class="main">
        <app-header
          :breadcrumbs="[{ link: `/ws/${workspace}`, name: workspace }]"
          :sticky="false"
        />
        <Error
          v-if="$fetchState.error"
          where="workspace datasets"
          :error="$fetchState.error"
        />
        <datasets-empty v-else-if="!datasets.length" :workspace="workspace" />
        <div v-else class="container">
          <div class="interactions">
            <ReSearchBar @input="onSearch" placeholder="Search datasets" />
          </div>
          <div>
            <ReTableInfo
              :data="datasets"
              :sorted-order="sortedOrder"
              :sorted-by-field="sortedByField"
              :actions="actions"
              :columns="tableColumns"
              :query-search="querySearch"
              :global-actions="false"
              search-on="name"
              :visible-modal-id="datasetCompositeId"
              :delete-modal-content="deleteConfirmationContent"
              :empty-search-info="emptySearchInfo"
              @sort-column="onSortColumns"
              @onActionClicked="onActionClicked"
              @close-modal="closeModal"
            />
          </div>
        </div>
      </div>
      <sidebar-menu @refresh="$fetch" />
    </div>
  </div>
</template>

<script>
import { ObservationDataset } from "@/models/Dataset";
import { mapActions } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
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
      { name: "delete", icon: "delete", title: "Delete dataset" },
      {
        name: "copy",
        icon: "copy-url",
        title: "Copy url to clipboard",
        tooltip: "Copied",
      },
    ],
    emptySearchInfo: {
      title: "0 datasets found",
    },
    externalLinks: [],
    sortedOrder: "desc",
    sortedByField: "last_updated",
    datasetCompositeId: undefined,
  }),
  async fetch() {
    await this.fetchDatasets();
  },
  computed: {
    datasets() {
      return ObservationDataset.all().map((dataset) => {
        return {
          ...dataset,
          id: dataset.id,
          link: this.datasetWorkspace(dataset),
        };
      });
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
    deleteConfirmationContent() {
      const [workspace, name] = this.datasetCompositeId || [];
      const content = {
        title: "Delete confirmation",
        text: `You are about to delete: <strong>${name}</strong> from workspace <strong>${workspace}</strong>. This action cannot be undone`,
      };

      if (workspace === this.workspace) {
        content.text = content.text.replace(
          ` from workspace <strong>${workspace}</strong>`,
          ""
        );
      }
      return content;
    },
  },
  methods: {
    ...mapActions({
      fetchDatasets: "entities/datasets/fetchAll",
      _deleteDataset: "entities/datasets/deleteDataset",
    }),

    datasetWorkspace(dataset) {
      var workspace = dataset.owner;
      if (workspace === null || workspace === "null") {
        workspace = this.workspace;
      }
      return `/ws/${workspace}/${dataset.name}`;
    },

    onActionClicked(action, dataset) {
      switch (action) {
        case "delete":
          this.showConfirmDatasetDeletion(dataset);
          break;
        case "copy":
          this.copyUrl(dataset);
          break;
        case "copy-name":
          this.copyName(dataset.name);
          break;
        case "confirm-delete":
          this.deleteDataset(dataset);
          break;

        default:
          console.warn(action);
      }
    },
    onSearch(event) {
      this.querySearch = event;
    },
    copyName(id) {
      this.copy(id);
    },
    copyUrl(dataset) {
      const route = `${window.origin}${dataset.link}`;
      this.copy(route);
    },
    copy(id) {
      const myTemporaryInputElement = document.createElement("input");
      myTemporaryInputElement.type = "text";
      myTemporaryInputElement.className = "hidden-input";
      myTemporaryInputElement.value = id;
      document.body.appendChild(myTemporaryInputElement);
      myTemporaryInputElement.select();
      document.execCommand("Copy");
    },
    showConfirmDatasetDeletion(dataset) {
      this.datasetCompositeId = dataset.id;
    },
    deleteDataset(dataset) {
      this._deleteDataset({
        workspace: dataset.owner,
        name: dataset.name,
      });
      this.closeModal();
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    closeModal() {
      this.datasetCompositeId = undefined;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  .main {
    width: 100%;
  }
}
.container {
  @extend %container;
  padding-top: 0.2em;
  padding-bottom: 0;
  padding-right: calc(4em + 45px);
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
