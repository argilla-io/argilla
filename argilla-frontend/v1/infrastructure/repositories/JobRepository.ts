import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendJob } from "../types/dataset";

class JobStatus {
  constructor(public readonly jobId: string, public readonly status: string) {}

  get isQueued() {
    return this.status === "queued";
  }

  get isStarted() {
    return this.status === "started";
  }

  get isFailed() {
    return this.status === "failed";
  }
}

export class JobRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getJobStatus(jobId: string): Promise<JobStatus> {
    try {
      const { data } = await this.axios.get<BackendJob>(`/v1/jobs/${jobId}`);

      return new JobStatus(data.id, data.status);
    } catch {
      return new JobStatus(jobId, "failed");
    }
  }
}
