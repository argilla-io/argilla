/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Database } from "@vuex-orm/core";

import { Pagination, DatasetViewSettings } from "@/models/DatasetViewSettings";
import { Notification } from "@/models/Notifications";
import { AnnotationProgress } from "@/models/AnnotationProgress";

import { ObservationDataset } from "@/models/Dataset";
import { Text2TextDataset } from "@/models/Text2Text";
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
database.register(Text2TextDataset);
database.register(TextClassificationDataset, text_classification);
database.register(TokenClassificationDataset, token_classification);

export default database;
