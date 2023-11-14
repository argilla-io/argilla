import { shallowMount } from "@vue/test-utils";
import RecordText2TextComponent from "./RecordText2Text";

let wrapper = null;

const options = {
  stubs: ["record-string-text-2-text", "Text2TextList"],
  propsData: {
    datasetId: ["workspace", "name"],
    datasetName: "name",
    viewSettings: {},
    record: {
      id: 13611370,
      metadata: {},
      annotation: {
        agent: "recognai",
        sentences: [
          {
            text: "Judy is staying for the weekend. Derek asks Judy to feed his animals on Friday and Saturday. Judy agrees. Derek will give her his keys on Thursday and provide Judy with details. \n\n",
            score: 1,
          },
        ],
      },
      status: "Validated",
      selected: false,
      event_timestamp: "2022-12-21T10:29:01.735435",
      vectors: {},
      last_updated: "2023-01-16T09:15:13.780297",
      search_keywords: [],
      text: "Derek: Judy, r you leaving for the weekend?\r\nJudy: Nah\r\nDerek: So can you feed my animals on Friday and Saturday?\r\nJudy: sure, no problem\r\nDerek: Thank you :) Maybe on Thursday I would give you my keys?\r\nJudy: Ok\r\nDerek: Thanks :) Later I will tell you the details :)\r\nJudy: surely",
    },
    isReferenceRecord: false,
  },
};

beforeEach(() => {
  wrapper = shallowMount(RecordText2TextComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RecordText2TextComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RecordText2TextComponent)).toBe(true);
  });
});
