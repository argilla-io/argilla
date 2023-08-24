const RECORD_STATUS = Object.freeze({
  PENDING: "PENDING",
  DISCARDED: "DISCARDED",
  SUBMITTED: "SUBMITTED",
});

const RECORD_STATUS_COLOR = Object.freeze({
  PENDING: "#b6b9ff",
  DISCARDED: "#c3c1c1",
  SUBMITTED: "#3e5cc9",
});

// NOTE - IMPORTANT : in the backend, the status are in lowercase
const RESPONSE_STATUS_FOR_API = Object.freeze({
  MISSING: "missing",
  DISCARDED: "discarded",
  SUBMITTED: "submitted",
});

export { RECORD_STATUS, RECORD_STATUS_COLOR, RESPONSE_STATUS_FOR_API };
