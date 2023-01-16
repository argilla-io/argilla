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
          class: "text",
          field: "owner",
          filtrable: "true",
          name: "Workspace",
          type: "text",
        },
      ],
      data: [
        {
          name: "dataset_1",
          owner: "recognai",
          task: "TokenClassification",
        },
        {
          name: "dataset_2",
          owner: "recognai",
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
      filterFromRoute: "owner",
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

  test("renders properly", () => {
    const wrapper = mountBaseTableInfo();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
