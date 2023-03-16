import { Rule as RuleModel, formatDatasetIdForRuleModel } from "./Rule.model";
import { getDatasetModelPrimaryKey } from "@/models/Dataset";

// Exists
const isAnyRuleByDatasetId = ({ datasetName, datasetWorkspace }) => {
  const datasetId = formatDatasetId({ datasetName, datasetWorkspace });
  return RuleModel.query().where("dataset_id", datasetId).exists();
};

// insert and update
const upsertRulesInRuleModel = async (rules) => {
  await RuleModel.insertOrUpdate({ data: rules });
};

// delete
const deleteAllRuleModel = () => {
  RuleModel.deleteAll();
};

// utils
const formatDatasetId = ({ datasetName, datasetWorkspace }) => {
  console.log(datasetName);
  const datasetPrimaryKey = getDatasetModelPrimaryKey({
    name: datasetName,
    workspace: datasetWorkspace,
  });

  const formattedDatasetId = formatDatasetIdForRuleModel(datasetPrimaryKey);

  return formattedDatasetId;
};

export { upsertRulesInRuleModel, deleteAllRuleModel, isAnyRuleByDatasetId };
