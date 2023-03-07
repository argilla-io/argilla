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
    <base-loading v-if="$fetchState.pending" />
    <div v-else class="wrapper">
      <div class="main">
        <app-header
          :copy-button="false"
          :breadcrumbs="breadcrumbs"
          :sticky="false"
          @breadcrumb-action="onBreadcrumbAction($event)"
        />
        <error
          v-if="$fetchState.error"
          where="workspace datasets"
          :error="$fetchState.error"
        />
        <datasets-empty v-else-if="!datasets.length" :workspace="workspace" />
        <div v-else class="container">
          <div class="interactions">
            <base-search-bar @input="onSearch" placeholder="Search datasets" />
          </div>
          <div>
            <base-table-info
              ref="table"
              :data="datasets"
              :sorted-order="sortedOrder"
              :sorted-by-field="sortedByField"
              :actions="actions"
              :columns="tableColumns"
              :query-search="querySearch"
              :global-actions="false"
              :empty-search-info="emptySearchInfo"
              :active-filters="activeFilters"
              search-on="name"
              @sort-column="onSortColumns"
              @onActionClicked="onActionClicked"
              @filter-applied="onColumnFilterApplied"
            />
          </div>
        </div>
      </div>
      <sidebar-menu
        class="home__sidebar"
        @refresh="$fetch"
        :sidebar-items="sidebarItems"
      />
    </div>
  </div>
</template>

<script>
import { ObservationDataset } from "@/models/Dataset";
import { mapActions } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { Base64 } from "js-base64";
export default {
  layout: "app",
  data: () => ({
    querySearch: undefined,
    breadcrumbs: [{ action: "clearFilters", name: "Datasets" }],
    tableColumns: [
      { name: "Name", field: "name", class: "table-info__title", type: "link" },
      {
        name: "Workspace",
        field: "workspace",
        class: "text",
        type: "text",
        filtrable: "true",
      },
      {
        name: "Task",
        field: "task",
        class: "task",
        type: "task",
        filtrable: "true",
      },
      {
        name: "Tags",
        field: "tags",
        class: "text",
        type: "object",
        filtrable: "true",
      },
      {
        name: "Created at",
        field: "created_at",
        class: "date",
        type: "date",
        sortable: "true",
      },
      {
        name: "Updated at",
        field: "last_updated",
        class: "date",
        type: "date",
        sortable: "true",
      },
    ],
    actions: [
      {
        name: "go-to-settings",
        icon: "settings",
        title: "Go to dataset settings",
        tooltip: "Dataset settings",
      },
      {
        name: "copy",
        icon: "link",
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
  }),
  async fetch() {
    await this.fetchDatasets();
  },
  computed: {
    activeFilters() {
      const workspaces = this.workspaces;
      const tasks = this.tasks;
      const tags = this.tags;
      return [
        { column: "workspace", values: workspaces || [] },
        { column: "task", values: tasks || [] },
        { column: "tags", values: tags || [] },
      ];
    },
    sidebarItems() {
      return [
        {
          id: "refresh",
          tooltip: "Refresh",
          icon: "refresh",
          group: "Refresh",
          action: "refresh",
        },
      ];
    },
    datasets() {
      return ObservationDataset.all().map((dataset) => {
        return {
          ...dataset,
          id: dataset.id,
          link: this.datasetWorkspace(dataset),
        };
      });
    },
    workspaces() {
      let _workspaces = this.$route.query.workspace;
      if (typeof _workspaces == "string") {
        _workspaces = [_workspaces];
      }
      return _workspaces;
    },
    tasks() {
      let _tasks = this.$route.query.task;
      if (typeof _tasks == "string") {
        _tasks = [_tasks];
      }
      return _tasks;
    },
    tags() {
      let _tags = this.$route.query.tags
        ? JSON.parse(Base64.decode(this.$route.query.tags))
        : undefined;
      if (typeof _tags == "string") {
        _tags = [_tags];
      }
      return _tags;
    },
    workspace() {
      // THIS IS WRONG !!!
      this.$route.query.workspace;
      return currentWorkspace(this.$route);
    },
  },
  methods: {
    ...mapActions({
      fetchDatasets: "entities/datasets/fetchAll",
    }),
    onColumnFilterApplied({ column, values }) {
      if (column === "workspace") {
        if (values !== this.workspaces) {
          this.$router.push({
            query: { ...this.$route.query, workspace: values },
          });
        }
      }
      if (column === "task") {
        if (values !== this.tasks) {
          this.$router.push({ query: { ...this.$route.query, task: values } });
        }
      }
      if (column === "tags") {
        if (values !== this.tags) {
          this.$router.push({
            query: {
              ...this.$route.query,
              tags: values.length
                ? Base64.encodeURI(JSON.stringify(values))
                : undefined,
            },
          });
        }
      }
    },
    datasetWorkspace(dataset) {
      var workspace = dataset.workspace;
      if (workspace === null || workspace === "null") {
        workspace = this.workspace;
      }
      return `/datasets/${workspace}/${dataset.name}`;
    },
    onActionClicked(action, dataset) {
      switch (action) {
        case "go-to-settings":
          this.goToSetting(dataset);
          break;
        case "copy":
          this.copyUrl(dataset);
          break;
        case "copy-name":
          this.copyName(dataset.name);
          break;
        default:
          console.warn(action);
      }
    },
    onSearch(event) {
      this.querySearch = event;
    },
    goToSetting(dataset) {
      const { workspace, name } = dataset;
      this.$router.push({
        path: `/datasets/${workspace}/${name}/settings`,
      });
    },
    copyName(id) {
      this.copy(id);
    },
    copyUrl(dataset) {
      const route = `${window.origin}${dataset.link}`;
      this.copy(route);
    },
    copy(id) {
      this.$copyToClipboard(id);
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    async clearFilters() {
      if (this.$refs.table) {
        await this.activeFilters.forEach((filter) => {
          this.$refs.table.onApplyFilters({ field: filter.column }, []);
        });
        this.$router.push({ path: "/datasets" });
      }
    },
    onBreadcrumbAction(e) {
      if (e === "clearFilters") {
        this.clearFilters();
      }
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
  padding-right: calc($sidebarMenuWidth + 4em);
  &--intro {
    padding-top: 2em;
    margin-bottom: 1.5em;
    &:after {
      border-bottom: 1px solid palette(grey, 700);
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
}

.title {
  display: inline-block;
  font-weight: lighter;
  margin-right: 1em;
  margin-bottom: 2em;
  @include font-size(18px);
}

.home {
  &__sidebar.sidebar {
    position: fixed;
    top: 56px;
    right: 0;
    border-left: 1px solid palette(grey, 600);
  }
}
</style>
