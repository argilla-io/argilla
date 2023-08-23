export class Dataset {
  private originalGuidelines: string;
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly task: string,
    public guidelines: string,
    public readonly status: string,
    public readonly workspaceId: string,
    public readonly workspaceName: string,
    public readonly tags: unknown,
    public readonly createdAt: string,
    public updatedAt: string
  ) {
    this.originalGuidelines = guidelines;
  }

  public get workspace() {
    return this.workspaceName;
  }

  public get isModified(): boolean {
    return this.guidelines !== this.originalGuidelines;
  }

  restore() {
    this.guidelines = this.originalGuidelines;
  }

  update(when: string) {
    this.originalGuidelines = this.guidelines;
    this.updatedAt = when;
  }
}
