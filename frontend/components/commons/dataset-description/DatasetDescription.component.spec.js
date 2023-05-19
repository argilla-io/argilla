import { shallowMount } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";
import * as Mocked from "./MockedService";

const options = {
  propsData: {
    datasetId: "FAKE_ID",
    datasetTask: "FAKE_TASK"
  },
};

jest.mock("marked", () => {
  return {
    marked: {
      parse: jest.fn((value) => `${value}-PARSED`)
    }
  }
})

describe("DatasetDescriptionComponent should", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  })

  it("render the component", () => {
    const wrapper = shallowMount(DatasetDescription, options);

    expect(wrapper.is(DatasetDescription)).toBe(true);
  });

  it("see the dataset description", () => {
    jest.spyOn(Mocked, "getDatasetDescription").mockReturnValue("FAKE_DESCRIPTION");
    const wrapper = shallowMount(DatasetDescription, options);

    const description = wrapper.find(".description__markdown__viewer-text");

    expect(description.element.innerHTML).toBe("FAKE_DESCRIPTION-PARSED")
  });

  it("save description when user click on save button", async () => {
    const saveDescriptionMocked = jest.spyOn(Mocked, "saveDescription");
    const wrapper = shallowMount(DatasetDescription, options);
    await wrapper.find("[name=edit-button]").trigger("on-click");

    await wrapper.find("[name=description-input]").setValue("NEW_DESCRIPTION")

    await wrapper.find("[name=save-button]").trigger("on-click");

    expect(saveDescriptionMocked).toHaveBeenCalledWith("FAKE_ID", "FAKE_TASK", "NEW_DESCRIPTION");
  })

  it("discard new description if the user cancel edition", async () => {
    const saveDescriptionMocked = jest.spyOn(Mocked, "saveDescription");
    const wrapper = shallowMount(DatasetDescription, options);
    await wrapper.find("[name=edit-button]").trigger("on-click");
    await wrapper.find("[name=description-input]").setValue("NEW_DESCRIPTION")

    await wrapper.find("[name=close-button]").trigger("on-click");

    expect(saveDescriptionMocked).toHaveBeenCalledTimes(0);

    expect(wrapper.find(".description__markdown__viewer-text").element.innerHTML).toBe("FAKE_DESCRIPTION-PARSED")
  })
});
