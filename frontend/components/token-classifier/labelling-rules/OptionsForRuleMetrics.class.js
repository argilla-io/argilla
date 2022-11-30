import _ from "lodash";
export default class OptionsForRuleMetrics {
  #coverage = 0;
  #coverageAnnotated = 0;
  #totalRecords = 0;
  #annotatedRecords = 0;
  #typeOfTask = "";
  #charToShowIfEmpty = "-";
  constructor(options, typeOfTask) {
    this.#coverage = this.#changeCoverage(options.coverage);
    this.#coverageAnnotated = this.#changeCoverageAnnotated(
      options.coverageAnnotated
    );
    this.#totalRecords = options.totalRecords;
    this.#annotatedRecords = options.annotatedRecords;
    this.#typeOfTask = typeOfTask;
  }

  getOptions() {
    if (this.#typeOfTask === "TOKEN_ANNOTATION") {
      return this.#getOptionsForTokenClassification();
    } else {
      return {};
    }
  }

  setMetrics({ coverage, coverageAnnotated, totalRecords, annotatedRecords }) {
    if (this.#typeOfTask === "TOKEN_ANNOTATION") {
      this.#changeCoverage(coverage);
      this.#changeCoverageAnnotated(coverageAnnotated);
      this.#changeTotalRecords(totalRecords);
      this.#changeAnnotatedRecords(annotatedRecords);
    }
  }

  #changeCoverage(coverage) {
    this.#coverage = this.#roundValuesWithSpecificDigit(coverage);
  }
  #changeCoverageAnnotated(coverageAnnotated) {
    this.#coverageAnnotated =
      this.#roundValuesWithSpecificDigit(coverageAnnotated);
  }
  #changeTotalRecords(totalRecords) {
    this.#totalRecords = totalRecords;
  }
  #changeAnnotatedRecords(annotatedRecords) {
    this.#annotatedRecords = annotatedRecords;
  }

  #getOptionsForTokenClassification() {
    return [
      {
        id: "option1",
        label: "Coverage",
        mainValue: this.#formatToPercent(this.#coverage),
        subValue: this.#formatSubValue(this.#coverage, this.#totalRecords),
        tooltip: {
          tooltipMessage: "Percentage of records labeled by the rule",
          tooltipDirection: "top",
        },
      },
      {
        id: "option2",
        label: "Annotated coverage",
        mainValue: this.#formatToPercent(this.#coverageAnnotated),
        subValue: this.#formatSubValue(
          this.#coverageAnnotated,
          this.#annotatedRecords
        ),
        tooltip: {
          tooltipMessage: "Percentage of annotated records labeled by the rule",
          tooltipDirection: "top",
        },
      },
    ];
  }

  #formatToPercent(value, min = 2, max = 3) {
    if (!_.isNil(value)) {
      const browserLanguage = navigator.language || "en";
      const formatterOptions = {
        style: "percent",
        minimumFractionDigits: min,
        maximumFractionDigits: max,
      };

      const formatter = new Intl.NumberFormat(
        browserLanguage,
        formatterOptions
      );
      return formatter.format(value);
    }
    return `${this.#charToShowIfEmpty}%`;
  }

  #formatSubValue(value, total) {
    const numerator = _.isNil(value)
      ? this.#charToShowIfEmpty
      : this.#roundValue(value * total);
    const denominator = _.isNil(total) ? this.#charToShowIfEmpty : total;

    return this.#formatToFraction(numerator, denominator);
  }

  #roundValue(value) {
    return Math.ceil(value);
  }

  #formatToFraction(numerator, denominator) {
    return `${numerator}/${denominator}`;
  }

  #roundValuesWithSpecificDigit(value, numberOfDigit = 4) {
    return _.isNil(value) ? value : Number(value.toFixed(numberOfDigit));
  }
}
