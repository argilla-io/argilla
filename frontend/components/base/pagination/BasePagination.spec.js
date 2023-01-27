import { shallowMount } from "@vue/test-utils";
import BasePagination from "./BasePagination";
import "@/plugins/filters";

let wrapper = null;
const options = {
  propsData: {
    totalItems: 500,
    paginationSettings: {
      disabledShortCutPagination: false,
      maxRecordsLimit: 10000,
      page: 2,
      pageSizeOptions: [1, 10, 20, 50, 100],
      size: 10,
    },
    onePage: false,
    visiblePagesRange: 5,
  },
};
beforeEach(() => {
  wrapper = shallowMount(BasePagination, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BasePaginationComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(BasePagination)).toBe(true);
  });
  it("emit event when previous is clicked", async () => {
    return prevNextButtonEmition(".pagination__arrow--prev", -1);
  });
  it("emit event when next is clicked", async () => {
    return prevNextButtonEmition(".pagination__arrow--next", 1);
  });
  it("emit event when page is clicked", async () => {
    const page = wrapper.find(".pagination__number");
    page.trigger("click");
    wrapper.vm.$nextTick();
    expect(wrapper.emitted("changePage")).toStrictEqual([
      [Number(page.text()), wrapper.vm.paginationSettings.size],
    ]);
  });
  it("should remove pagination buttons when records are 0", async () => {
    await wrapper.setProps({
      totalItems: 0,
    });
    expect(wrapper.find(".pagination").exists()).toBe(false);
  });
  it("should only render records number if one page is active", async () => {
    await wrapper.setProps({
      onePage: true,
    });
    expect(wrapper.find(".pagination").exists()).toBe(false);
    expect(wrapper.find(".pagination__selector").exists()).toBe(false);
  });
});

const prevNextButtonEmition = async (className, value) => {
  const button = wrapper.find(className);
  button.trigger("click");
  wrapper.vm.$nextTick();
  expect(wrapper.emitted("changePage")).toStrictEqual([
    [
      wrapper.vm.paginationSettings.page + value,
      wrapper.vm.paginationSettings.size,
    ],
  ]);
};
