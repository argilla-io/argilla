# Webhooks internal

Argilla Webhooks implements [Standard Webhooks](https://www.standardwebhooks.com) to facilitate the integration of Argilla with listeners written in any language and ensure consistency and security. If you need to do a custom integration with Argilla webhooks take a look to the [specs](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md) to have a better understanding of how to implement such integration.

## Events payload

The payload is the core part of every webhook. It is the actual data being sent as part of the webhook, and usually consists of important information about the event and related information.

The payloads sent by Argilla webhooks will be a POST request with a JSON body with the following structure:

```json
{
  "type": "example.event",
  "version": 1,
  "timestamp": "2022-11-03T20:26:10.344522Z",
  "data": {
    "foo": "bar",
  }
}
```

Your listener must return any `2XX` status code value to indicate to Argilla that the webhook message has been successfully received. If a different status code is returned Argilla will retry up to 3 times. You have up to 20 seconds to give a response to an Argilla webhook request.

The payload attributes are:

* `type`: a full-stop delimited type string associated with the event. The type indicates the type of the event being sent. (e.g `"dataset.created"` or `"record.completed"`), indicates the schema of the payload (passed in `data` attribute).The following are the values that can be present on this attribute:
    * `dataset.created`
    * `dataset.updated`
    * `dataset.deleted`
    * `dataset.published`
    * `record.created`
    * `record.updated`
    * `record.deleted`
    * `record.completed`
    * `response.created`
    * `response.updated`
    * `response.deleted`
* `version`: an integer with the version of the webhook payload sent. Right now we only support version `1`.
* `timestamp`: the timestamp of when the event occurred.
* `data`: the actual event data associated with the event.

## Events payload examples

In this section we will show payload examples for all the events emitted by Argilla webhooks.

### Dataset events

#### Created

```json
{
  "type": "dataset.created",
  "version": 1,
  "timestamp": "2024-09-26T14:17:20.488053Z",
  "data": {
    "id": "3d673549-ad31-4485-97eb-31f9dcd0df71",
    "name": "fineweb-edu-min",
    "guidelines": null,
    "allow_extra_metadata": true,
    "status": "draft",
    "distribution": {
      "strategy": "overlap",
      "min_submitted": 1
    },
    "workspace": {
      "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
      "name": "argilla",
      "inserted_at": "2024-09-05T11:39:20.377192",
      "updated_at": "2024-09-05T11:39:20.377192"
    },
    "questions": [],
    "fields": [],
    "metadata_properties": [],
    "vectors_settings": [],
    "last_activity_at": "2024-09-26T14:17:20.477163",
    "inserted_at": "2024-09-26T14:17:20.477163",
    "updated_at": "2024-09-26T14:17:20.477163"
  }
}
```

#### Updated

```json
{
  "type": "dataset.updated",
  "version": 1,
  "timestamp": "2024-09-26T14:17:20.504483Z",
  "data": {
    "id": "3d673549-ad31-4485-97eb-31f9dcd0df71",
    "name": "fineweb-edu-min",
    "guidelines": null,
    "allow_extra_metadata": false,
    "status": "draft",
    "distribution": {
      "strategy": "overlap",
      "min_submitted": 1
    },
    "workspace": {
      "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
      "name": "argilla",
      "inserted_at": "2024-09-05T11:39:20.377192",
      "updated_at": "2024-09-05T11:39:20.377192"
    },
    "questions": [],
    "fields": [
      {
        "id": "77578693-9925-4c3d-a921-8c964cdd7acd",
        "name": "text",
        "title": "text",
        "required": true,
        "settings": {
          "type": "text",
          "use_markdown": false
        },
        "inserted_at": "2024-09-26T14:17:20.528738",
        "updated_at": "2024-09-26T14:17:20.528738"
      }
    ]
    "metadata_properties": [],
    "vectors_settings": [],
    "last_activity_at": "2024-09-26T14:17:20.497343",
    "inserted_at": "2024-09-26T14:17:20.477163",
    "updated_at": "2024-09-26T14:17:20.497343"
  }
}
```

#### Deleted

```json
{
  "type": "dataset.deleted",
  "version": 1,
  "timestamp": "2024-09-26T14:21:44.261872Z",
  "data": {
    "id": "3d673549-ad31-4485-97eb-31f9dcd0df71",
    "name": "fineweb-edu-min",
    "guidelines": null,
    "allow_extra_metadata": false,
    "status": "ready",
    "distribution": {
      "strategy": "overlap",
      "min_submitted": 1
    },
    "workspace": {
      "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
      "name": "argilla",
      "inserted_at": "2024-09-05T11:39:20.377192",
      "updated_at": "2024-09-05T11:39:20.377192"
    },
    "questions": [
      {
        "id": "80069251-4792-49e7-b58a-69a6117e8d32",
        "name": "int_score",
        "title": "Rate the quality of the text",
        "description": null,
        "required": true,
        "settings": {
          "type": "rating",
          "options": [
            {
              "value": 0
            },
            {
              "value": 1
            },
            {
              "value": 2
            },
            {
              "value": 3
            },
            {
              "value": 4
            },
            {
              "value": 5
            }
          ]
        },
        "inserted_at": "2024-09-26T14:17:20.541716",
        "updated_at": "2024-09-26T14:17:20.541716"
      },
      {
        "id": "5e7b45c3-b863-48c8-a1e8-2caa279b71e7",
        "name": "comments",
        "title": "Comments:",
        "description": null,
        "required": false,
        "settings": {
          "type": "text",
          "use_markdown": false
        },
        "inserted_at": "2024-09-26T14:17:20.551750",
        "updated_at": "2024-09-26T14:17:20.551750"
      }
    ],
    "fields": [
      {
        "id": "77578693-9925-4c3d-a921-8c964cdd7acd",
        "name": "text",
        "title": "text",
        "required": true,
        "settings": {
          "type": "text",
          "use_markdown": false
        },
        "inserted_at": "2024-09-26T14:17:20.528738",
        "updated_at": "2024-09-26T14:17:20.528738"
      }
    ],
    "metadata_properties": [
      {
        "id": "284945d9-4bda-4fde-9ca0-b3928282ce83",
        "name": "dump",
        "title": "dump",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.560704",
        "updated_at": "2024-09-26T14:17:20.560704"
      },
      {
        "id": "5b8f17e5-1be5-4d99-b3d3-567cfaf33fe3",
        "name": "url",
        "title": "url",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.570162",
        "updated_at": "2024-09-26T14:17:20.570162"
      },
      {
        "id": "a18c60ca-0212-4b22-b1f4-ab3e0fc5ae95",
        "name": "language",
        "title": "language",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.578088",
        "updated_at": "2024-09-26T14:17:20.578088"
      },
      {
        "id": "c5f6d407-87b7-4678-9c7b-28cd002fcefb",
        "name": "language_score",
        "title": "language_score",
        "settings": {
          "min": null,
          "max": null,
          "type": "float"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.585319",
        "updated_at": "2024-09-26T14:17:20.585319"
      },
      {
        "id": "ed3ee682-5d12-4c58-91a2-b1cca89fe62b",
        "name": "token_count",
        "title": "token_count",
        "settings": {
          "min": null,
          "max": null,
          "type": "integer"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.593545",
        "updated_at": "2024-09-26T14:17:20.593545"
      },
      {
        "id": "c807d5dd-3cf0-47b9-b07e-bcf03176115f",
        "name": "score",
        "title": "score",
        "settings": {
          "min": null,
          "max": null,
          "type": "float"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.601316",
        "updated_at": "2024-09-26T14:17:20.601316"
      }
    ],
    "vectors_settings": [],
    "last_activity_at": "2024-09-26T14:17:20.675364",
    "inserted_at": "2024-09-26T14:17:20.477163",
    "updated_at": "2024-09-26T14:17:20.675364"
  }
}
```

#### Published

```json
{
  "type": "dataset.published",
  "version": 1,
  "timestamp": "2024-09-26T14:17:20.680921Z",
  "data": {
    "id": "3d673549-ad31-4485-97eb-31f9dcd0df71",
    "name": "fineweb-edu-min",
    "guidelines": null,
    "allow_extra_metadata": false,
    "status": "ready",
    "distribution": {
      "strategy": "overlap",
      "min_submitted": 1
    },
    "workspace": {
      "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
      "name": "argilla",
      "inserted_at": "2024-09-05T11:39:20.377192",
      "updated_at": "2024-09-05T11:39:20.377192"
    },
    "questions": [
      {
        "id": "80069251-4792-49e7-b58a-69a6117e8d32",
        "name": "int_score",
        "title": "Rate the quality of the text",
        "description": null,
        "required": true,
        "settings": {
          "type": "rating",
          "options": [
            {
              "value": 0
            },
            {
              "value": 1
            },
            {
              "value": 2
            },
            {
              "value": 3
            },
            {
              "value": 4
            },
            {
              "value": 5
            }
          ]
        },
        "inserted_at": "2024-09-26T14:17:20.541716",
        "updated_at": "2024-09-26T14:17:20.541716"
      },
      {
        "id": "5e7b45c3-b863-48c8-a1e8-2caa279b71e7",
        "name": "comments",
        "title": "Comments:",
        "description": null,
        "required": false,
        "settings": {
          "type": "text",
          "use_markdown": false
        },
        "inserted_at": "2024-09-26T14:17:20.551750",
        "updated_at": "2024-09-26T14:17:20.551750"
      }
    ],
    "fields": [
      {
        "id": "77578693-9925-4c3d-a921-8c964cdd7acd",
        "name": "text",
        "title": "text",
        "required": true,
        "settings": {
          "type": "text",
          "use_markdown": false
        },
        "inserted_at": "2024-09-26T14:17:20.528738",
        "updated_at": "2024-09-26T14:17:20.528738"
      }
    ],
    "metadata_properties": [
      {
        "id": "284945d9-4bda-4fde-9ca0-b3928282ce83",
        "name": "dump",
        "title": "dump",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.560704",
        "updated_at": "2024-09-26T14:17:20.560704"
      },
      {
        "id": "5b8f17e5-1be5-4d99-b3d3-567cfaf33fe3",
        "name": "url",
        "title": "url",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.570162",
        "updated_at": "2024-09-26T14:17:20.570162"
      },
      {
        "id": "a18c60ca-0212-4b22-b1f4-ab3e0fc5ae95",
        "name": "language",
        "title": "language",
        "settings": {
          "type": "terms",
          "values": null
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.578088",
        "updated_at": "2024-09-26T14:17:20.578088"
      },
      {
        "id": "c5f6d407-87b7-4678-9c7b-28cd002fcefb",
        "name": "language_score",
        "title": "language_score",
        "settings": {
          "min": null,
          "max": null,
          "type": "float"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.585319",
        "updated_at": "2024-09-26T14:17:20.585319"
      },
      {
        "id": "ed3ee682-5d12-4c58-91a2-b1cca89fe62b",
        "name": "token_count",
        "title": "token_count",
        "settings": {
          "min": null,
          "max": null,
          "type": "integer"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.593545",
        "updated_at": "2024-09-26T14:17:20.593545"
      },
      {
        "id": "c807d5dd-3cf0-47b9-b07e-bcf03176115f",
        "name": "score",
        "title": "score",
        "settings": {
          "min": null,
          "max": null,
          "type": "float"
        },
        "visible_for_annotators": true,
        "inserted_at": "2024-09-26T14:17:20.601316",
        "updated_at": "2024-09-26T14:17:20.601316"
      }
    ],
    "vectors_settings": [],
    "last_activity_at": "2024-09-26T14:17:20.675364",
    "inserted_at": "2024-09-26T14:17:20.477163",
    "updated_at": "2024-09-26T14:17:20.675364"
  }
}
```

### Record events

#### Created

```json
{
  "type": "record.created",
  "version": 1,
  "timestamp": "2024-09-26T14:17:43.078165Z",
  "data": {
    "id": "49e0acda-df13-4f65-8137-2274b3e33c9c",
    "status": "pending",
    "fields": {
      "text": "Taking Play Seriously\nBy ROBIN MARANTZ HENIG\nPublished: February 17, 2008\nOn a drizzly Tuesday night in late January, 200 people came out to hear a psychiatrist talk rhapsodically about play -- not just the intense, joyous play of children, but play for all people, at all ages, at all times."
    },
    "metadata": {
      "dump": "CC-MAIN-2013-20",
      "url": "http://query.nytimes.com/gst/fullpage.html?res=9404E7DA1339F934A25751C0A96E9C8B63&scp=2&sq=taking%20play%20seriously&st=cse",
      "language": "en",
      "language_score": 0.9614589214324951,
      "token_count": 1055,
      "score": 2.5625
    },
    "external_id": "<urn:uuid:316c7af5-14e1-4d0b-9576-753e17ef2cc5>",
    "dataset": {
      "id": "3d673549-ad31-4485-97eb-31f9dcd0df71",
      "name": "fineweb-edu-min",
      "guidelines": null,
      "allow_extra_metadata": false,
      "status": "ready",
      "distribution": {
        "strategy": "overlap",
        "min_submitted": 1
      },
      "workspace": {
        "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
        "name": "argilla",
        "inserted_at": "2024-09-05T11:39:20.377192",
        "updated_at": "2024-09-05T11:39:20.377192"
      },
      "questions": [
        {
          "id": "80069251-4792-49e7-b58a-69a6117e8d32",
          "name": "int_score",
          "title": "Rate the quality of the text",
          "description": null,
          "required": true,
          "settings": {
            "type": "rating",
            "options": [
              {
                "value": 0
              },
              {
                "value": 1
              },
              {
                "value": 2
              },
              {
                "value": 3
              },
              {
                "value": 4
              },
              {
                "value": 5
              }
            ]
          },
          "inserted_at": "2024-09-26T14:17:20.541716",
          "updated_at": "2024-09-26T14:17:20.541716"
        },
        {
          "id": "5e7b45c3-b863-48c8-a1e8-2caa279b71e7",
          "name": "comments",
          "title": "Comments:",
          "description": null,
          "required": false,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-26T14:17:20.551750",
          "updated_at": "2024-09-26T14:17:20.551750"
        }
      ],
      "fields": [
        {
          "id": "77578693-9925-4c3d-a921-8c964cdd7acd",
          "name": "text",
          "title": "text",
          "required": true,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-26T14:17:20.528738",
          "updated_at": "2024-09-26T14:17:20.528738"
        }
      ],
      "metadata_properties": [
        {
          "id": "284945d9-4bda-4fde-9ca0-b3928282ce83",
          "name": "dump",
          "title": "dump",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.560704",
          "updated_at": "2024-09-26T14:17:20.560704"
        },
        {
          "id": "5b8f17e5-1be5-4d99-b3d3-567cfaf33fe3",
          "name": "url",
          "title": "url",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.570162",
          "updated_at": "2024-09-26T14:17:20.570162"
        },
        {
          "id": "a18c60ca-0212-4b22-b1f4-ab3e0fc5ae95",
          "name": "language",
          "title": "language",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.578088",
          "updated_at": "2024-09-26T14:17:20.578088"
        },
        {
          "id": "c5f6d407-87b7-4678-9c7b-28cd002fcefb",
          "name": "language_score",
          "title": "language_score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.585319",
          "updated_at": "2024-09-26T14:17:20.585319"
        },
        {
          "id": "ed3ee682-5d12-4c58-91a2-b1cca89fe62b",
          "name": "token_count",
          "title": "token_count",
          "settings": {
            "min": null,
            "max": null,
            "type": "integer"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.593545",
          "updated_at": "2024-09-26T14:17:20.593545"
        },
        {
          "id": "c807d5dd-3cf0-47b9-b07e-bcf03176115f",
          "name": "score",
          "title": "score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-26T14:17:20.601316",
          "updated_at": "2024-09-26T14:17:20.601316"
        }
      ],
      "vectors_settings": [],
      "last_activity_at": "2024-09-26T14:17:20.675364",
      "inserted_at": "2024-09-26T14:17:20.477163",
      "updated_at": "2024-09-26T14:17:20.675364"
    },
    "inserted_at": "2024-09-26T14:17:43.026852",
    "updated_at": "2024-09-26T14:17:43.026852"
  }
}
```

#### Updated

```json
{
  "type": "record.updated",
  "version": 1,
  "timestamp": "2024-09-26T14:05:30.231988Z",
  "data": {
    "id": "88654411-4eec-4d17-ad73-e5baf59d0efb",
    "status": "completed",
    "fields": {
      "text": "Throughout life there are many times when outside influences change or influence decision-making. The young child has inner motivation to learn and explore, but as he matures, finds outside sources to be a motivating force for development, as well."
    },
    "metadata": {
      "dump": "CC-MAIN-2013-20",
      "url": "http://www.funderstanding.com/category/child-development/brain-child-development/",
      "language": "en",
      "language_score": 0.9633054733276367,
      "token_count": 1062,
      "score": 3.8125
    },
    "external_id": "<urn:uuid:4fafe4c1-2dd0-49fd-8b1b-41d1829f7cdf>",
    "dataset": {
      "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
      "name": "fineweb-edu-min",
      "guidelines": null,
      "allow_extra_metadata": false,
      "status": "ready",
      "distribution": {
        "strategy": "overlap",
        "min_submitted": 1
      },
      "workspace": {
        "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
        "name": "argilla",
        "inserted_at": "2024-09-05T11:39:20.377192",
        "updated_at": "2024-09-05T11:39:20.377192"
      },
      "questions": [
        {
          "id": "faeea416-5390-4721-943c-de7d0212ba20",
          "name": "int_score",
          "title": "Rate the quality of the text",
          "description": null,
          "required": true,
          "settings": {
            "type": "rating",
            "options": [
              {
                "value": 0
              },
              {
                "value": 1
              },
              {
                "value": 2
              },
              {
                "value": 3
              },
              {
                "value": 4
              },
              {
                "value": 5
              }
            ]
          },
          "inserted_at": "2024-09-20T09:39:20.481193",
          "updated_at": "2024-09-20T09:39:20.481193"
        },
        {
          "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
          "name": "comments",
          "title": "Comments:",
          "description": null,
          "required": false,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.490851",
          "updated_at": "2024-09-20T09:39:20.490851"
        }
      ],
      "fields": [
        {
          "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
          "name": "text",
          "title": "text",
          "required": true,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.468254",
          "updated_at": "2024-09-20T09:39:20.468254"
        }
      ],
      "metadata_properties": [
        {
          "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
          "name": "dump",
          "title": "dump",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.499466",
          "updated_at": "2024-09-20T09:39:20.499466"
        },
        {
          "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
          "name": "url",
          "title": "url",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.507944",
          "updated_at": "2024-09-20T09:39:20.507944"
        },
        {
          "id": "98eced0d-d92f-486c-841c-a55085c7538b",
          "name": "language",
          "title": "language",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.517551",
          "updated_at": "2024-09-20T09:39:20.517551"
        },
        {
          "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
          "name": "language_score",
          "title": "language_score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.526219",
          "updated_at": "2024-09-20T09:39:20.526219"
        },
        {
          "id": "0585c420-5885-4fce-9757-82c5199304bc",
          "name": "token_count",
          "title": "token_count",
          "settings": {
            "min": null,
            "max": null,
            "type": "integer"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.534559",
          "updated_at": "2024-09-20T09:39:20.534559"
        },
        {
          "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
          "name": "score",
          "title": "score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.544562",
          "updated_at": "2024-09-20T09:39:20.544562"
        }
      ],
      "vectors_settings": [],
      "last_activity_at": "2024-09-26T14:05:30.129734",
      "inserted_at": "2024-09-20T09:39:20.433798",
      "updated_at": "2024-09-26T14:05:30.130662"
    },
    "inserted_at": "2024-09-20T09:39:23.148539",
    "updated_at": "2024-09-26T14:05:30.224076"
  }
}
```

#### Deleted

```json
{
  "type": "record.deleted",
  "version": 1,
  "timestamp": "2024-09-26T14:45:30.464503Z",
  "data": {
    "id": "5b285767-18c9-46ab-a4ec-5e0ee4e26de9",
    "status": "pending",
    "fields": {
      "text": "This tutorial shows how to send modifications of code in the right way: by using patches.\nThe word developer is used here for someone having a KDE SVN account.\nWe suppose that you have modified some code in KDE and that you are ready to share it. First a few important points:\nNow you have the modification as a source file. Sending the source file will not be helpful, as probably someone else has done other modifications to the original file in the meantime. So your modified file could not replace it."
    },
    "metadata": {
      "dump": "CC-MAIN-2013-20",
      "url": "http://techbase.kde.org/index.php?title=Contribute/Send_Patches&oldid=40759",
      "language": "en",
      "language_score": 0.9597765207290649,
      "token_count": 2482,
      "score": 3.0625
    },
    "external_id": "<urn:uuid:b1579d04-7a6b-420c-9fe2-a0b676d91ec3>",
    "dataset": {
      "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
      "name": "fineweb-edu-min",
      "guidelines": null,
      "allow_extra_metadata": false,
      "status": "ready",
      "distribution": {
        "strategy": "overlap",
        "min_submitted": 1
      },
      "workspace": {
        "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
        "name": "argilla",
        "inserted_at": "2024-09-05T11:39:20.377192",
        "updated_at": "2024-09-05T11:39:20.377192"
      },
      "questions": [
        {
          "id": "faeea416-5390-4721-943c-de7d0212ba20",
          "name": "int_score",
          "title": "Rate the quality of the text",
          "description": null,
          "required": true,
          "settings": {
            "type": "rating",
            "options": [
              {
                "value": 0
              },
              {
                "value": 1
              },
              {
                "value": 2
              },
              {
                "value": 3
              },
              {
                "value": 4
              },
              {
                "value": 5
              }
            ]
          },
          "inserted_at": "2024-09-20T09:39:20.481193",
          "updated_at": "2024-09-20T09:39:20.481193"
        },
        {
          "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
          "name": "comments",
          "title": "Comments:",
          "description": null,
          "required": false,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.490851",
          "updated_at": "2024-09-20T09:39:20.490851"
        }
      ],
      "fields": [
        {
          "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
          "name": "text",
          "title": "text",
          "required": true,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.468254",
          "updated_at": "2024-09-20T09:39:20.468254"
        }
      ],
      "metadata_properties": [
        {
          "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
          "name": "dump",
          "title": "dump",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.499466",
          "updated_at": "2024-09-20T09:39:20.499466"
        },
        {
          "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
          "name": "url",
          "title": "url",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.507944",
          "updated_at": "2024-09-20T09:39:20.507944"
        },
        {
          "id": "98eced0d-d92f-486c-841c-a55085c7538b",
          "name": "language",
          "title": "language",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.517551",
          "updated_at": "2024-09-20T09:39:20.517551"
        },
        {
          "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
          "name": "language_score",
          "title": "language_score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.526219",
          "updated_at": "2024-09-20T09:39:20.526219"
        },
        {
          "id": "0585c420-5885-4fce-9757-82c5199304bc",
          "name": "token_count",
          "title": "token_count",
          "settings": {
            "min": null,
            "max": null,
            "type": "integer"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.534559",
          "updated_at": "2024-09-20T09:39:20.534559"
        },
        {
          "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
          "name": "score",
          "title": "score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.544562",
          "updated_at": "2024-09-20T09:39:20.544562"
        }
      ],
      "vectors_settings": [],
      "last_activity_at": "2024-09-26T14:15:11.139023",
      "inserted_at": "2024-09-20T09:39:20.433798",
      "updated_at": "2024-09-26T14:15:11.141067"
    },
    "inserted_at": "2024-09-20T09:39:23.148687",
    "updated_at": "2024-09-20T09:39:23.148687"
  }
}
```

#### Completed

```json
{
  "type": "record.completed",
  "version": 1,
  "timestamp": "2024-09-26T14:05:30.236958Z",
  "data": {
    "id": "88654411-4eec-4d17-ad73-e5baf59d0efb",
    "status": "completed",
    "fields": {
      "text": "Throughout life there are many times when outside influences change or influence decision-making. The young child has inner motivation to learn and explore, but as he matures, finds outside sources to be a motivating force for development, as well."
    },
    "metadata": {
      "dump": "CC-MAIN-2013-20",
      "url": "http://www.funderstanding.com/category/child-development/brain-child-development/",
      "language": "en",
      "language_score": 0.9633054733276367,
      "token_count": 1062,
      "score": 3.8125
    },
    "external_id": "<urn:uuid:4fafe4c1-2dd0-49fd-8b1b-41d1829f7cdf>",
    "dataset": {
      "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
      "name": "fineweb-edu-min",
      "guidelines": null,
      "allow_extra_metadata": false,
      "status": "ready",
      "distribution": {
        "strategy": "overlap",
        "min_submitted": 1
      },
      "workspace": {
        "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
        "name": "argilla",
        "inserted_at": "2024-09-05T11:39:20.377192",
        "updated_at": "2024-09-05T11:39:20.377192"
      },
      "questions": [
        {
          "id": "faeea416-5390-4721-943c-de7d0212ba20",
          "name": "int_score",
          "title": "Rate the quality of the text",
          "description": null,
          "required": true,
          "settings": {
            "type": "rating",
            "options": [
              {
                "value": 0
              },
              {
                "value": 1
              },
              {
                "value": 2
              },
              {
                "value": 3
              },
              {
                "value": 4
              },
              {
                "value": 5
              }
            ]
          },
          "inserted_at": "2024-09-20T09:39:20.481193",
          "updated_at": "2024-09-20T09:39:20.481193"
        },
        {
          "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
          "name": "comments",
          "title": "Comments:",
          "description": null,
          "required": false,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.490851",
          "updated_at": "2024-09-20T09:39:20.490851"
        }
      ],
      "fields": [
        {
          "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
          "name": "text",
          "title": "text",
          "required": true,
          "settings": {
            "type": "text",
            "use_markdown": false
          },
          "inserted_at": "2024-09-20T09:39:20.468254",
          "updated_at": "2024-09-20T09:39:20.468254"
        }
      ],
      "metadata_properties": [
        {
          "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
          "name": "dump",
          "title": "dump",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.499466",
          "updated_at": "2024-09-20T09:39:20.499466"
        },
        {
          "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
          "name": "url",
          "title": "url",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.507944",
          "updated_at": "2024-09-20T09:39:20.507944"
        },
        {
          "id": "98eced0d-d92f-486c-841c-a55085c7538b",
          "name": "language",
          "title": "language",
          "settings": {
            "type": "terms",
            "values": null
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.517551",
          "updated_at": "2024-09-20T09:39:20.517551"
        },
        {
          "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
          "name": "language_score",
          "title": "language_score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.526219",
          "updated_at": "2024-09-20T09:39:20.526219"
        },
        {
          "id": "0585c420-5885-4fce-9757-82c5199304bc",
          "name": "token_count",
          "title": "token_count",
          "settings": {
            "min": null,
            "max": null,
            "type": "integer"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.534559",
          "updated_at": "2024-09-20T09:39:20.534559"
        },
        {
          "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
          "name": "score",
          "title": "score",
          "settings": {
            "min": null,
            "max": null,
            "type": "float"
          },
          "visible_for_annotators": true,
          "inserted_at": "2024-09-20T09:39:20.544562",
          "updated_at": "2024-09-20T09:39:20.544562"
        }
      ],
      "vectors_settings": [],
      "last_activity_at": "2024-09-26T14:05:30.129734",
      "inserted_at": "2024-09-20T09:39:20.433798",
      "updated_at": "2024-09-26T14:05:30.130662"
    },
    "inserted_at": "2024-09-20T09:39:23.148539",
    "updated_at": "2024-09-26T14:05:30.224076"
  }
}
```

### Response events

#### Created

```json
{
  "type": "response.created",
  "version": 1,
  "timestamp": "2024-09-26T14:05:30.182364Z",
  "data": {
    "id": "7164a58e-3611-4b0a-98cc-9184bc92dc5a",
    "values": {
      "int_score": {
        "value": 3
      }
    },
    "status": "submitted",
    "record": {
      "id": "88654411-4eec-4d17-ad73-e5baf59d0efb",
      "status": "pending",
      "fields": {
        "text": "Throughout life there are many times when outside influences change or influence decision-making. The young child has inner motivation to learn and explore, but as he matures, finds outside sources to be a motivating force for development, as well."
      },
      "metadata": {
        "dump": "CC-MAIN-2013-20",
        "url": "http://www.funderstanding.com/category/child-development/brain-child-development/",
        "language": "en",
        "language_score": 0.9633054733276367,
        "token_count": 1062,
        "score": 3.8125
      },
      "external_id": "<urn:uuid:4fafe4c1-2dd0-49fd-8b1b-41d1829f7cdf>",
      "dataset": {
        "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
        "name": "fineweb-edu-min",
        "guidelines": null,
        "allow_extra_metadata": false,
        "status": "ready",
        "distribution": {
          "strategy": "overlap",
          "min_submitted": 1
        },
        "workspace": {
          "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
          "name": "argilla",
          "inserted_at": "2024-09-05T11:39:20.377192",
          "updated_at": "2024-09-05T11:39:20.377192"
        },
        "questions": [
          {
            "id": "faeea416-5390-4721-943c-de7d0212ba20",
            "name": "int_score",
            "title": "Rate the quality of the text",
            "description": null,
            "required": true,
            "settings": {
              "type": "rating",
              "options": [
                {
                  "value": 0
                },
                {
                  "value": 1
                },
                {
                  "value": 2
                },
                {
                  "value": 3
                },
                {
                  "value": 4
                },
                {
                  "value": 5
                }
              ]
            },
            "inserted_at": "2024-09-20T09:39:20.481193",
            "updated_at": "2024-09-20T09:39:20.481193"
          },
          {
            "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
            "name": "comments",
            "title": "Comments:",
            "description": null,
            "required": false,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.490851",
            "updated_at": "2024-09-20T09:39:20.490851"
          }
        ],
        "fields": [
          {
            "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
            "name": "text",
            "title": "text",
            "required": true,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.468254",
            "updated_at": "2024-09-20T09:39:20.468254"
          }
        ],
        "metadata_properties": [
          {
            "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
            "name": "dump",
            "title": "dump",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.499466",
            "updated_at": "2024-09-20T09:39:20.499466"
          },
          {
            "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
            "name": "url",
            "title": "url",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.507944",
            "updated_at": "2024-09-20T09:39:20.507944"
          },
          {
            "id": "98eced0d-d92f-486c-841c-a55085c7538b",
            "name": "language",
            "title": "language",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.517551",
            "updated_at": "2024-09-20T09:39:20.517551"
          },
          {
            "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
            "name": "language_score",
            "title": "language_score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.526219",
            "updated_at": "2024-09-20T09:39:20.526219"
          },
          {
            "id": "0585c420-5885-4fce-9757-82c5199304bc",
            "name": "token_count",
            "title": "token_count",
            "settings": {
              "min": null,
              "max": null,
              "type": "integer"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.534559",
            "updated_at": "2024-09-20T09:39:20.534559"
          },
          {
            "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
            "name": "score",
            "title": "score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.544562",
            "updated_at": "2024-09-20T09:39:20.544562"
          }
        ],
        "vectors_settings": [],
        "last_activity_at": "2024-09-26T14:05:30.129734",
        "inserted_at": "2024-09-20T09:39:20.433798",
        "updated_at": "2024-09-23T11:08:30.392833"
      },
      "inserted_at": "2024-09-20T09:39:23.148539",
      "updated_at": "2024-09-20T09:39:23.148539"
    },
    "user": {
      "id": "df114042-958d-42c6-9f03-ab49bd451c6c",
      "first_name": "",
      "last_name": null,
      "username": "argilla",
      "role": "owner",
      "inserted_at": "2024-09-05T11:39:20.376463",
      "updated_at": "2024-09-05T11:39:20.376463"
    },
    "inserted_at": "2024-09-26T14:05:30.128332",
    "updated_at": "2024-09-26T14:05:30.128332"
  }
}
```

#### Updated

```json
{
  "type": "response.updated",
  "version": 1,
  "timestamp": "2024-09-26T14:13:22.256501Z",
  "data": {
    "id": "38e4d537-c768-4ced-916e-31b74b220c36",
    "values": {
      "int_score": {
        "value": 5
      }
    },
    "status": "discarded",
    "record": {
      "id": "54b137ae-68a4-4aa4-ab2f-ef350ca96a6b",
      "status": "completed",
      "fields": {
        "text": "Bolivia: Coca-chewing protest outside US embassy\nIndigenous activists in Bolivia have been holding a mass coca-chewing protest as part of campaign to end an international ban on the practice.\nHundreds of people chewed the leaf outside the US embassy in La Paz and in other cities across the country."
      },
      "metadata": {
        "dump": "CC-MAIN-2013-20",
        "url": "http://www.bbc.co.uk/news/world-latin-america-12292661",
        "language": "en",
        "language_score": 0.9660392999649048,
        "token_count": 484,
        "score": 2.703125
      },
      "external_id": "<urn:uuid:a63f6870-f496-4355-adfd-f3296c1577e5>",
      "dataset": {
        "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
        "name": "fineweb-edu-min",
        "guidelines": null,
        "allow_extra_metadata": false,
        "status": "ready",
        "distribution": {
          "strategy": "overlap",
          "min_submitted": 1
        },
        "workspace": {
          "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
          "name": "argilla",
          "inserted_at": "2024-09-05T11:39:20.377192",
          "updated_at": "2024-09-05T11:39:20.377192"
        },
        "questions": [
          {
            "id": "faeea416-5390-4721-943c-de7d0212ba20",
            "name": "int_score",
            "title": "Rate the quality of the text",
            "description": null,
            "required": true,
            "settings": {
              "type": "rating",
              "options": [
                {
                  "value": 0
                },
                {
                  "value": 1
                },
                {
                  "value": 2
                },
                {
                  "value": 3
                },
                {
                  "value": 4
                },
                {
                  "value": 5
                }
              ]
            },
            "inserted_at": "2024-09-20T09:39:20.481193",
            "updated_at": "2024-09-20T09:39:20.481193"
          },
          {
            "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
            "name": "comments",
            "title": "Comments:",
            "description": null,
            "required": false,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.490851",
            "updated_at": "2024-09-20T09:39:20.490851"
          }
        ],
        "fields": [
          {
            "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
            "name": "text",
            "title": "text",
            "required": true,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.468254",
            "updated_at": "2024-09-20T09:39:20.468254"
          }
        ],
        "metadata_properties": [
          {
            "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
            "name": "dump",
            "title": "dump",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.499466",
            "updated_at": "2024-09-20T09:39:20.499466"
          },
          {
            "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
            "name": "url",
            "title": "url",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.507944",
            "updated_at": "2024-09-20T09:39:20.507944"
          },
          {
            "id": "98eced0d-d92f-486c-841c-a55085c7538b",
            "name": "language",
            "title": "language",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.517551",
            "updated_at": "2024-09-20T09:39:20.517551"
          },
          {
            "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
            "name": "language_score",
            "title": "language_score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.526219",
            "updated_at": "2024-09-20T09:39:20.526219"
          },
          {
            "id": "0585c420-5885-4fce-9757-82c5199304bc",
            "name": "token_count",
            "title": "token_count",
            "settings": {
              "min": null,
              "max": null,
              "type": "integer"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.534559",
            "updated_at": "2024-09-20T09:39:20.534559"
          },
          {
            "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
            "name": "score",
            "title": "score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.544562",
            "updated_at": "2024-09-20T09:39:20.544562"
          }
        ],
        "vectors_settings": [],
        "last_activity_at": "2024-09-26T14:13:22.204670",
        "inserted_at": "2024-09-20T09:39:20.433798",
        "updated_at": "2024-09-26T14:07:09.788573"
      },
      "inserted_at": "2024-09-20T09:39:23.148505",
      "updated_at": "2024-09-26T14:06:06.726296"
    },
    "user": {
      "id": "df114042-958d-42c6-9f03-ab49bd451c6c",
      "first_name": "",
      "last_name": null,
      "username": "argilla",
      "role": "owner",
      "inserted_at": "2024-09-05T11:39:20.376463",
      "updated_at": "2024-09-05T11:39:20.376463"
    },
    "inserted_at": "2024-09-26T14:06:06.672138",
    "updated_at": "2024-09-26T14:13:22.206179"
  }
}
```

#### Deleted

```json
{
  "type": "response.deleted",
  "version": 1,
  "timestamp": "2024-09-26T14:15:11.138363Z",
  "data": {
    "id": "7164a58e-3611-4b0a-98cc-9184bc92dc5a",
    "values": {
      "int_score": {
        "value": 3
      }
    },
    "status": "submitted",
    "record": {
      "id": "88654411-4eec-4d17-ad73-e5baf59d0efb",
      "status": "completed",
      "fields": {
        "text": "Throughout life there are many times when outside influences change or influence decision-making. The young child has inner motivation to learn and explore, but as he matures, finds outside sources to be a motivating force for development, as well."
      },
      "metadata": {
        "dump": "CC-MAIN-2013-20",
        "url": "http://www.funderstanding.com/category/child-development/brain-child-development/",
        "language": "en",
        "language_score": 0.9633054733276367,
        "token_count": 1062,
        "score": 3.8125
      },
      "external_id": "<urn:uuid:4fafe4c1-2dd0-49fd-8b1b-41d1829f7cdf>",
      "dataset": {
        "id": "ae2961f0-18a4-49d5-ba0c-40fa863fc8f2",
        "name": "fineweb-edu-min",
        "guidelines": null,
        "allow_extra_metadata": false,
        "status": "ready",
        "distribution": {
          "strategy": "overlap",
          "min_submitted": 1
        },
        "workspace": {
          "id": "350bc020-2cd2-4a67-8b23-37a15c4d8139",
          "name": "argilla",
          "inserted_at": "2024-09-05T11:39:20.377192",
          "updated_at": "2024-09-05T11:39:20.377192"
        },
        "questions": [
          {
            "id": "faeea416-5390-4721-943c-de7d0212ba20",
            "name": "int_score",
            "title": "Rate the quality of the text",
            "description": null,
            "required": true,
            "settings": {
              "type": "rating",
              "options": [
                {
                  "value": 0
                },
                {
                  "value": 1
                },
                {
                  "value": 2
                },
                {
                  "value": 3
                },
                {
                  "value": 4
                },
                {
                  "value": 5
                }
              ]
            },
            "inserted_at": "2024-09-20T09:39:20.481193",
            "updated_at": "2024-09-20T09:39:20.481193"
          },
          {
            "id": "0e14a758-a6d0-43ff-af5b-39f4e4d031ab",
            "name": "comments",
            "title": "Comments:",
            "description": null,
            "required": false,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.490851",
            "updated_at": "2024-09-20T09:39:20.490851"
          }
        ],
        "fields": [
          {
            "id": "a4e81325-7d11-4dcf-af23-d3c867c75c9c",
            "name": "text",
            "title": "text",
            "required": true,
            "settings": {
              "type": "text",
              "use_markdown": false
            },
            "inserted_at": "2024-09-20T09:39:20.468254",
            "updated_at": "2024-09-20T09:39:20.468254"
          }
        ],
        "metadata_properties": [
          {
            "id": "1259d700-2ff6-4315-a3c7-703bce3d65d7",
            "name": "dump",
            "title": "dump",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.499466",
            "updated_at": "2024-09-20T09:39:20.499466"
          },
          {
            "id": "9d135f00-5a51-4506-a607-bc463dce1c2f",
            "name": "url",
            "title": "url",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.507944",
            "updated_at": "2024-09-20T09:39:20.507944"
          },
          {
            "id": "98eced0d-d92f-486c-841c-a55085c7538b",
            "name": "language",
            "title": "language",
            "settings": {
              "type": "terms",
              "values": null
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.517551",
            "updated_at": "2024-09-20T09:39:20.517551"
          },
          {
            "id": "b9f9a3b9-7186-4e23-9147-b5aa52d0d045",
            "name": "language_score",
            "title": "language_score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.526219",
            "updated_at": "2024-09-20T09:39:20.526219"
          },
          {
            "id": "0585c420-5885-4fce-9757-82c5199304bc",
            "name": "token_count",
            "title": "token_count",
            "settings": {
              "min": null,
              "max": null,
              "type": "integer"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.534559",
            "updated_at": "2024-09-20T09:39:20.534559"
          },
          {
            "id": "ae31acb5-f198-4f0b-8d6c-13fcc80d10d1",
            "name": "score",
            "title": "score",
            "settings": {
              "min": null,
              "max": null,
              "type": "float"
            },
            "visible_for_annotators": true,
            "inserted_at": "2024-09-20T09:39:20.544562",
            "updated_at": "2024-09-20T09:39:20.544562"
          }
        ],
        "vectors_settings": [],
        "last_activity_at": "2024-09-26T14:13:22.204670",
        "inserted_at": "2024-09-20T09:39:20.433798",
        "updated_at": "2024-09-26T14:13:22.207478"
      },
      "inserted_at": "2024-09-20T09:39:23.148539",
      "updated_at": "2024-09-26T14:05:30.224076"
    },
    "user": {
      "id": "df114042-958d-42c6-9f03-ab49bd451c6c",
      "first_name": "",
      "last_name": null,
      "username": "argilla",
      "role": "owner",
      "inserted_at": "2024-09-05T11:39:20.376463",
      "updated_at": "2024-09-05T11:39:20.376463"
    },
    "inserted_at": "2024-09-26T14:05:30.128332",
    "updated_at": "2024-09-26T14:05:30.128332"
  }
}
```

## How to implement a listener

Argilla webhooks implements [Standard Webhooks](https://www.standardwebhooks.com) so you can use one of their libraries to implement the verification of webhooks events coming from Argilla, available in many different languages.

The following example is a simple listener written in Ruby, using [sinatra](https://sinatrarb.com) and [standardwebhooks Ruby library](https://github.com/standard-webhooks/standard-webhooks/tree/main/libraries/ruby):

```ruby
require "sinatra"
require "standardwebhooks"

post "/webhook" do
  wh = StandardWebhooks::Webhook.new("YOUR_SECRET")

  headers = {
    "webhook-id" => env["HTTP_WEBHOOK_ID"],
    "webhook-signature" => env["HTTP_WEBHOOK_SIGNATURE"],
    "webhook-timestamp" => env["HTTP_WEBHOOK_TIMESTAMP"],
  }

  puts wh.verify(request.body.read.to_s, headers)
end
```

In the previous snippet we are creating a [sinatra](https://sinatrarb.com) application that listens for `POST` requests on `/webhook` endpoint. We are using the [standardwebhooks Ruby library](https://github.com/standard-webhooks/standard-webhooks/tree/main/libraries/ruby) to verify the incoming webhook event and printing the verified payload on the console.
