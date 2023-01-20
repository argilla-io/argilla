import { shallowMount } from "@vue/test-utils";
import BasePaginationComponent from "./BasePagination";
import "@/plugins/filters";

let wrapper = null;

const options = {
  propsData: {
    totalItems: 0,
    paginationSettings: {
      $id: "a_lot_of_labels_multi-label",
      id: "a_lot_of_labels_multi-label",
      size: 50,
      page: 1,
      pageSizeOptions: [1, 10, 20, 50, 100],
      maxRecordsLimit: 10000,
      disabledShortCutPagination: false,
    },
    visiblePagesRange: 5,
  },
};

beforeEach(() => {
  wrapper = shallowMount(BasePaginationComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BasePaginationComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(BasePaginationComponent)).toBe(true);
    expect(wrapper.find(".total-records").exists()).toBe(true);
  });

  it("show the totalItems as the total records if records<10k", async () => {
    await itTestIfTheTotalRecordsShownInPaginationIsEqualToPropsTotalItems(5);
  });

  it("show the totalItems as the total records if records>10k", async () => {
    await itTestIfTheTotalRecordsShownInPaginationIsEqualToPropsTotalItems(
      10001
    );
  });
});

const itTestIfTheTotalRecordsShownInPaginationIsEqualToPropsTotalItems = async (
  totalRecords
) => {
  await wrapper.setProps({ totalItems: totalRecords });
  const formatNumberFilter = new Intl.NumberFormat("en").format(totalRecords);
  const totalRecordsTextWrapper = wrapper.find(".total-records");
  expect(totalRecordsTextWrapper.text()).toBe(formatNumberFilter);
};
