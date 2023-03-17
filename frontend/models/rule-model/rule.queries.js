import { Rule as RuleModel, formatDatasetIdForRuleModel } from "./Rule.model";
import { getDatasetModelPrimaryKey } from "@/models/Dataset";

// Getters
const getAllRulesByDatasetId = (datasetId, savedInDataset = true) => {
  const formattedDatasetId = formatDatasetIdForRuleModel(datasetId);
  return RuleModel.query()
    .where("dataset_id", formattedDatasetId)
    .where("is_saved_in_dataset", savedInDataset)
    .get();
};

const getQueryRuleArrayByDatasetNameAndWorkspace = ({
  datasetName,
  datasetWorkspace,
}) => {
  const datasetId = getDatasetModelPrimaryKey({
    name: datasetName,
    workspace: datasetWorkspace,
  });
  const rules = getAllRulesByDatasetId(datasetId);

  return rules.map((rule) => rule.query);
};

// Exists
const isAnyRuleByDatasetNameAndWorkspace = ({
  datasetName,
  datasetWorkspace,
}) => {
  const datasetId = formatDatasetId({ datasetName, datasetWorkspace });
  return RuleModel.query().where("dataset_id", datasetId).exists();
};

// Insert and update
const upsertRulesInRuleModel = async (rules) => {
  await RuleModel.insertOrUpdate({ data: rules });
};

// Delete
const deleteAllRuleModel = () => {
  RuleModel.deleteAll();
};

// Utils
const formatDatasetId = ({ datasetName, datasetWorkspace }) => {
  const datasetPrimaryKey = getDatasetModelPrimaryKey({
    name: datasetName,
    workspace: datasetWorkspace,
  });

  const formattedDatasetId = formatDatasetIdForRuleModel(datasetPrimaryKey);

  return formattedDatasetId;
};

export {
  getAllRulesByDatasetId,
  getQueryRuleArrayByDatasetNameAndWorkspace,
  upsertRulesInRuleModel,
  deleteAllRuleModel,
  isAnyRuleByDatasetNameAndWorkspace,
};
