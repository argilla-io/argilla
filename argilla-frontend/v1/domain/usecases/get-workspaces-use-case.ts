import { Workspace } from "../entities/workspace/Workspace";
import { WorkspaceRepository } from "~/v1/infrastructure/repositories/WorkspaceRepository";

export class GetWorkspacesUseCase {
  constructor(private workspaceRepository: WorkspaceRepository) {}

  async execute(): Promise<Workspace[]> {
    const workspaces = await this.workspaceRepository.getWorkspaces();

    return workspaces.map((w) => new Workspace(w.id, w.name));
  }
}
