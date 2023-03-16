import { Rule as RuleModel } from "./Rule.model";

const upsertRulesInRuleModel = async (rules) => {
  await RuleModel.insertOrUpdate({ data: rules });
};

const deleteAllRuleModel = () => {
  RuleModel.deleteAll();
};

export { upsertRulesInRuleModel, deleteAllRuleModel };
