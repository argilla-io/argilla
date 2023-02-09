import { shallowMount } from "@vue/test-utils";
import HelpInfoContent from "./HelpInfoContent";

let wrapper = null;
beforeEach(() => {
  wrapper = shallowMount(HelpInfoContent, options);
});

const options = {
  selectedComponent: undefined,
  stubs: ["helpInfoSimilarity", "helpInfoExplain", "base-button"],
  propsData: {
    helpContents: [
      {
        id: "similarity",
        name: "Similarity Search",
        component: "helpInfoSimilarity",
      },
      {
        id: "explain",
        name: "Colors in token attributions",
        component: "helpInfoExplain",
      },
    ],
  },
};

afterEach(() => {
  wrapper.destroy();
});

describe("HelpInfoContentComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(HelpInfoContent)).toBe(true);
  });
  it("expect to render content if similarity or explain context exist", async () => {
    expect(wrapper.find(".help-info__content").exists()).toBe(true);
  });
  it("expect to make visible firts help content when there is not selected one", async () => {
    expect(wrapper.vm.visibleComponent).toBe(
      wrapper.vm.helpContents[0].component
    );
  });
  it("expect to render helpInfoSimilarity if option similarity is selected", async () => {
    await wrapper.setData({ selectedComponent: "helpInfoSimilarity" });
    const childComponentToRender = wrapper.vm.selectedComponent;
    expect(childComponentToRender).toBe(`helpInfoSimilarity`);
  });
});
