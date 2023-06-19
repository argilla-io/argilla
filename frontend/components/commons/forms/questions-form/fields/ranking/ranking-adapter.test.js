import { adaptQuestionsToSots } from "./ranking-adapter";
import { settingsFake } from "./ranking-fakes";

describe("Ranking adapter should", () => {
  it("get the same slots quantity that questions has", () => {
    const { slots, questions } = adaptQuestionsToSots(settingsFake);

    expect(slots.length).toBe(questions.length);
  });

  it("has get adapted options as a question with name", () => {
    const { questions } = adaptQuestionsToSots(settingsFake);

    expect(questions[0].text).toBe("My label");
    expect(questions[1].text).toBe("Other Label");
    expect(questions[2].text).toBe("Wat?!");
    expect(questions[3].text).toBe("Ough!");
  });

  it("has a question id property based on index iteration", () => {
    const { questions } = adaptQuestionsToSots(settingsFake);

    expect(questions[0].value).toBe("label-01");
    expect(questions[1].value).toBe("label-02");
    expect(questions[2].value).toBe("label-03");
    expect(questions[3].value).toBe("label-04");
  });

  it("has slot name created based on index iteration", () => {
    const { slots } = adaptQuestionsToSots(settingsFake);

    expect(slots[0].ranking).toBe(1);
    expect(slots[1].ranking).toBe(2);
    expect(slots[2].ranking).toBe(3);
    expect(slots[3].ranking).toBe(4);
  });

  it("get ranking correctly based on question", () => {
    const { slots, questions, getRanking } = adaptQuestionsToSots(settingsFake);

    slots[1].items.push(questions[0]);

    const rankingExpected = getRanking(questions[0]);

    expect(rankingExpected).toBe(2);
  });
});
