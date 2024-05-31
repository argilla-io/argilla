import { adaptQuestionsToSlots } from "./ranking-adapter";
import { settingsFake } from "./ranking-fakes";

describe("Ranking adapter should", () => {
  it("get the same slots quantity that questions has", () => {
    const { slots, questions } = adaptQuestionsToSlots(settingsFake);

    expect(slots.length).toBe(questions.length);
  });

  it("has get adapted options as a question with name", () => {
    const { questions } = adaptQuestionsToSlots(settingsFake);

    expect(questions[0].text).toBe("My label");
    expect(questions[1].text).toBe("Other Label");
    expect(questions[2].text).toBe("Wat?!");
    expect(questions[3].text).toBe("Ough!");
  });

  it("has a question id property based on index iteration", () => {
    const { questions } = adaptQuestionsToSlots(settingsFake);

    expect(questions[0].value).toBe("label-01");
    expect(questions[1].value).toBe("label-02");
    expect(questions[2].value).toBe("label-03");
    expect(questions[3].value).toBe("label-04");
  });

  it("has slot name created based on index iteration", () => {
    const { slots } = adaptQuestionsToSlots(settingsFake);

    expect(slots[0].rank).toBe(1);
    expect(slots[1].rank).toBe(2);
    expect(slots[2].rank).toBe(3);
    expect(slots[3].rank).toBe(4);
  });

  it("get ranking correctly based on question", () => {
    const { slots, questions, getRanking } =
      adaptQuestionsToSlots(settingsFake);

    slots[1].items.push(questions[0]);

    const rankingExpected = getRanking(questions[0]);

    expect(rankingExpected).toBe(2);
  });

  it("get the same ranking when slot has two questions ranked", () => {
    const { slots, questions, getRanking } =
      adaptQuestionsToSlots(settingsFake);

    slots[1].items.push(questions[0]);
    slots[1].items.push(questions[1]);

    const rankingExpectedOne = getRanking(questions[0]);
    const rankingExpectedTwo = getRanking(questions[0]);

    expect(rankingExpectedOne).toBe(2);
    expect(rankingExpectedTwo).toBe(2);
  });
});
