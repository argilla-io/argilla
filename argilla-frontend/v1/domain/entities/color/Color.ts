import { Guard } from "../error";

interface Parts {
  hue: number;
  saturation: number;
  lightness: number;
}

interface Palette {
  veryDark: string;
  dark: string;
  light: string;
  veryLight: string;
}

export class Color extends String {
  public readonly parts: Parts;
  public readonly palette: Palette;

  private constructor(value: string) {
    const [hue, saturation, lightness] = value.match(/\d+/g).map(Number);

    Guard.condition(
      hue === undefined || saturation === undefined || lightness === undefined,
      "The value color must be HSL for now."
    );

    super(value);

    this.parts = { hue, saturation, lightness };

    this.palette = {
      veryDark: `hsl(${hue}, 50%, 40%)`,
      dark: `hsl(${hue}, 60%, 60%)`,
      light: `hsl(${hue}, 80%, 92%)`,
      veryLight: `hsl(${hue}, 30%, 96%)`,
    };
  }

  static from(value: string): Color {
    return new Color(value);
  }

  static generate(key: string): Color {
    const generatedColor = this.colorGenerator(key);

    return Color.from(generatedColor);
  }

  private static colorGenerator(key: string, saturation = 80, lightness = 80) {
    const stringUniqueHash = [...key].reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);

    return `hsl(${Math.abs(
      stringUniqueHash % 360
    )}, ${saturation}%, ${lightness}%)`;
  }
}
