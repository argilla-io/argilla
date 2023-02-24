import { mount } from "@vue/test-utils";
import EntitiesSelector from "@/components/token-classifier/results/EntitiesSelector";
const $entitiesMaxColors = 50;

function mountEntitiesSelector() {
  return mount(EntitiesSelector, {
    stubs: ["entity-label"],
    propsData: {
      datasetId: ["workspace", "name"],
      datasetLastSelectedEntity: {
        color_id: 14,
        shortcut: "1",
        text: "Arreglo",
      },
      formattedEntities: [
        {
          color_id: 14,
          shortcut: "1",
          text: "Arreglo",
        },
        {
          color_id: 1,
          shortcut: "2",
          text: "CARDINAL",
        },
      ],
      token: {
        end: 73,
        entity: {
          end: 73,
          end_token: 15,
          label: "Arreglo",
          start: 57,
          start_token: 13,
        },
        origin: "annotation",
      },
      showEntitiesSelector: true,
      suggestedLabel: "GPE",
    },
    mocks: {
      $entitiesMaxColors,
    },
  });
}

describe("EntitiesSelector", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountEntitiesSelector();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
