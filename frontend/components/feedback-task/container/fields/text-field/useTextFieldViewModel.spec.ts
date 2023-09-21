import { useTextFieldViewModel } from "./useTextFieldViewModel";

describe("markdown fields", () => {
  test("there is no highlight for markdown fields", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "This",
      useMarkdown: true,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(props.fieldText);
  });
});

describe("string to highlight is empty", () => {
  test("return initial fieldText when sentence is empty", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(props.fieldText);
  });
});

describe("raw text", () => {
  test("the word this must be highlighted", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "this",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a sentence"
    );
  });

  test("the word This must be highlighted", () => {
    const props = {
      fieldText: "This is a sentence",
      stringToHighlight: "This",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">This</span> is a sentence"
    );
  });

  test("the word <p>The HTML must be highlighted", () => {
    const props = {
      fieldText:
        "<p>The HTML <code>button</code> tag defines a clickable button.</p>",
      stringToHighlight: "<p>The HTML",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">&lt;p&gt;The</span> <span class=\"highlight-text\">HTML</span> &lt;code&gt;button&lt;/code&gt; tag defines a clickable button.&lt;/p&gt;"
    );
  });

  test("the word This must be highlighted (with backtick)", () => {
    const props = {
      fieldText: "`This is a sentence",
      stringToHighlight: "`This",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">`This</span> is a sentence"
    );
  });

  test("the word This must be highlighted (surrounded by backticks)", () => {
    const props = {
      fieldText: "`This` is a sentence",
      stringToHighlight: "`This`",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "<span class=\"highlight-text\">`This`</span> is a sentence"
    );
  });

  test("the word This must be highlighted multiple time", () => {
    const props = {
      fieldText: "`This` is a sentence and this sentence",
      stringToHighlight: "this",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      // eslint-disable-next-line prettier/prettier
      "`<span class=\"highlight-text\">This</span>` is a sentence and <span class=\"highlight-text\">this</span> sentence"
    );
  });

  test("escape all HTML characters", () => {
    const props = {
      fieldText:
        "<p>The HTML <code>button</code> tag defines a clickable button.</p>",
      stringToHighlight: "",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      "&lt;p&gt;The HTML &lt;code&gt;button&lt;/code&gt; tag defines a clickable button.&lt;/p&gt;"
    );
  });

  test("not found word", () => {
    const props = {
      fieldText:
        "<p>The HTML <code>button</code> tag defines a clickable button.</p>",
      stringToHighlight: "foo",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      "&lt;p&gt;The HTML &lt;code&gt;button&lt;/code&gt; tag defines a clickable button.&lt;/p&gt;"
    );
  });

  test("not highlight partially", () => {
    const props = {
      fieldText:
        "<p>The HTML <code>button</code> tag defines a clickable button.</p>",
      stringToHighlight: "foo",
      useMarkdown: false,
    };
    const { text } = useTextFieldViewModel(props);
    expect(text.value).toBe(
      "&lt;p&gt;The HTML &lt;code&gt;button&lt;/code&gt; tag defines a clickable button.&lt;/p&gt;"
    );
  });
});
