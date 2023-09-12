import { useTextFieldViewModel } from "./useTextFieldViewModel";

describe("useTextFieldViewModel highlight text without any words between backtick", () => {
  test("return the fieldText if the string to highlight is empty", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText if the string to highlight is not found", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "word",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText with the corresponding word highlighted", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "This",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a sentence"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the case", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "THIs",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a sentence"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the position in the fieldtext", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "Is",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> a sentence"
    );
  });

  test("return the fieldText with corresponding words highlighted independently of the number of words", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "Is A",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> <span class=\"highlight-text\">a</span> sentence"
    );
  });
});

describe("useTextFieldViewModel highlight text with a markdown with one word", () => {
  test("return the fieldText if the string to highlight is empty", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText if the string to highlight is not found", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "word",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText with the corresponding word highlighted", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "This",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a `sentence`"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the case", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "THIs",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a `sentence`"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the position in the fieldtext", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "Is",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> a `sentence`"
    );
  });

  test("return the fieldText with corresponding words highlighted independently of the number of words and without highlighting the markdown word", () => {
    const props = {
      fieldText: "This is a `sentence`",
      stringToHighlight: "Is a `Sentence`",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> <span class=\"highlight-text\">a</span> `sentence`"
    );
  });
});

describe("useTextFieldViewModel highlight text with a markdown with several words", () => {
  test("return the fieldText if the string to highlight is empty", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText if the string to highlight is not found", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "word",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText with the corresponding word highlighted", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "This",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is `a sentence`"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the case", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "THIs",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is `a sentence`"
    );
  });

  test("return the fieldText with the corresponding word highlighted independently of the position in the fieldtext", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "Is",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> `a sentence`"
    );
  });

  test("return the fieldText with corresponding words highlighted independently of the number of words and without highlighting the markdown word", () => {
    const props = {
      fieldText: "This is `a sentence`",
      stringToHighlight: "Is `a Sentence`",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "This <span class=\"highlight-text\">is</span> `a sentence`"
    );
  });
});

describe("sentence with duplicated words and markdown", () => {
  test("return the fieldText if the string to highlight is empty", () => {
    const props = {
      fieldText: "record record records `recordssss` rEcOrD RECORD",
      stringToHighlight: "",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(props.fieldText);
  });

  test("return the fieldText with the corresponding exact matching words", () => {
    const props = {
      fieldText: "record record records `recordssss` rEcOrD RECORD",
      stringToHighlight: "record",
      useMarkdown: true,
    };

    const { text } = useTextFieldViewModel(props);

    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">record</span> <span class=\"highlight-text\">record</span> records `recordssss` <span class=\"highlight-text\">rEcOrD</span> <span class=\"highlight-text\">RECORD</span>"
    );
  });
});
