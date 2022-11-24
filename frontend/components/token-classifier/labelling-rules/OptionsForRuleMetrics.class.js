export default class OptionsForRuleMetrics {
  #coverage = 0;
  #coverageAnnotated = 0;
  #totalRecords = 0;
  #annotatedRecords = 0;
  #typeOfTask = "";
  constructor(options, typeOfTask) {
    this.#coverage = this.#roundValuesWithSpecificDigit(options.coverage);
    this.#coverageAnnotated = this.#roundValuesWithSpecificDigit(
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

  #getOptionsForTokenClassification() {
    return [
      {
        id: "option1",
        label: "Coverage",
        mainValue: this.#formatToPercent(this.#coverage),
        subValue: this.#formatToFraction(this.#coverage, this.#totalRecords),
        tooltip: {
          tooltipMessage: "Percentage of records labeled by the rule",
          tooltipDirection: "top",
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
          tooltipMessage: "Percentage of annotated records labeled by the rule",
          tooltipDirection: "top",
        },
      },
    ];
  }

  #formatToPercent(value, min = 2, max = 3) {
    const browserLanguage = navigator.language || "en";
    const formatterOptions = {
      style: "percent",
      minimumFractionDigits: min,
      maximumFractionDigits: max,
    };

    const formatter = new Intl.NumberFormat(browserLanguage, formatterOptions);
    return formatter.format(value);
  }

  #formatToFraction(value, total) {
    return `${Math.round(value * total)}/${total}`;
  }

  #roundValuesWithSpecificDigit(value, numberOfDigit = 4) {
    return Number(value.toFixed(numberOfDigit));
  }
}
