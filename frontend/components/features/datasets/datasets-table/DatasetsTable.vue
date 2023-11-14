<template>
  <div class="container">
    <datasets-empty v-if="!datasets.length" />
    <div class="dataset__table" v-else>
      <div class="interactions">
        <base-search-bar @input="onSearch" placeholder="Search datasets" />
      </div>
      <base-table-info
        ref="table"
        search-on="name"
        :global-actions="false"
        :data="datasets"
        :sorted-order="sortedOrder"
        :sorted-by-field="sortedByField"
        :actions="actions"
        :columns="tableColumns"
        :query-search="querySearch"
        :empty-search-info="emptySearchInfo"
        :active-filters="activeFilters"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
        @filter-applied="onColumnFilterApplied"
      />
    </div>
  </div>
</template>

<script>
import { Base64 } from "js-base64";
import { useRoutes } from "@/v1/infrastructure/services";

export default {
  props: {
    datasets: {
      type: Array,
      required: true,
    },
  },
  created() {
    this.datasets.forEach((dataset) => {
      dataset.link = this.getDatasetLink(dataset);
    });
  },
  data() {
    return {
      querySearch: undefined,
      tableColumns: [
        {
          name: "Name",
          field: "name",
          class: "table-info__title",
          type: "link",
        },
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
          field: "createdAt",
          class: "date",
          type: "date",
          sortable: "true",
        },
        {
          name: "Updated at",
          field: "lastActivityAt",
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
      sortedByField: "updatedAt",
    };
  },
  computed: {
    activeFilters() {
      const workspaces = this.workspaces;
      const tasks = this.tasks;
      const tags = this.tags;
      return [
        { column: "workspace", values: workspaces },
        { column: "task", values: tasks },
        { column: "tags", values: tags },
      ];
    },
    workspaces() {
      return this.$route.query.workspaces?.split(",") ?? [];
    },
    tasks() {
      return this.$route.query.tasks?.split(",") ?? [];
    },
    tags() {
      return this.$route.query.tags
        ? JSON.parse(Base64.decode(this.$route.query.tags))
        : [];
    },
  },
  methods: {
    clearFilters() {
      if (this.$refs.table) {
        this.activeFilters.forEach((filter) => {
          this.$refs.table.onApplyFilters({ field: filter.column }, []);
        });

        this.goToDatasetsList();
      }
    },
    onSearch(event) {
      this.querySearch = event;
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    onColumnFilterApplied({ column, values }) {
      const updateUrlParamsFor = (
        values,
        paramKey,
        currentParams,
        valuesToPush
      ) => {
        if (values === currentParams) return;

        const query = createQueryFor(values, paramKey, valuesToPush);
        this.$router.push({ query });
      };

      const createQueryFor = (values, paramKey, valuesToPush) => {
        if (values.length) {
          return { ...this.$route.query, [paramKey]: valuesToPush };
        }

        const { [paramKey]: keyToEscape, ...rest } = this.$route.query;
        return { ...rest };
      };

      switch (column) {
        case "workspace":
          updateUrlParamsFor(
            values,
            "workspaces",
            this.workspaces,
            values.join(",")
          );
          break;
        case "task":
          updateUrlParamsFor(values, "tasks", this.tasks, values.join(","));
          break;
        case "tags":
          updateUrlParamsFor(
            values,
            "tags",
            this.tags,
            Base64.encodeURI(JSON.stringify(values))
          );
          break;
      }
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
          this.copyName(dataset);
          break;
        default:
          console.warn(action);
      }
    },
    copy(value) {
      this.$copyToClipboard(value);
    },
    copyUrl(dataset) {
      this.copy(`${window.origin}${this.getDatasetLink(dataset)}`);
    },
    copyName({ name }) {
      this.copy(name);
    },
  },
  setup() {
    return useRoutes();
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  justify-content: center;
  padding: 0.2em calc($sidebarMenuWidth + 4em) 0 4em;
  flex-grow: 1;
  overflow: auto;
}
.dataset {
  &__table {
    width: 100%;
  }
}
.interactions {
  display: flex;
  align-items: flex-end;
  margin: 2em 0 1em 0;
}

.search-area {
  width: clamp(300px, 30vw, 800px);
}
</style>
