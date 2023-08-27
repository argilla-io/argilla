import { Field } from "../entities/field/Field";
import { Question } from "../entities/question/Question";
import { Record } from "../entities/record/Record";
import { Suggestion } from "../entities/question/Suggestion";
import { IRecordStorage } from "../services/IRecordStorage";
import { Records } from "../entities/record/Records";
import { RecordAnswer } from "../entities/record/RecordAnswer";
import {
  RecordRepository,
  QuestionRepository,
  FieldRepository,
} from "@/v1/infrastructure/repositories";

export class GetRecordsToAnnotateUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly recordsStorage: IRecordStorage
  ) {}

  async execute(
    datasetId: string,
    page: number,
    status: string,
    searchText: string
  ): Promise<void> {
    const savedRecords = this.recordsStorage.get();

    const offsetForPagination = savedRecords.getOffsetToFind(page, status);

    console.log("OFFSET", offsetForPagination);

    const getRecords = this.recordRepository.getRecords(
      datasetId,
      offsetForPagination,
      status,
      searchText
    );
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);

    const [recordsFromBackend, questionsFromBackend, fieldsFromBackend] =
      await Promise.all([getRecords, getQuestions, getFields]);

    const recordsToAnnotate = recordsFromBackend.records.map(
      (record, index) => {
        const fields = Object.keys(record.fields).map((fieldName) => {
          const field = fieldsFromBackend.find(
            (field) => field.name === fieldName
          );

          return new Field(
            field.id,
            field.name,
            field.title,
            record.fields[fieldName],
            datasetId,
            field.required,
            field.settings
          );
        });

        const questions = questionsFromBackend.map((question) => {
          return new Question(
            question.id,
            question.name,
            question.description,
            datasetId,
            question.title,
            question.required,
            question.settings
          );
        });

        const userAnswer = record.responses[0];
        const answer = userAnswer
          ? new RecordAnswer(
              userAnswer.id,
              userAnswer.status,
              userAnswer.values
            )
          : null;

        const suggestions = record.suggestions.map((suggestion) => {
          return new Suggestion(
            suggestion.id,
            suggestion.question_id,
            suggestion.value
          );
        });

        return new Record(
          record.id,
          datasetId,
          questions,
          fields,
          answer,
          suggestions,
          index + page - 1
        );
      }
    );

    const records = new Records(recordsToAnnotate, recordsFromBackend.total);

    this.recordsStorage.add(records);

    console.table(
      {
        pending: this.recordsStorage
          .get()
          .records.filter((r) => r.status === "pending").length,
        submitted: this.recordsStorage
          .get()
          .records.filter((r) => r.status === "submitted").length,
        discarded: this.recordsStorage
          .get()
          .records.filter((r) => r.status === "discarded").length,
      },
      ["Pending", "Submitted", "Discarded"]
    );
  }
}
