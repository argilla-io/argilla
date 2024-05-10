interface OriginalVector {
  title: string;
}
export class Vector {
  private original: OriginalVector;
  constructor(
    public readonly id: string,
    public readonly name: string,
    public title: string,
    public readonly dimensions: number,
    public readonly datasetId: string
  ) {
    this.initializeOriginal();
  }

  public get isModified(): boolean {
    return this.title.trim() !== this.original.title;
  }

  private MAX_TITLE_LENGTH = 500;
  public validate(): Record<"title", string[]> {
    const validations: Record<"title", string[]> = {
      title: [],
    };

    if (this.title?.length > this.MAX_TITLE_LENGTH)
      validations.title.push(
        `This must be less than ${this.MAX_TITLE_LENGTH}.`
      );

    return validations;
  }

  public get isValid(): boolean {
    return this.validate().title.length === 0;
  }

  restore() {
    this.title = this.original.title;
  }

  update(title: string) {
    this.title = title;

    this.initializeOriginal();
  }

  private initializeOriginal() {
    this.original = {
      title: this.title,
    };
  }
}
