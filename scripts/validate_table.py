import sys
from great_expectations.data_context import get_context
from great_expectations.checkpoint import Checkpoint

# ✅ Usage: python scripts/validate_table.py players
if len(sys.argv) != 2:
    print("❌ Usage: python scripts/validate_table.py <table_name>")
    sys.exit(1)

table_name = sys.argv[1]
print(f"🔍 Validating table: {table_name}")

# ✅ Step 1: Load context
context = get_context()

# ✅ Step 2: Ensure datasource is registered
datasource_name = "postgres_db"
datasource_names = [ds["name"] for ds in context.list_datasources()]
if datasource_name not in datasource_names:
    datasource = context.sources.add_postgres(
        name=datasource_name,
        connection_string="postgresql+psycopg2://postgres@localhost:5432/football_db"
    )
else:
    datasource = context.get_datasource(datasource_name)

# ✅ Step 3: Add the asset only if it doesn't already exist
if table_name not in [asset.name for asset in datasource.assets]:
    datasource.add_query_asset(name=table_name, query=f"SELECT * FROM {table_name}")


# ✅ Step 4: Build batch request and load suite
asset = datasource.get_asset(table_name)
batch_request = asset.build_batch_request()
suite_name = f"{table_name}_suite"
suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)

# ✅ Step 5: Get validator and define expectations
validator = context.get_validator(batch_request=batch_request, expectation_suite=suite)

validator.expect_column_values_to_be_unique("id")
validator.expect_column_values_to_not_be_null("id")

if table_name == "players":
    validator.expect_column_values_to_not_be_null("name")
    validator.expect_column_values_to_be_between("age", min_value=15, max_value=45)
    validator.expect_column_values_to_be_between("rating", min_value=0.0, max_value=10.0)

validator.save_expectation_suite()

# ✅ Step 6: Run checkpoint
checkpoint = Checkpoint(
    name=f"{table_name}_checkpoint",
    data_context=context,
    validations=[
        {
            "batch_request": batch_request,
            "expectation_suite_name": suite_name
        }
    ],
    action_list=[
        {"name": "store_validation_result", "action": {"class_name": "StoreValidationResultAction"}},
        {"name": "store_evaluation_params", "action": {"class_name": "StoreEvaluationParametersAction"}},
        {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
    ]
)

results = checkpoint.run()

print("✅ Validation complete.")
print("📄 Run `great_expectations docs build` to view the results.")
