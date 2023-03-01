import { shallowMount } from "@vue/test-utils";
import DatasetDelete from "./DatasetDelete.component";
const $route = {
  params: {
    workspace: "argilla",
  },
};
let wrapper = null;
const options = {
  stubs: ["base-button", "base-card", "base-modal"],
  propsData: {
    datasetName: "datasete_1",
    sectionTitle: "Danger zone",
    showdeleteModal: false,
  },
  mocks: {
    $route,
  },
};
beforeEach(() => {
  console.log(wrapper);
  wrapper = shallowMount(DatasetDelete, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DatasetDeleteComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDelete)).toBe(true);
  });

  it("not render base-modal when showdeleteModal is false", async () => {
    expect(wrapper.find(".modal-wrapper").exists()).toBe(false);
  });

  it("render base-modal when showdeleteModal is true", async () => {
    await wrapper.setProps({
      showdeleteModal: true,
    });
    expect(wrapper.find(".delete-modal").exists()).toBe(true);
  });
});
