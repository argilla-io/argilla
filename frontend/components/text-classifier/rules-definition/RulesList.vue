<template>
    <ReTableInfo
        :data="list"
        :sorted-order="sortedOrder"
        :sorted-by-field="sortedByField"
        :columns="tableColumns"
        :global-actions="false"
        search-on="query"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
    />
</template>
<script>
export default {
  data: () => {
    return {
      list: [
        {
          query: 'test',
          name: 'test',
          exampleField: {'exampleField1' : 'lorem', 'exampleField2' : 'ipsum'},
        }
      ],
      tableColumns: [
        {
          name: "Query",
          field: "query",
          class: "example class",
          type: 'link',
        },
        { name: "Tags", field: "exampleField", class: "text", type: "object" },
      ],
      sortedOrder: "desc",
      sortedByField: "query",
    };
  },
  methods: {
    onActionClicked(action, rowId) {
      console.log(action, rowId)
      switch (action) {
        case "select":
          console.log('action', rowId)
          break;
        default:
          console.warn(action);
      }
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
  }
};
</script>
<style lang="scss" scoped>
</style>

