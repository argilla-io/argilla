import { shallowMount } from "@vue/test-utils";
import DatasetDescriptionReadOnly from "./DatasetDescriptionReadOnly.component";

let wrapper = null;
const options = {
  stubs: ["RenderMarkdownBaseComponent"],
  propsData: {
    guidelines: "Lorem ipsum",
  },
  mocks: {
    $t: (msg) => msg,
  },
};
beforeEach(() => {
  wrapper = shallowMount(DatasetDescriptionReadOnly, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DatasetDescriptionReadonlyComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DatasetDescriptionReadOnly)).toBe(true);
  });
});
