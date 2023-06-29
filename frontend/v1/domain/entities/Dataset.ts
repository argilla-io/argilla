export class Dataset {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly guidelines: string,
    public readonly status: string,
    public readonly workspaceId: string,
    public readonly workspaceName: string,
    public readonly createdAt: string,
    public readonly lastUpdated: string,
  ) {}

  public get workspace() {
    return this.workspaceName;
  }

  public get tags() {
    return {};
  }

  public get task() {
    return "FeedbackTask";
  }

  public get link() {
    return {
      name: "dataset-id-annotation-mode",
      params: {
        id: this.id,
      },
    };
  }
}
