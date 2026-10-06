{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- if target.name == 'prod' and custom_schema_name is not none -%}

        {# If no custom schema is specified, fall back to the profiles.yml target schema #}
        {{ custom_schema_name | trim }}

    {%- else -%}

        {# If a custom schema is specified in dbt_project.yml or config(), use ONLY that #}
        {%- if target.name == 'dev' and custom_schema_name is none -%}
            {{ target.schema }}
        {%- else -%}
            {{ custom_schema_name | trim }}
        {%- endif -%}

    {%- endif -%}

{%- endmacro %}
