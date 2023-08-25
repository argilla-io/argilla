import { shallowMount } from "@vue/test-utils";
import DatasetDescriptionReadOnly from "./DatasetDescriptionReadOnly.component";

let wrapper = null;
const options = {
  stubs: ["RenderMarkdownBaseComponent"],
  propsData: {
    datasetDescription: "Lorem ipsum",
  },
};
beforeEach(() => {
  wrapper = shallowMount(DatasetDescriptionReadOnly, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DatasetDescriptionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDescriptionReadOnly)).toBe(true);
  });
});
