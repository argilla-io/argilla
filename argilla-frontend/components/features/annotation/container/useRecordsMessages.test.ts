import { useRecordMessages } from "./useRecordsMessages";
import { Metrics } from "~/v1/domain/entities/dataset/Metrics";
import { Progress } from "~/v1/domain/entities/dataset/Progress";
import { RecordStatus } from "~/v1/domain/entities/record/RecordAnswer";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

jest.mock("~/v1/infrastructure/storage/MetricsStorage");
const useMetricsMocked = jest.mocked(useMetrics);
jest.mock("~/v1/infrastructure/storage/TeamProgressStorage");
const useTeamProgressMocked = jest.mocked(useTeamProgress);

const createRecordCriteria = (
  status: RecordStatus,
  isFilteredByText = false
) => {
  const criteria = new RecordCriteria(
    "datasetId",
    "1",
    status,
    isFilteredByText ? "searchText" : "",
    "",
    "",
    "",
    "",
    ""
  );

  criteria.commit();

  return criteria;
};

const createRecordsMockWith = (hasRecordsToAnnotate: boolean) => {
  return new Records([], 0, hasRecordsToAnnotate);
};

const METRICS = {
  EMPTY: () => new Metrics(0, 0, 0, 0, 0),
  WITH_20_ANNOTATED: () => new Metrics(20, 0, 0, 0, 0),
};

const PROGRESS = {
  EMPTY: () => new Progress(0, 0, 0),
  COMPLETED: () => new Progress(20, 20, 0),
  IN_PROGRESS: () => new Progress(20, 10, 10),
};

const mockMetricsWith = (metrics: Metrics) => {
  useMetricsMocked.mockReturnValue({
    state: metrics,
    save: jest.fn(),
    get: jest.fn(),
  });
};

const mockTamProgressWith = (progress: Progress) => {
  useTeamProgressMocked.mockReturnValue({
    state: progress,
    save: jest.fn(),
    get: jest.fn(),
  });
};

describe("useRecordsMessages", () => {
  describe("getMessagesForLoading should", () => {
    test("return `The dataset is empty message' when the dataset no have records", () => {
      const recordCriteria = createRecordCriteria("pending");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.EMPTY());
      mockTamProgressWith(PROGRESS.EMPTY());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "The dataset is empty, start to upload records (include code snippet for admin/owner) / come back soon (annotator)"
      );
    });

    test("return 'The task is completed' when team progress mark as completed", () => {
      const recordCriteria = createRecordCriteria("pending");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.COMPLETED());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe("🎉 The task is completed!");
    });

    test.each(["pending", "draft", "submitted", "discarded"])(
      "return 'No have %s records matching with a query' when no have records",
      (status: RecordStatus) => {
        const recordCriteria = createRecordCriteria(status, true);
        const records = createRecordsMockWith(false);

        mockMetricsWith(METRICS.WITH_20_ANNOTATED());

        mockTamProgressWith(PROGRESS.IN_PROGRESS());

        const { getMessagesForLoading } = useRecordMessages(recordCriteria);

        expect(getMessagesForLoading(records)).toBe(
          `You have no ${status} records matching your query`
        );
      }
    );

    test("return 'No have draft records' when the draft queue is empty", () => {
      const recordCriteria = createRecordCriteria("draft");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "You have no records with draft responses / You have no records in draft"
      );
    });

    test("return 'No have submitted records yet' when the submitted queue is empty", () => {
      const recordCriteria = createRecordCriteria("submitted");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "You have not submitted any record yet"
      );
    });

    test.each(["pending", "discarded"])(
      "return 'No have %s records' when %s queue is empty",
      (status: RecordStatus) => {
        const recordCriteria = createRecordCriteria(status);
        const records = createRecordsMockWith(false);

        mockMetricsWith(METRICS.WITH_20_ANNOTATED());

        mockTamProgressWith(PROGRESS.IN_PROGRESS());

        const { getMessagesForLoading } = useRecordMessages(recordCriteria);

        expect(getMessagesForLoading(records)).toBe(
          `You have no ${status} records`
        );
      }
    );

    test("return null when have records to annotate", () => {
      const recordCriteria = createRecordCriteria("pending");
      const records = createRecordsMockWith(true);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBeNull();
    });
  });

  describe("getMessageForPagination should", () => {
    test("return 'The task is completed' when team progress mark as completed", () => {
      const recordCriteria = createRecordCriteria("pending");

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.COMPLETED());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(true)).toBe("🎉 The task is completed!");
    });

    test("return 'No have pending records' when pending queue is empty", () => {
      const recordCriteria = createRecordCriteria("pending");

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(false)).toBe(
        "🎉 Your have no pending records to annotate"
      );
    });

    test("return 'No have draft records' when draft queue is empty", () => {
      const recordCriteria = createRecordCriteria("draft");

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(false)).toBe(
        "Your have no draft records to review"
      );
    });

    test("return 'No have discarded records' when discarded queue is empty", () => {
      const recordCriteria = createRecordCriteria("discarded");

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(false)).toBe(
        "You have no discarded records"
      );
    });

    test("return null when have records to annotate", () => {
      const recordCriteria = createRecordCriteria("pending");

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(true)).toBeNull();
    });
  });
});
