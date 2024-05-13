import { mount } from "@vue/test-utils";
import RecordExtraActions from "@/components/commons/results/RecordExtraActions";

function mountRecordExtraActions() {
  return mount(RecordExtraActions, {
    idState() {
      return {
        open: true,
      };
    },
    stubs: ["base-action-tooltip", "base-button"],
    propsData: {
      recordId: "recordId",
      recordClipboardText: ["word 1", "word 2"],
      datasetName: "datasetName",
      record: {
        metadata: {
          Metadata: "metadata example",
        },
        status: "Validated",
      },
      allowChangeStatus: true,
      dataset: {
        name: "Dataset1",
      },
    },
  });
}

describe("RecordExtraActions", () => {
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountRecordExtraActions();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
