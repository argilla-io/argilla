import { DomainEvent } from "@codescouts/events";
import { Record } from "../entities/record/Record";

export class RecordResponseUpdatedEvent extends DomainEvent {
  constructor(public readonly record: Record) {
    super();
  }
}
