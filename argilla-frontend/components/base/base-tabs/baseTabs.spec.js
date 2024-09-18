import { shallowMount } from "@vue/test-utils";
import BaseTabs from "./BaseTabs";

let wrapper = null;
const options = {
  components: { BaseTabs },
  propsData: {
    tabs: [
      { id: "tab1", name: "Tab 1" },
      { id: "tab2", name: "Tab 2" },
    ],
    activeTab: { id: "tab1", name: "Tab 1" },
  },
};

beforeEach(() => {
  wrapper = shallowMount(BaseTabs, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseTabs", () => {
  it("emit change-tab event with first tab id on click in the first tab", async () => {
    const button = wrapper.findAll(".tab__button").at(0);
    button.trigger("click");
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("change-tab")).toEqual([[wrapper.vm.tabs[0].id]]);
  });
  it("not render --active class when tab is not active", async () => {
    checkButtonActiveClass(1, false);
  });
  it("render --active class when tab is active", async () => {
    checkButtonActiveClass(0, true);
  });
  it("render --active class when there is only one tab", async () => {
    await wrapper.setProps({
      tabs: [{ id: "tab1", name: "Tab 1" }],
    });
    checkButtonActiveClass(0, true);
  });
});

const checkButtonActiveClass = async (tabPosition, value) => {
  const button = wrapper.findAll(".tab__button").at(tabPosition);
  expect(button.find(".--active").exists()).toBe(value);
};
