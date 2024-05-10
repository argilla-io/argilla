import { shallowMount } from "@vue/test-utils";
import DatasetDelete from "./DatasetDelete.component";
const $route = {
  params: {
    workspace: "argilla",
  },
};

jest.mock("@/models/dataset.utilities", () => ({
  getDatasetFromORM: () => ({
    $id: "settings_textclass_no_labels",
    id: "settings_textclass_no_labels",
    name: "settings_textclass_no_labels",
  }),
}));
let wrapper = null;
const options = {
  stubs: ["base-button", "base-card", "base-modal"],
  propsData: {
    datasetId: ["recognai", "settings_textclass_no_labels"],
    datasetTask: "TextClassification",
    showDeleteModal: false,
  },
  mocks: {
    $route,
  },
};
beforeEach(() => {
  wrapper = shallowMount(DatasetDelete, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DatasetDeleteComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDelete)).toBe(true);
  });

  it("not render base-modal when showDeleteModal is false", async () => {
    expect(wrapper.find(".modal-wrapper").exists()).toBe(false);
  });

  it("render base-modal when showDeleteModal is true", async () => {
    await wrapper.setProps({ showDeleteModal: true });
    expect(wrapper.find(".delete-modal").exists()).toBe(true);
  });
});
