import { Database } from "@vuex-orm/core";

import { Pagination, DatasetViewSettings } from "@/models/DatasetViewSettings";
import { Notification } from "@/models/Notifications";
import { AnnotationProgress } from "@/models/AnnotationProgress";

import { ObservationDataset } from "@/models/Dataset";
import { TextClassificationDataset } from "@/models/TextClassification";
import { TokenClassificationDataset } from "@/models/TokenClassification";

import datasets from "@/database/modules/datasets";
import text_classification from "@/database/modules/text_classification";
import token_classification from "@/database/modules/token_classification";

import notifications from "@/database/modules/notifications";

const database = new Database();

database.register(DatasetViewSettings);
database.register(Pagination);
database.register(AnnotationProgress);
database.register(Notification, notifications);

database.register(ObservationDataset, datasets);
database.register(TextClassificationDataset, text_classification);
database.register(TokenClassificationDataset, token_classification);

export default database;
