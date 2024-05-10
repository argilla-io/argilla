import { shallowMount } from "@vue/test-utils";
import SimilaritySearch from "./SimilaritySearch.component";

let wrapper = null;
const options = {
  stubs: [
    "nuxt",
    "base-button",
    "base-dropdown",
    "similarity-search-content",
    "similarity-search-footer",
  ],
  propsData: {
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
  wrapper = shallowMount(SimilaritySearch, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("SimilaritySearchComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(SimilaritySearch)).toBe(true);
  });
  it("expect to exist formattedVectors", async () => {
    expect(wrapper.props().formattedVectors).toBeTruthy();
  });
  it("expect visible dropdown if multiple formattedVectors and hidden direct button", async () => {
    await wrapper.setProps({
      formattedVectors: [
        {
          id: "text_vector",
          name: "text_vector",
          value: [
            -0.019986379891633987, 0.05246466398239136, 0.023972749710083008,
          ],
        },
        {
          id: "text_vector",
          name: "text_vector",
          value: [
            -0.019986379891633987, 0.05246466398239136, 0.023972749710083008,
          ],
        },
      ],
    });
    const dropdown = wrapper.find("#dropdown");
    const directButton = wrapper.find("#find-similar-button");
    expect(dropdown.exists()).toBe(true);
    expect(directButton.exists()).toBe(false);
  });
  it("expect hidden dropdown if single formattedVectors and visible direct button", async () => {
    const dropdown = wrapper.find("#dropdown");
    const directButton = wrapper.find("#find-similar-button");
    expect(dropdown.exists()).toBe(false);
    expect(directButton.exists()).toBe(true);
  });
});
