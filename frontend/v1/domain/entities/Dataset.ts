export class Dataset {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly task: string,
    public readonly guidelines: string,
    public readonly status: string,
    public readonly workspaceId: string,
    public readonly workspaceName: string,
    public readonly tags: unknown,
    public readonly createdAt: string,
    public readonly updatedAt: string
  ) {}

  public get workspace() {
    return this.workspaceName;
  }
}
