export default class OptionsForRuleMetrics {
  #coverage = 0;
  #coverageAnnotated = 0;
  #totalRecords = 0;
  #annotatedRecords = 0;
  #typeOfTask = "";
  constructor(options, typeOfTask) {
    this.#coverage = options.coverage;
    this.#coverageAnnotated = options.coverageAnnotated;
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

  #getOptionsForTokenClassification() {
    return [
      {
        id: "option1",
        label: "Coverage",
        mainValue: this.#formatToPercent(this.#coverage),
        subValue: this.#formatToFraction(this.#coverage, this.#totalRecords),
        tooltip: {
          tooltipMessage: "tooltip 1",
          tooltipDirection: "right",
        },
      },
      {
        id: "option2",
        label: "Annotated coverage",
        mainValue: this.#formatToPercent(this.#coverageAnnotated),
        subValue: this.#formatToFraction(
          this.#coverageAnnotated,
          this.#annotatedRecords
        ),
        tooltip: {
          tooltipMessage: "tooltip 2",
          tooltipDirection: "left",
        },
      },
    ];
  }

  #formatToPercent(value) {
    return `${value}%`;
  }
  #formatToFraction(value1, value2) {
    return `${value1}/${value2}`;
  }
}
