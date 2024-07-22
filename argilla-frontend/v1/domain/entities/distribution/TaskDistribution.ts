export class TaskDistribution {
  constructor(private readonly status: "completed" | "pending") {}

  get isCompleted() {
    return this.status === "completed";
  }
}
