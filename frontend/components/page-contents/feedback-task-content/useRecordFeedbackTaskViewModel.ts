import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { isNil } from "lodash";
import { useResolve } from "ts-injecty";
import { useFeedback } from "~/v1/infrastructure/FeedbackStorage";

const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
};

export const useRecordFeedbackTaskViewModel = () => {
  const recordRepository = useResolve(RecordRepository);
  const feedbackTask = useFeedback();

  const getRecordsFromBackend = async (
    datasetId: string,
    offset: number,
    status: string,
    searchText: string
  ) => {
    let records = [];
    let totalRecords = null;

    if (isNil(searchText) || !searchText.length) {
      ({ items: records } = await recordRepository.getRecords(
        datasetId,
        offset,
        status
      ));
    } else {
      ({ items: records, totalRecords } = await recordRepository.searchRecords(
        datasetId,
        offset,
        status,
        searchText
      ));
    }

    const feedback = feedbackTask.get();

    feedback.addRecords(records);

    feedbackTask.save(feedback);

    return { records, totalRecords };
  };

  return { getRecordsFromBackend };
};

export class RecordRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getRecords(datasetId, offset, status, numberOfRecordsToFetch = 10) {
    try {
      const url = `/v1/me/datasets/${datasetId}/records`;

      const params = new URLSearchParams();
      params.append("include", "responses");
      if (status === "missing") params.append("include", "suggestions");
      params.append("offset", offset);
      params.append("limit", numberOfRecordsToFetch.toString());
      params.append("response_status", status);

      const { data } = await this.axios.get(url, { params });
      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
      };
    }
  }

  async searchRecords(
    datasetId,
    offset,
    status,
    searchText,
    numberOfRecordsToFetch = 10
  ) {
    try {
      const url = `/v1/me/datasets/${datasetId}/records/search`;

      const body = JSON.parse(
        JSON.stringify({
          query: {
            text: {
              q: searchText,
            },
          },
        })
      );

      const params = {
        include: "responses",
        response_status: status,
        limit: numberOfRecordsToFetch,
        offset,
      };

      const { data } = await this.axios.post(url, body, { params });
      const { items, total: totalRecords } = data;

      const formattedItems = items.map((item) => item.record);
      return { items: formattedItems, totalRecords };
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
      };
    }
  }
}
