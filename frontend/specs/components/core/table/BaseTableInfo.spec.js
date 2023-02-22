import { mount } from "@vue/test-utils";
import BaseTableInfo from "@/components/base/table/BaseTableInfo";

const $route = {
  query: {},
};

function mountBaseTableInfo() {
  return mount(BaseTableInfo, {
    stubs: [
      "lazy-table-filtrable-column",
      "base-modal",
      "base-button",
      "base-modal",
    ],
    propsData: {
      actions: [],
      columns: [
        {
          idx: 1,
          key: "column1",
          class: "text",
          field: "workspace",
          filtrable: "true",
          name: "Workspace",
          type: "text",
        },
      ],
      data: [
        {
          key: "data1",
          name: "dataset_1",
          workspace: "recognai",
          task: "TokenClassification",
        },
        {
          key: "data2",
          name: "dataset_2",
          workspace: "recognai",
          task: "TokenClassification",
        },
      ],
      deleteModalContent: {
        text: "You are about to delete: <strong>undefined</strong>. This action cannot be undone",
        title: "Delete confirmation",
      },
      emptySearchInfo: {
        title: "0 datasets found",
      },
      globalActions: false,
      groupBy: undefined,
      hideButton: false,
      noDataInfo: undefined,
      querySearch: undefined,
      filterFromRoute: "workspace",
      searchOn: "name",
      sortedByField: "last_updated",
      sortedOrder: "desc",
      visibleModalId: undefined,
    },
    mocks: {
      $route,
    },
  });
}

describe("BaseTableInfo", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  it.skip("renders properly", () => {
    // FIXME
    const wrapper = mountBaseTableInfo();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
