import { isNil } from "lodash";

const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
};

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = async (
    datasetId,
    offset,
    responseStatus,
    numberOfRecordsToFetch = 10
  ) => {
    try {
      const url = `/v1/me/datasets/${datasetId}/records`;
      const params = {
        include: "responses",
        offset,
        limit: numberOfRecordsToFetch,
        response_status: responseStatus,
      };
      const { data } = await this.$axios.get(url, { params });
      return data;
    } catch (err) {
      console.warn(err);
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
      };
    }
  };
  const searchRecords = async (
    datasetId,
    offset,
    responseStatus,
    searchText,
    numberOfRecordsToFetch = 10
  ) => {
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
        response_status: responseStatus,
        limit: numberOfRecordsToFetch,
        offset,
      };

      const { data } = await this.$axios.post(url, body, { params });
      const { items, total: totalRecords } = data;

      const formattedItems = items.map((item) => item.record);
      return { items: formattedItems, totalRecords };
    } catch (err) {
      console.warn(err);
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_RECORDS,
      };
    }
  };

  const getRecordsFromBackend = async (
    datasetId: string,
    offset: number,
    status: string,
    searchText: string
  ) => {
    let records = [];
    let totalRecords = null;

    if (isNil(searchText) || !searchText.length) {
      ({ items: records } = await getRecords(datasetId, offset, status));
    } else {
      ({ items: records, totalRecords } = await searchRecords(
        datasetId,
        offset,
        status,
        searchText
      ));
    }

    return { records, totalRecords };
  };

  return { getRecordsFromBackend };
};
