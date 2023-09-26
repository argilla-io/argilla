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
      min: 0,
      max: 2,
    },
  },
  {
    id: "3",
    name: "float",
    description: "The training loss affecting the records",
    settings: {
      type: "float",
      min: 0.1,
      max: 3.76,
    },
  },
  {
    id: "4",
    name: "split_2",
    description: "The split of the record",
    settings: {
      type: "terms",
      values: ["test", "train", "validation"],
    },
  },
  {
    id: "5",
    name: "split_3",
    description: "The split of the record",
    settings: {
      type: "terms",
      values: ["test", "train", "validation"],
    },
  },
];

export const createMetadataMock = () =>
  metadataMocked.map((metadata) => {
    return new Metadata(
      metadata.id,
      metadata.name,
      metadata.description,
      metadata.settings
    );
  });
