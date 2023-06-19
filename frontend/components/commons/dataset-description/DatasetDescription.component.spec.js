import { shallowMount } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";

let wrapper = null;
const options = {
  stubs: ["RenderMarkdownBaseComponent"],
  propsData: {
    datasetDescription: "Lorem ipsum",
  },
};
beforeEach(() => {
  wrapper = shallowMount(DatasetDescription, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DatasetDescriptionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDescription)).toBe(true);
  });
});
