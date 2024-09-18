import { useLanguageDirection } from "./useLanguageDirection";

describe("useLanguageDirection", () => {
  const { isRTL } = useLanguageDirection();

  describe("isRTL should", () => {
    test("be true if the text is Arabic", () => {
      const text = "مرحبا بالعالم";

      const result = isRTL(text);

      expect(result).toBe(true);
    });

    test("be true if the text is Hebrew", () => {
      const text = "שלום עולם";

      const result = isRTL(text);

      expect(result).toBe(true);
    });

    test("be true if the text is Persian", () => {
      const text = "سلام دنیا";

      const result = isRTL(text);

      expect(result).toBe(true);
    });

    test("be false if the text is LTR", () => {
      const text = "Hello World";

      const result = isRTL(text);

      expect(result).toBe(false);
    });

    test("be true if the text has more than RTL characters than LTR characters", () => {
      const text = "هذا نص مثال Hello";

      const result = isRTL(text);

      expect(result).toBe(true);
    });

    test("be false if the text has more LTR characters than RTL characters", () => {
      const text = "Esto es un texto de ejemplo مرحبًا";

      const result = isRTL(text);

      expect(result).toBe(false);
    });
  });
});
