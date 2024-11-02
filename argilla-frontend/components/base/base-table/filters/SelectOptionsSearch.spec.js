import { mount } from "@vue/test-utils";
import SelectOptionsSearch from "@/components/base/base-table/filters/SelectOptionsSearch.vue";

function mountSelectOptionsSearch() {
  return mount(SelectOptionsSearch, {
    propsData: {
      value: "Search Input",
      allowClear: true,
    },
  });
}

describe("SelectOptionsSearch", () => {
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountSelectOptionsSearch();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
