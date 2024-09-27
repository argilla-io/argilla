---
description: Learn how to create custom fields using HTML, CSS, and JavaScript templates in Argilla.
---

# Custom fields with layout templates

This guide demonstrates how to create custom fields in Argilla using HTML, CSS, and JavaScript templates.

!!! info "Main Class"

    ```python
    rg.CustomField(
        name="custom",
        title="Custom",
        template="<div>{{record.fields.custom.key}}</div>",
        advanced_mode=False,
        required=True,
        description="Field description",
    )
    ```

    > Check the [CustomField - Python Reference](../reference/argilla/settings/fields.md#src.argilla.settings._field.CustomField) to see the attributes, arguments, and methods of the `CustomField` class in detail.

## Understanding the Record Object

The `record` object is the main object that contains all the information about the Argilla `record` object in the UI, like `fields`, `metadata`, etc. Your template can use this object to display record information within the custom field.

## Using Handlebars in your template

By default, custom fields will use the [handlebars syntax engine](https://handlebarsjs.com/) to render templates with `record` information. This engine will convert the content inside the brackets `{{}}` to the values of record's field's object that you reference within your template. As described in the [Accessing record information](#accessing-record-information) section, you can access the fields of the record by navigating to `{{record.fields.<field_name>}}`. For more complex use cases, handlebars has various [expressions, partials, and helpers](https://handlebarsjs.com/guide/) that you can use to render your data. You can deactivate the `handlebars` engine with the `advanced_mode=False` parameter in `CustomField`, then you will need to define custom javascript to access the record attributes.

### Usage example

Because of the handlebars syntax engine, we only need to pass the HTML between `<script>` tags and potentially some CSS in
between the `<style>` tags.

```python
css_template = """
<style>
.div {
    font-weight: bold;
}
</style>
""" # (1)

html_template = """
<div>{{record.fields.custom.key}}</div>
""" # (2)
```

1. This is a CSS template, which ensures that the text inside the `div` is bold.
2. This is an HTML template, which creates a `div` and injects the value corresponding to the `key` of the `custom` field into it.

We can now pass these templates to the `CustomField` class.

```python
import argilla as rg

custom_field = rg.CustomField(
    name="custom",
    template=css_template + html_template,
    advanced_mode=False
)

settings = rg.Settings(
    fields=[custom_field],
    questions=[rg.TextQuestion(name="response")],
)

dataset = rg.Dataset(
    name="custom_field_dataset",
    settings=settings,
)


dataset.records.log(
    rg.Record(
        fields={
            "custom": {"key": "value"},
        }
    )
)
```

### Example Gallery

=== "Show images in two columns"

    ```python
    template = """
    <style>
    #container {
        display: flex;
        gap: 10px;
    }
    .column {
        flex: 1;
    }
    </style>
    <div id="container">
        <div class="column">
            <h3>Original text</h3>
            <div>{{record.fields.text.original}}</div>
        </div>
        <div class="column">
            <h3>Revision</h3>
            <div>{{record.fields.text.revision}}</div>
        </div>
    </div>
    """
    record_object = rg.Record(
        fields={
            "text": {
                "original": "Hello, world!",
                "revision": "Hello, Argilla!",
            }
        }
    )
    ```

=== "Show metadata in a table"

    ```python
    template = """
    <style>
    .container {
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
        width: 100%;
        max-width: 400px;
    }
    .header {
        display: flex;
        background-color: #f2f2f2;
        font-weight: bold;
        border-bottom: 1px solid #ddd;
    }
    .row {
        display: flex;
        border-bottom: 1px solid #ddd;
    }
    .row:last-child {
        border-bottom: none;
    }
    .column {
        flex: 1;
        padding: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .column:first-child {
        border-right: 1px solid #ddd;
    }
    </style>
    <div class="container">
        <div class="header">
            <div class="column">Metadata</div>
            <div class="column">Value</div>
        </div>
        {{#each record_object.metadata}}
        <div class="row">
            <div class="column">{{@key}}</div>
            <div class="column">{{this}}</div>
        </div>
        {{/each}}
    </div>
    """

## Advanced Mode

When `advanced_mode=True`, you can use the `template` argument to pass a full HTML page. This allows for more complex customizations, including the use of JavaScript.

### Usage example

Let's reproduce example from the [Without advanced mode](#without-advanced-mode) section but this time we will insert the [handlebars syntax engine](https://handlebarsjs.com/) ourselves.

```python
render_template = """
<script id="template" type="text/x-handlebars-template">
    <style>
        .div {{
            font-weight: bold;
        }}
    </style>
    <div class="div">{{record.fields.custom.key}}</div>
</script>
""" # (1)

script = """
<script src="https://cdn.jsdelivr.net/npm/handlebars@latest/dist/handlebars.min.js"></script>
<script>
    const template = document.getElementById('template').innerHTML;
    const rendered = Handlebars.compile(template);
    document.body.innerHTML = rendered({{"key": "value"}});
    // Compile the Handlebars template
    const template = Handlebars.compile(document.getElementById('template').innerHTML);
    const rendered = template({ record: record_object });
    document.getElementById('container').innerHTML = rendered;
</script>
""" # (2)
```

1. This is a JavaScript template script. We set `id` to `template` to use it later in our JavaScript code and `type` to `text/x-handlebars-template` to indicate that this is a Handlebars template.
2. This is a JavaScript template script. We load the Handlebars library and then use it to compile the template and render the record.

We can now pass these templates to the `CustomField` class, ensuring that the `advanced_mode` is set to `True`.

```python
import argilla as rg

custom_field = rg.CustomField(
    name="custom",
    template=render_template + script,
    advanced_mode=True
)
```

### Example Gallery

=== "Show text difference"

    ```python
    import argilla as rg
    ```

=== "JSON viewer"

    ```python
    import argilla as rg
    ```
