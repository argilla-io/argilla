import { Field } from "../entities/field/Field";
import { Question } from "../entities/question/Question";
import { Suggestion } from "../entities/question/Suggestion";
import { RecordAnswer } from "../entities/record/RecordAnswer";
import { RecordCriteria } from "../entities/record/RecordCriteria";
import { IRecordStorage } from "../services/IRecordStorage";
import { Records, RecordsWithReference } from "../entities/record/Records";
import { Record } from "../entities/record/Record";
import {
  QuestionRepository,
  FieldRepository,
  RecordRepository,
} from "~/v1/infrastructure/repositories";

export class GetRecordsByCriteriaUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly recordsStorage: IRecordStorage
  ) {}

  public async execute(criteria: RecordCriteria): Promise<Records> {
    const { datasetId } = criteria;
    const savedRecords = this.recordsStorage.get();
    savedRecords.synchronizeQueuePagination(criteria);

    const getRecords = this.recordRepository.getRecords(criteria);
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);

    const [recordsFromBackend, questionsFromBackend, fieldsFromBackend] =
      await Promise.all([getRecords, getQuestions, getFields]);

    const recordsToAnnotate = recordsFromBackend.records.map(
      (record, index) => {
        const recordPage = index + criteria.queuePage;

        const fields = fieldsFromBackend
          .filter((f) => record.fields[f.name])
          .map((field) => {
            return new Field(
              field.id,
              field.name,
              field.title,
              record.fields[field.name],
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
              userAnswer.values,
              userAnswer.updated_at
            )
          : null;

        const suggestions = !criteria.page.isBulkMode
          ? record.suggestions.map((suggestion) => {
              return new Suggestion(
                suggestion.id,
                suggestion.question_id,
                suggestion.value,
                suggestion.score,
                suggestion.agent
              );
            })
          : [];

        return new Record(
          record.id,
          datasetId,
          questions,
          fields,
          answer,
          suggestions,
          record.query_score,
          recordPage
        );
      }
    );

    if (criteria.isFilteringBySimilarity) {
      let referenceRecord = savedRecords.getById(
        criteria.similaritySearch.recordId
      );

      if (!referenceRecord) {
        const referenceRecordFromBackend =
          await this.recordRepository.getRecord(
            criteria.similaritySearch.recordId
          );

        const fields = fieldsFromBackend
          .filter((f) => referenceRecordFromBackend.fields[f.name])
          .map((field) => {
            return new Field(
              field.id,
              field.name,
              field.title,
              referenceRecordFromBackend.fields[field.name],
              datasetId,
              field.required,
              field.settings
            );
          });

        referenceRecord = new Record(
          referenceRecordFromBackend.id,
          datasetId,
          [],
          fields,
          null,
          [],
          0,
          0
        );
      }

      const recordsWithReference = new RecordsWithReference(
        recordsToAnnotate,
        recordsFromBackend.total,
        referenceRecord
      );

      return recordsWithReference;
    }

    return new Records(recordsToAnnotate, recordsFromBackend.total);
  }
}
