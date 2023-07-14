import { type NuxtAxiosInstance } from "@nuxtjs/axios";
export const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
};

export class RecordRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getRecords(datasetId, offset, status, numberOfRecordsToFetch = 10) {
    try {
      const url = `/v1/me/datasets/${datasetId}/records`;

      const params = new URLSearchParams();
      params.append("include", "responses");
      params.append("include", "suggestions");
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

      const params = new URLSearchParams();
      params.append("include", "responses");
      params.append("include", "suggestions");
      params.append("offset", offset);
      params.append("limit", numberOfRecordsToFetch.toString());
      params.append("response_status", status);

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
