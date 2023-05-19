import { shallowMount } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";

let wrapper = null;
const options = {
  propsData: {
    datasetId: "FAKE_ID",
    datasetTask: "FAKE_TASK"
  },
};
beforeEach(() => {
  wrapper = shallowMount(DatasetDescription, options);
});

afterEach(() => {
  wrapper.destroy();
});

jest.mock("@/models/dataset.utilities", () => {
  return {
    getDatasetFromORM: jest.fn(() => ({ tags: { description: "FAKE_DESCRIPTION" } }))
  }
})
describe("DatasetDescriptionComponent should", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDescription)).toBe(true);
  });

  it("see description", () => {
    const description = wrapper.find(".description__text");

    expect(description.element.innerHTML).toBe("FAKE_DESCRIPTION")
  });
});
