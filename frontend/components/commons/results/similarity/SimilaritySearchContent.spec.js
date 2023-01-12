import { shallowMount } from "@vue/test-utils";
import SimilaritySearchContent from "./SimilaritySearchContent";

let wrapper = null;
const options = {
  propsData: {
    selectedVector: {
      id: "text_vector",
      name: "text_vector",
      value: [-0.019986379891633987, 0.05246466398239136, 0.023972749710083008],
    },
    formattedVectors: [
      {
        id: "text_vector",
        name: "text_vector",
        value: [
          -0.019986379891633987, 0.05246466398239136, 0.023972749710083008,
        ],
      },
    ],
  },
};
beforeEach(() => {
  wrapper = shallowMount(SimilaritySearchContent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("SimilaritySearchContentComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(SimilaritySearchContent)).toBe(true);
  });
  it("expect to exist vectors", async () => {
    expect(wrapper.props().formattedVectors).toBeTruthy();
  });
  it("expect to exist selectedName", async () => {
    expect(wrapper.vm.selectedName).toBeTruthy();
  });
});
