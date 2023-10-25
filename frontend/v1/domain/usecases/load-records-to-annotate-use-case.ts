import { Field } from "../entities/field/Field";
import { Question } from "../entities/question/Question";
import { Record } from "../entities/record/Record";
import { Suggestion } from "../entities/question/Suggestion";
import { IRecordStorage } from "../services/IRecordStorage";
import { Records, RecordsWithReference } from "../entities/record/Records";
import { RecordAnswer } from "../entities/record/RecordAnswer";
import { RecordCriteria } from "../entities/record/RecordCriteria";
import {
  RecordRepository,
  QuestionRepository,
  FieldRepository,
} from "@/v1/infrastructure/repositories";

export type LoadRecordsMode = "append" | "replace";

export class LoadRecordsToAnnotateUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly recordsStorage: IRecordStorage
  ) {}

  async load(mode: LoadRecordsMode, criteria: RecordCriteria): Promise<void> {
    const { page } = criteria;

    let newRecords = await this.loadRecords(mode, criteria);

    let isRecordExistForCurrentPage = newRecords.existsRecordOn(page);

    if (!isRecordExistForCurrentPage && page !== 1) {
      criteria.page = 1;

      newRecords = await this.loadRecords(mode, criteria);

      isRecordExistForCurrentPage = newRecords.existsRecordOn(page);
    }

    if (isRecordExistForCurrentPage) {
      const record = newRecords.getRecordOn(page);

      record.initialize();
    }

    criteria.commit();
  }

  async paginate(criteria: RecordCriteria): Promise<boolean> {
    const { page } = criteria;
    let records = this.recordsStorage.get();
    let isNextRecordExist = records.existsRecordOn(page);

    if (!isNextRecordExist) {
      records = await this.loadRecords("append", criteria);

      isNextRecordExist = records.existsRecordOn(page);
    }

    if (isNextRecordExist) {
      const record = records.getRecordOn(page);

      record.initialize();

      criteria.commit();
    }

    return isNextRecordExist;
  }

  private async loadRecords(mode: LoadRecordsMode, criteria: RecordCriteria) {
    const { datasetId, page } = criteria;
    const savedRecords = this.recordsStorage.get();
    const pagination = savedRecords.getPageToFind(criteria);

    const getRecords = this.recordRepository.getRecords(criteria, pagination);

    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);

    const [recordsFromBackend, questionsFromBackend, fieldsFromBackend] =
      await Promise.all([getRecords, getQuestions, getFields]);

    const recordsToAnnotate = recordsFromBackend.records.map(
      (record, index) => {
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
          index + page
        );
      }
    );

    if (criteria.similaritySearch.isCompleted) {
      const recordsWithReference = new RecordsWithReference(
        recordsToAnnotate,
        recordsFromBackend.total,
        savedRecords.getById(criteria.similaritySearch.recordId)
      );

      this.recordsStorage.save(recordsWithReference);

      return recordsWithReference;
    }

    const records = new Records(recordsToAnnotate, recordsFromBackend.total);

    if (mode === "append") {
      this.recordsStorage.append(records);
    } else {
      this.recordsStorage.replace(records);
    }

    return records;
  }
}
