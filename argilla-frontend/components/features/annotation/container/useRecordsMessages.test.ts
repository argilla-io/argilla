import { useRecordMessages } from "./useRecordsMessages";
import { Metrics } from "~/v1/domain/entities/dataset/Metrics";
import { Progress } from "~/v1/domain/entities/dataset/Progress";
import { RecordStatus } from "~/v1/domain/entities/record/RecordAnswer";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";
import { useRole } from "~/v1/infrastructure/services";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

jest.mock("~/v1/infrastructure/storage/MetricsStorage");
const useMetricsMocked = jest.mocked(useMetrics);
jest.mock("~/v1/infrastructure/storage/TeamProgressStorage");
const useTeamProgressMocked = jest.mocked(useTeamProgress);

jest.mock("~/v1/infrastructure/services/useRole");
const useRoleMocked = jest.mocked(useRole);

class RecordCriteriaMocked extends RecordCriteria {
  constructor(
    private readonly _isFilteringByAdvanceSearch: boolean,
    datasetId: string,
    datasetVersion: string,
    status: RecordStatus,
    searchText: string,
    metadata: string,
    sortBy: string,
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    super(
      datasetId,
      datasetVersion,
      status,
      searchText,
      metadata,
      sortBy,
      response,
      suggestion,
      similaritySearch
    );
  }

  get isFilteringByAdvanceSearch() {
    return this._isFilteringByAdvanceSearch;
  }
}

const createRecordCriteria = (
  status: RecordStatus,
  isFilteringByAdvanceSearch = false
) => {
  const criteria = new RecordCriteriaMocked(
    isFilteringByAdvanceSearch,
    "datasetId",
    "1",
    status,
    "",
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
useRoleMocked.mockReturnValue({
  isAdminOrOwner: jest.fn(),
  isAdminOrOwnerRole: {
    value: true,
  } as any,
});

describe("useRecordsMessages", () => {
  describe("getMessagesForLoading should", () => {
    test("return `The dataset is empty message for admin' when the dataset no have records and the logged in user is admin or owner", () => {
      const recordCriteria = createRecordCriteria("pending");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.EMPTY());
      mockTamProgressWith(PROGRESS.EMPTY());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "#noRecordsMessages.datasetEmptyForAdmin#"
      );
    });

    test("return `The dataset is empty message for annotator' when the dataset no have records and the logged in user is annotator", () => {
      const recordCriteria = createRecordCriteria("pending");
      const records = createRecordsMockWith(false);
      useRoleMocked.mockReturnValue({
        isAdminOrOwner: jest.fn(),
        isAdminOrOwnerRole: {
          value: false,
        } as any,
      });

      mockMetricsWith(METRICS.EMPTY());
      mockTamProgressWith(PROGRESS.EMPTY());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "#noRecordsMessages.datasetEmptyForAnnotator#"
      );
    });

    test("return 'The task is completed' when team progress mark as completed and does not have records to annotate", () => {
      const recordCriteria = createRecordCriteria("pending", false);
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.COMPLETED());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "#noRecordsMessages.taskDistributionCompleted#"
      );
    });

    test.each(["pending", "draft", "submitted", "discarded"])(
      "return 'No have %s records matching with a query' when no have records",
      (status: RecordStatus) => {
        const isFilteringByAdvanceSearch = true;
        const recordCriteria = createRecordCriteria(
          status,
          isFilteringByAdvanceSearch
        );
        const records = createRecordsMockWith(false);

        mockMetricsWith(METRICS.WITH_20_ANNOTATED());

        mockTamProgressWith(PROGRESS.IN_PROGRESS());

        const { getMessagesForLoading } = useRecordMessages(recordCriteria);

        expect(getMessagesForLoading(records)).toBe(
          `#noRecordsMessages.noRecordsFound.#recordStatus.${status}.2##`
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
        "#noRecordsMessages.noDraftRecordsToReview#"
      );
    });

    test("return 'No have submitted records yet' when the submitted queue is empty", () => {
      const recordCriteria = createRecordCriteria("submitted");
      const records = createRecordsMockWith(false);

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessagesForLoading } = useRecordMessages(recordCriteria);

      expect(getMessagesForLoading(records)).toBe(
        "#noRecordsMessages.noSubmittedRecords#"
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
          `#noRecordsMessages.noRecords.#recordStatus.${status}.2##`
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
      const hasRecordsOnNextPage = false;

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.COMPLETED());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(hasRecordsOnNextPage)).toBe(
        "#noRecordsMessages.taskDistributionCompleted#"
      );
    });

    test("return 'No have pending records' when pending queue is empty", () => {
      const recordCriteria = createRecordCriteria("pending");
      const hasRecordsOnNextPage = false;

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(hasRecordsOnNextPage)).toBe(
        "#noRecordsMessages.noPendingRecordsToAnnotate#"
      );
    });

    test("return 'No have draft records' when draft queue is empty", () => {
      const recordCriteria = createRecordCriteria("draft");
      const hasRecordsOnNextPage = false;

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(hasRecordsOnNextPage)).toBe(
        "#noRecordsMessages.noDraftRecordsToReview#"
      );
    });

    test("return 'No have discarded records' when discarded queue is empty", () => {
      const recordCriteria = createRecordCriteria("discarded");
      const hasRecordsOnNextPage = false;

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(hasRecordsOnNextPage)).toBe(
        "#noRecordsMessages.noRecords.#recordStatus.discarded.2##"
      );
    });

    test("return null when have records to annotate", () => {
      const recordCriteria = createRecordCriteria("pending");
      const hasRecordsOnNextPage = true;

      mockMetricsWith(METRICS.WITH_20_ANNOTATED());

      mockTamProgressWith(PROGRESS.IN_PROGRESS());

      const { getMessageForPagination } = useRecordMessages(recordCriteria);

      expect(getMessageForPagination(hasRecordsOnNextPage)).toBeNull();
    });
  });
});
