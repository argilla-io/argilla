import { Feedback } from "../domain/entities/Feedback";
import { IDatasetsStorage } from "../domain/services/IDatasetsStorage";
import { useStoreFor } from "../store/create";

const useStoreForFeedback = useStoreFor<Feedback, IDatasetsStorage>(Feedback);

export const useFeedback = () => useStoreForFeedback();
