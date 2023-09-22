import { Metadata } from "../../metadata/Metadata";

export const metadataMocked = [
  {
    id: "1",
    name: "split",
    description: "The split of the record",
    settings: {
      type: "terms",
      values: ["test", "train", "validation"],
    },
  },
  {
    id: "2",
    name: "loss",
    description: "The training loss affecting the records",
    settings: {
      type: "integer",
    },
  },
  {
    id: "3",
    name: "float",
    description: "The training loss affecting the records",
    settings: {
      type: "float",
    },
  },
];
