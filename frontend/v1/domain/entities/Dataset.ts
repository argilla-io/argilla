export class Dataset {
  private readonly originalGuidelines: string;
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
    public readonly updatedAt: string
  ) {
    this.originalGuidelines = guidelines;
  }

  public get workspace() {
    return this.workspaceName;
  }

  public get areGuidelinesModified(): boolean {
    return this.guidelines !== this.originalGuidelines;
  }
}
