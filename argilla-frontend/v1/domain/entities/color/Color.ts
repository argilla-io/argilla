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
    if (value.startsWith('#')) {
      value = Color.hexToCssHsl(value)
    }
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

  static hexToCssHsl(hex: string): string {
      // Normalize Hex Code
      hex = hex.replace(/^#/, '').toLowerCase();
      // Convert the three-character hex code into a six--character code
      if (hex.length === 3) {
          hex = hex.split('').map(char => char + char).join('');
      }
      // Parse the hex code
      const result = /^([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      if (!result || result.length !== 4) throw `Failed to parse hex: ${hex}`;

      let r = parseInt(result[1], 16) / 255;
      let g = parseInt(result[2], 16) / 255;
      let b = parseInt(result[3], 16) / 255;
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      const delta = max - min;
      let h = 0, s = 0, l = (max + min) / 2;

      if (delta !== 0) {
          s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
          switch (max) {
            case r: h = (g - b) / delta + (g < b ? 6 : 0); break;
            case g: h = (b - r) / delta + 2; break;
            case b: h = (r - g) / delta + 4; break;
          }
          h = Math.round(h * 60);
      }

      s = Math.round(s * 100);
      l = Math.round(l * 100);

      const hslString = `hsl(${h},${s}%,${l}%)`;
      return hslString;
  }
}
