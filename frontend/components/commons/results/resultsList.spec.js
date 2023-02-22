import { shallowMount, createLocalVue } from "@vue/test-utils";
import ResultsListComponent from "./ResultsList";
import Vuex from "vuex";
// jest.mock("@/models/TextClassification.js");

const localVue = createLocalVue();
localVue.use(Vuex);

let store = null;
let getters = {};
store = new Vuex.Store({ getters });

let wrapper = null;

const options = {
  stubs: [
    "TextClassificationResultsList",
    "TokenClassificationResultsList",
    "Text2TextResultsList",
  ],
  localVue,
  store,
  propsData: {
    datasetId: ["workspace", "name"],
    datasetTask: "TextClassification",
  },
};

beforeEach(() => {
  wrapper = shallowMount(ResultsListComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("ResultsListComponent", () => {
  it.skip("render the component", async () => {
    // FIXME - solved the undefined getter => see https://dev.to/anthonygore/dependency-mocks-a-secret-weapon-for-vue-unit-tests-3af
    expect(wrapper.is(ResultsListComponent)).toBe(true);
  });
});
