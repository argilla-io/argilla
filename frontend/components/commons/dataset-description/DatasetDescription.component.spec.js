import { shallowMount, mount, createLocalVue } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";
import MarkdownEditorComponent from "./MarkdownEditor.component";
import BaseSpinner from "@/components/base/BaseSpinner";
import { Notification } from "@/models/Notifications";

jest.mock("@/models/dataset.utilities", () => ({
  getDatasetFromORM: () => ({
      guidelines: "text",
    }),
}));

let wrapper = null;
const options = {
  components: { BaseSpinner, MarkdownEditorComponent },
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
    const spinner = wrapper.find('basespinner-stub')

    expect(spinner.exists()).toBe(true)
  });

  it("shows the markdown editor when the data is loaded", () => {
    const editor = wrapper.find('markdowneditorcomponent-stub')

    expect(editor.exists()).toBe(true)
  });

  it("sends the updated guidelines to the API", async () => {
    const spy = jest.spyOn(DatasetDescription.methods, 'updateGuidelines')
    jest.spyOn(Notification, 'dispatch').mockImplementation(() => {})

    wrapper = mount(DatasetDescription, options)

    const button = wrapper.find('base-button')
    await button.trigger('on-click')

    expect(spy).toHaveBeenCalled()

    spy.mockClear()
  })

  it("Sends an error notification when saving the guidelines fail", async () => {
    const updateSpy = jest.spyOn(DatasetDescription.methods, 'updateDatasetGuidelines').mockImplementation(() => {
      throw new Error();
    });

    const dispatchSpy = jest.spyOn(Notification, 'dispatch').mockImplementation(() => {})

    wrapper = mount(DatasetDescription, options)

    const button = wrapper.find('base-button')
    await button.trigger('on-click')

    expect(dispatchSpy).toHaveBeenCalled()

    dispatchSpy.mockClear()
    updateSpy.mockClear()
  })
});
