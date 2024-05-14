import { SearchTextCriteria } from "./SearchTextCriteria";

describe("SearchTextCriteria", () => {
  describe("complete", () => {
    test("should set value to empty strings when urlParams is empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("");

      expect(searchTextCriteria.value).toEqual({
        text: "",
        field: "all",
      });
    });

    test("should set value to text and field when urlParams is not empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("text~field");

      expect(searchTextCriteria.value).toEqual({
        text: "text",
        field: "field",
      });
    });

    test("should set value to text when field is empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("text");

      expect(searchTextCriteria.value).toEqual({
        text: "text",
        field: "all",
      });
    });

    test("should set value correctly if has the separator as a text", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("text~two~three~all");

      expect(searchTextCriteria.value).toEqual({
        text: "text~two~three",
        field: "all",
      });
    });

    test("should set value correctly if has many separators", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("text~~~field");

      expect(searchTextCriteria.value).toEqual({
        text: "text~~",
        field: "field",
      });
    });

    test("should set value correctly with spaces", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.complete("__text_with_spaces__~field");

      expect(searchTextCriteria.value).toEqual({
        text: "__text with spaces__",
        field: "field",
      });
    });
  });

  describe("withValue", () => {
    test("should set value to empty strings when searchTextCriteria value is empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "",
        field: "",
      };

      expect(searchTextCriteria.value).toEqual({
        text: "",
        field: "",
      });
    });

    test("should set value to text and field when searchTextCriteria value is not empty", () => {
      const searchTextCriteria = new SearchTextCriteria();
      const searchTextCriteriaToCopy = new SearchTextCriteria();

      searchTextCriteriaToCopy.value = {
        text: "text",
        field: "field",
      };

      searchTextCriteria.withValue(searchTextCriteriaToCopy);

      expect(searchTextCriteria.value).toEqual({
        text: "text",
        field: "field",
      });
    });
  });

  describe("reset", () => {
    test("should set value to empty strings", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "text",
        field: "field",
      };

      searchTextCriteria.reset();

      expect(searchTextCriteria.value).toEqual({
        text: "",
        field: "all",
      });
    });
  });

  describe("isCompleted", () => {
    test("should return false when text is empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "",
        field: "field",
      };

      expect(searchTextCriteria.isCompleted).toBe(false);
    });

    test("should return true when text is not empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "text",
        field: "field",
      };

      expect(searchTextCriteria.isCompleted).toBe(true);
    });
  });

  describe("urlParams", () => {
    test("should return empty string when isCompleted is false", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "",
        field: "field",
      };

      expect(searchTextCriteria.urlParams).toBe("");
    });

    test("should return text when field is empty", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "text",
        field: "",
      };

      expect(searchTextCriteria.urlParams).toBe("text~all");
    });

    test("should return text and field", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "text",
        field: "field",
      };

      expect(searchTextCriteria.urlParams).toBe("text~field");
    });

    test("should return text and field correctly if the text has the same separator", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "one~two",
        field: "field",
      };

      expect(searchTextCriteria.urlParams).toBe("one~two~field");
    });

    test("should return the url params replacing the spaces to underscores", () => {
      const searchTextCriteria = new SearchTextCriteria();

      searchTextCriteria.value = {
        text: "__text with spaces__",
        field: "field",
      };

      expect(searchTextCriteria.urlParams).toBe("__text_with_spaces__~field");
    });
  });
});
