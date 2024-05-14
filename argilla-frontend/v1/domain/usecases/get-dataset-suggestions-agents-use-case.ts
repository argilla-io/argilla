import { Agent } from "../entities/suggestion/Agent";
import { AgentRepository } from "~/v1/infrastructure/repositories/AgentRepository";

export class GetDatasetSuggestionsAgentsUseCase {
  constructor(private readonly agentRepository: AgentRepository) {}

  execute(datasetId: string): Promise<Agent[]> {
    return this.agentRepository.getAgents(datasetId);
  }
}
