import { shallowMount } from "@vue/test-utils";
import DatasetDescription from "./DatasetDescription.component";
import * as Mocked from "./MockedService";

const options = {
  propsData: {
    datasetId: "FAKE_ID",
    datasetTask: "FAKE_TASK"
  },
};
describe("DatasetDescriptionComponent should", () => {
  it("render the component", () => {
    const wrapper = shallowMount(DatasetDescription, options);

    expect(wrapper.is(DatasetDescription)).toBe(true);
  });

  it("see description", () => {
    jest.spyOn(Mocked, "getDatasetDescription").mockReturnValue("FAKE_DESCRIPTION");
    const wrapper = shallowMount(DatasetDescription, options);

    const description = wrapper.find(".description__text");

    expect(description.element.innerHTML).toBe("FAKE_DESCRIPTION")
  });

  it("save description when user click on save button", async () => {
    const saveDescriptionMocked = jest.spyOn(Mocked, "saveDescription");
    const wrapper = shallowMount(DatasetDescription, options);
    await wrapper.find("[name=edit-button]").trigger("on-click");

    await wrapper.find("[name=save-button]").trigger("on-click");

    expect(saveDescriptionMocked).toHaveBeenCalledWith("FAKE_ID", "FAKE_TASK", "TEMPORAL_TODO_REMOVE");
  })
});
