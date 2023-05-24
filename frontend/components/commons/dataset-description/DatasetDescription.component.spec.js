import { shallowMount, mount, createLocalVue } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";

jest.mock("@/models/dataset.utilities", () => ({
  getDatasetFromORM: () => ({
      guidelines: "text",
    }),
}));

let wrapper = null;
const options = {
  propsData: {
    isLoading: false,
    datasetId: ['argilla', 'dataset-id'],
    datasetTask: 'TokenClassification',
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

  it("shows the loading spinner when data is not loaded", async () => {
    await wrapper.setProps({isLoading: true})
    const spinner = wrapper.find('basespinner')

    expect(spinner.exists()).toBe(true)
  });

  it("shows the markdown editor when the data is loaded", () => {
    const editor = wrapper.find('markdown-editor-stub')

    expect(editor.exists()).toBe(true)
  });

  it("sends the updated guidelines to the API", async () => {
    const spy = jest.spyOn(DatasetDescription.methods, 'updateGuidelines')
    wrapper = mount(DatasetDescription, options)

    const button = wrapper.find('base-button')
    await button.trigger('click')

    expect(spy).toHaveBeenCalled()

    spy.mockClear()
  })
});
