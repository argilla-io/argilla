import { Color } from "./Color";

describe("Color", () => {
  describe("from", () => {
    test("returns a Color instance", () => {
      const color = Color.from("hsl(0, 80%, 80%)");

      expect(color).toBeInstanceOf(Color);
    });
  });

  describe("generate", () => {
    test("returns the same color for each key", () => {
      const color = Color.generate("key");

      expect(color).toEqual(Color.generate("key"));
    });

    test("returns different colors for different keys", () => {
      const color = Color.generate("key");

      expect(color).not.toEqual(Color.generate("another key"));

      expect(color).not.toEqual(Color.generate("yet another key"));
    });
  });

  describe("parts", () => {
    test("returns the parts of the color", () => {
      const color = Color.from("hsl(0, 80%, 80%)");

      expect(color.parts).toEqual({ hue: 0, saturation: 80, lightness: 80 });
    });
  });
});
