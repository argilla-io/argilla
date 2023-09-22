import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import {
  BackedRecord,
  BackedRecords,
  BackendAnswerCombinations,
  BackendResponse,
  BackendRecordStatus,
  Response,
} from "../types";
import { MetadataFilterQueryParam } from "../types/metadata";
import { RecordAnswer } from "@/v1/domain/entities/record/RecordAnswer";
import { Record } from "@/v1/domain/entities/record/Record";
import { Question } from "@/v1/domain/entities/question/Question";

const RECORD_API_ERRORS = {
  ERROR_FETCHING_RECORDS: "ERROR_FETCHING_RECORDS",
  ERROR_DELETING_RECORD_RESPONSE: "ERROR_DELETING_RECORD_RESPONSE",
  ERROR_UPDATING_RECORD_RESPONSE: "ERROR_UPDATING_RECORD_RESPONSE",
  ERROR_CREATING_RECORD_RESPONSE: "ERROR_CREATING_RECORD_RESPONSE",
};

export class RecordRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  getRecords(
    datasetId: string,
    fromRecord: number,
    howMany: number,
    status: string,
    searchText: string,
    metadata: MetadataFilterQueryParam[] = []
  ): Promise<BackedRecords> {
    if (searchText?.length)
      return this.getRecordsByText(
        datasetId,
        fromRecord,
        howMany,
        status,
        searchText,
        metadata
      );

    return this.getRecordsDatasetId(
      datasetId,
      fromRecord,
      howMany,
      status,
      metadata
    );
  }

  async deleteRecordResponse(record: Record) {
    if (!record.answer) return;

    try {
      await this.axios.delete(`/v1/responses/${record.answer.id}`);
    } catch (error) {
      throw {
        response: RECORD_API_ERRORS.ERROR_DELETING_RECORD_RESPONSE,
      };
    }
  }

  discardRecordResponse(record: Record): Promise<RecordAnswer> {
    if (record.answer) return this.updateRecordResponse(record, "discarded");

    return this.createRecordResponse(record, "discarded");
  }

  submitNewRecordResponse(record: Record): Promise<RecordAnswer> {
    if (record.answer) return this.updateRecordResponse(record, "submitted");

    return this.createRecordResponse(record, "submitted");
  }

  saveDraft(record: Record): Promise<RecordAnswer> {
    if (record.answer) return this.updateRecordResponse(record, "draft");

    return this.createRecordResponse(record, "draft");
  }

  private async updateRecordResponse(
    record: Record,
    status: BackendRecordStatus
  ) {
    try {
      const request = this.createRequest(status, record.questions);

      const { data } = await this.axios.put<BackendResponse>(
        `/v1/responses/${record.answer.id}`,
        request
      );

      return new RecordAnswer(data.id, status, data.values, data.updated_at);
    } catch (error) {
      throw {
        response: RECORD_API_ERRORS.ERROR_UPDATING_RECORD_RESPONSE,
      };
    }
  }

  private async createRecordResponse(
    record: Record,
    status: BackendRecordStatus
  ) {
    try {
      const request = this.createRequest(status, record.questions);

      const { data } = await this.axios.post<BackendResponse>(
        `/v1/records/${record.id}/responses`,
        request
      );

      return new RecordAnswer(
        data.id,
        data.status,
        data.values,
        data.updated_at
      );
    } catch (error) {
      throw {
        response: RECORD_API_ERRORS.ERROR_CREATING_RECORD_RESPONSE,
      };
    }
  }

  private async getRecordsDatasetId(
    datasetId: string,
    fromRecord: number,
    howMany: number,
    status: string,
    metadata: MetadataFilterQueryParam[]
  ): Promise<BackedRecords> {
    try {
      const url = `/v1/me/datasets/${datasetId}/records`;

      const params = this.createParams(fromRecord, howMany, status, metadata);

      const { data } = await this.axios.get<Response<BackedRecord[]>>(url, {
        params,
      });

      return {
        records: data.items,
        total: data.items.length,
      };
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_RECORDS,
      };
    }
  }

  private async getRecordsByText(
    datasetId: string,
    fromRecord: number,
    howMany: number,
    status: string,
    searchText: string,
    metadata: MetadataFilterQueryParam[]
  ): Promise<BackedRecords> {
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

      const params = this.createParams(fromRecord, howMany, status, metadata);

      const { data } = await this.axios.post(url, body, { params });

      const { items, total } = data;

      const records = items.map((item) => item.record);

      return {
        records,
        total,
      };
    } catch (err) {
      throw {
        response: RECORD_API_ERRORS.ERROR_FETCHING_RECORDS,
      };
    }
  }

  private createRequest(
    status: BackendRecordStatus,
    questions: Question[]
  ): Omit<BackendResponse, "id" | "updated_at"> {
    const values = {} as BackendAnswerCombinations;

    questions
      .filter(
        (question) =>
          question.answer.isValid || question.answer.isPartiallyValid
      )
      .forEach((question) => {
        values[question.name] = { value: question.answer.valuesAnswered };
      });

    return {
      status,
      values,
    };
  }

  private createParams(
    fromRecord: number,
    howMany: number,
    status: string,
    metadata: MetadataFilterQueryParam[]
  ) {
    const offset = `${fromRecord - 1}`;
    const backendStatus = status === "pending" ? "missing" : status;
    const params = new URLSearchParams();

    params.append("include", "responses");
    params.append("include", "suggestions");
    params.append("offset", offset);
    params.append("limit", howMany.toString());
    params.append("response_status", backendStatus);

    if (backendStatus === "missing") params.append("response_status", "draft");

    metadata?.forEach(({ name, value }) => {
      params.append("metadata", `${name}:${value}`);
    });

    return params;
  }
}
