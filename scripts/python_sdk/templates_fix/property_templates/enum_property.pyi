{% macro construct(property, source, initial_value="None") %}
{% if property.required %}
{{ property.python_name }} = {{ property.reference.class_name }}({{ source }})
{% else %}
{{ property.python_name }} = {{ initial_value }}
_{{ property.python_name }} = {{ source }}
if _{{ property.python_name }} is not None and not isinstance(_{{ property.python_name }}, Unset):
    {{ property.python_name }} = {{ property.reference.class_name }}(_{{ property.python_name }})
{% endif %}
{% endmacro %}

{% macro transform(property, source, destination, declare_type=True) %}
{% if property.required %}
{% if property.nullable %}
{{ destination }} = {{ source }}.value if {{ source }} else None
{% else %}
{{ destination }} = {{ source }}.value
{% endif %}
{% else %}
{{ destination }}{% if declare_type %}: {{ property.get_type_string() }}{% endif %} = UNSET
if not isinstance({{ source }}, Unset):
{% if property.nullable %}
    {{ destination }} = {{ source }} if {{ source }} else None
{% else %}
    {{ destination }} = {{ source }}
{% endif %}
{% endif %}
{% endmacro %}
