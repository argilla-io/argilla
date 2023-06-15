// props
// this props came from settings
const ranking_slots = [
  {
    text: "First place",
  },
  {
    text: "Second place",
  },
  {
    text: "Out of top 2",
  },
];

// this props came from settings
const options0 = [
  {
    value: "label-01",
    text: "My label",
    description: "This is an optional field",
  },
];
const options1 = [
  {
    value: "label-01",
    text: "My label",
    description: "This is an optional field",
  },
  { value: "label-02", text: "My other Label" },
  { value: "label-03", text: "Wat?!" },
  { value: "label-04", text: "Ough!" },
];

// this props came from record responses (or value)
const responses0 = [{ value: "label-01", ranking: 1 }];
const responses1 = [
  { value: "label-01", ranking: 1 },
  { value: "label-02", ranking: 1 },
  { value: "label-03", ranking: 2 },
  { value: "label-04", ranking: 3 },
];
const responses2 = [
  { value: "label-01", ranking: 1 },
  { value: "label-02", ranking: 1 },
  { value: "label-03", ranking: 2 },
  { value: "label-04", ranking: 100000 },
];

// expected result
const expectedRanking0 = [
  {
    text: "First place",
    ranking: 1,
    items: [
      {
        value: "label-01",
        text: "My label",
        description: "This is an optional field",
      },
    ],
  },
  {
    text: "Second place",
    ranking: 2,
    items: [],
  },
  {
    text: "Out of top 2",
    ranking: 3,
    items: [],
  },
];
const expectedRanking1 = [
  {
    text: "First place",
    ranking: 1,
    items: [
      {
        value: "label-01",
        text: "My label",
        description: "This is an optional field",
      },
      { value: "label-02", text: "My other Label" },
    ],
  },
  {
    text: "Second place",
    ranking: 2,
    items: [{ value: "label-03", text: "Wat?!" }],
  },
  {
    text: "Out of top 2",
    ranking: 3,
    items: [{ value: "label-04", text: "Ough!" }],
  },
];
const expectedRanking3 = [
  {
    text: "First place",
    ranking: 1,
    items: [
      {
        value: "label-01",
        text: "My label",
        description: "This is an optional field",
      },
      { value: "label-02", text: "My other Label" },
    ],
  },
  {
    text: "Second place",
    ranking: 2,
    items: [{ value: "label-03", text: "Wat?!" }],
  },
  {
    text: "Out of top 2",
    ranking: 3,
    items: [],
  },
];

const factoryRanking = ({ ranking_slots, options, responses }) => {
  const outputs = ranking_slots.map((rankingSlot, index) => {
    const ranking = index + 1;
    const filteredResponses = responses.filter(
      (response) => response.ranking == ranking
    );

    const items = filteredResponses.map((response) => {
      const optionToResponse = options.find(
        (option) => option.value == response.value
      );
      if (optionToResponse) {
        return optionToResponse;
      }
    });

    return { ...rankingSlot, ranking, items };
  });

  return outputs;
};

describe("test the factory function to init ranking", () => {
  it("init ranking list for case 0", () => {
    expect(
      factoryRanking({
        ranking_slots,
        options: options0,
        responses: responses0,
      })
    ).toStrictEqual(expectedRanking0);
  });
  it("init ranking list for case 1", () => {
    expect(
      factoryRanking({
        ranking_slots,
        options: options1,
        responses: responses1,
      })
    ).toStrictEqual(expectedRanking1);
  });
  it("not add the responses if the corresponding ranking was not find", () => {
    expect(
      factoryRanking({
        ranking_slots,
        options: options1,
        responses: responses2,
      })
    ).toStrictEqual(expectedRanking3);
  });
});
