import { shallowMount } from "@vue/test-utils";
import FilterSimilarity from "./FilterSimilarity";

let wrapper = null;
const options = {
  stubs: ["nuxt", "base-button"],
  propsData: {
    filterIsActive: false,
  },
};
beforeEach(() => {
  wrapper = shallowMount(FilterSimilarity, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("FilterSimilarityComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(FilterSimilarity)).toBe(true);
  });
  it("expect active filtered status to be hidden", async () => {
    testIfActiveClassIsVisible(false);
  });
  it("expect active filtered status to be visible", async () => {
    await wrapper.setProps({ filterIsActive: true });
    testIfActiveClassIsVisible(true);
  });
  it("expect active filtered status to be visible", async () => {
    await wrapper.setProps({ filterIsActive: true });
    testIfActiveClassIsVisible(true);
  });
  it.skip("expect to emit 'search-records'", async () => {
    await wrapper.setProps({ filterIsActive: true });
    const query = { vector: null };
    const removeButton = wrapper.find(".filter__similarity__button");
    removeButton.trigger("click");
    wrapper.vm.$nextTick();
    wrapper.vm.$nextTick();
    expect(wrapper.emitted("search-records")).toStrictEqual([[query]]);
  });
});

const testIfActiveClassIsVisible = async (value) => {
  const activeComponent = wrapper.find("#filter-active");
  expect(activeComponent.exists()).toBe(value);
};
