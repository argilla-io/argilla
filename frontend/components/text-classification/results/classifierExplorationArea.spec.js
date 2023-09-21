import { shallowMount } from "@vue/test-utils";
import ClassifierExplorationAreaComponent from "./ClassifierExplorationArea";

let wrapper = null;

const options = {
  propsData: {
    record: {
      id: "00171137-272c-43d0-a8e8-d05f7ed8eb49",
      metadata: {},
      annotation: {
        agent: "recognai",
        labels: [{ class: "card_arrival", score: 1 }],
      },
      status: "Validated",
      selected: false,
      event_timestamp: "2022-12-22T11:11:28.214440",
      vectors: {},
      last_updated: "2023-01-17T11:03:30.613183",
      search_keywords: [],
      inputs: {
        text: "I made a deposit this morning but it is still pending?",
      },
      multi_label: false,
    },
    datasetName: "name",
    paginationSize: 10,
  },
};

beforeEach(() => {
  wrapper = shallowMount(ClassifierExplorationAreaComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("ClassifierExplorationAreaComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(ClassifierExplorationAreaComponent)).toBe(true);
  });
});
