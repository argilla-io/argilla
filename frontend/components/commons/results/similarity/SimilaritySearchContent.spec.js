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
    vectors: [
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
    expect(wrapper.props().vectors).toBeTruthy();
  });
  it("expect to exist similaritySelectedVector", async () => {
    expect(wrapper.vm.similaritySelectedVector).toBeTruthy();
  });
  // it("expect visible dropdown if multiple vectors and hidden direct button", async () => {
  //   await wrapper.setProps({
  //     vectors: [
  //       {
  //         id: "text_vector",
  //         name: "text_vector",
  //         value: [
  //           -0.019986379891633987, 0.05246466398239136, 0.023972749710083008,
  //         ],
  //       },
  //       {
  //         id: "text_vector",
  //         name: "text_vector",
  //         value: [
  //           -0.019986379891633987, 0.05246466398239136, 0.023972749710083008,
  //         ],
  //       },
  //     ],
  //   });
  //   const dropdown = wrapper.find("#dropdown");
  //   const directButton = wrapper.find("#find-similar-button");
  //   expect(dropdown.exists()).toBe(true);
  //   expect(directButton.exists()).toBe(false);
  // });
  // it("expect hidden dropdown if single vectors and visible direct button", async () => {
  //   const dropdown = wrapper.find("#dropdown");
  //   const directButton = wrapper.find("#find-similar-button");
  //   expect(dropdown.exists()).toBe(false);
  //   expect(directButton.exists()).toBe(true);
  // });
});
