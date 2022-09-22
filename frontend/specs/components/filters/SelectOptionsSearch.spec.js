import { mount } from "@vue/test-utils";
import SelectOptionsSearch from "@/components/commons/header/filters/SelectOptionsSearch";

function mountSelectOptionsSearch() {
  return mount(SelectOptionsSearch, {
    propsData: {
      value: ["NEGAT"],
      allowClear: true,
    },
  });
}

describe("SelectOptionsSearch", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountSelectOptionsSearch();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
