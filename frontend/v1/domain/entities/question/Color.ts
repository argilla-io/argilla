interface Parts {
  hue: number;
  saturation: number;
  lightness: number;
}

export class Color extends String {
  private constructor(value: string) {
    super(value);
  }

  get parts(): Parts {
    const [hue, saturation, lightness] = this.match(/\d+/g).map(Number);

    return { hue, saturation, lightness };
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
