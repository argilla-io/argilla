import { factoryRanking } from "./ranking-adapter";
import { settingsFake } from "./ranking-fakes";

describe("Ranking adapter should", () => {
  it("get the same slots quantity that questions has", () => {
    const { slots, questions } = factoryRanking(settingsFake);

    expect(slots.length).toBe(questions.length);
  });

  it("has get adapted options as a question with name", () => {
    const { questions } = factoryRanking(settingsFake);

    expect(questions[0].name).toBe("My label");
    expect(questions[1].name).toBe("Other Label");
    expect(questions[2].name).toBe("Wat?!");
    expect(questions[3].name).toBe("Ough!");
  });

  it("has a question id property based on index iteration", () => {
    const { questions } = factoryRanking(settingsFake);

    expect(questions[0].id).toBe(1);
    expect(questions[1].id).toBe(2);
    expect(questions[2].id).toBe(3);
    expect(questions[3].id).toBe(4);
  });

  it("has slot name created based on index iteration", () => {
    const { slots } = factoryRanking(settingsFake);

    expect(slots[0].name).toBe("#1");
    expect(slots[1].name).toBe("#2");
    expect(slots[2].name).toBe("#3");
    expect(slots[3].name).toBe("#4");
  });
});
