from great_expectations.data_context import get_context
from great_expectations.checkpoint import Checkpoint

# ✅ Step 1: Load context
context = get_context()

# ✅ Step 2: Add datasource if not exists
existing = [ds["name"] for ds in context.list_datasources()]
if "postgres_db" in existing:
    postgres_ds = context.get_datasource("postgres_db")
else:
    postgres_ds = context.sources.add_postgres(
        name="postgres_db",
        connection_string="postgresql+psycopg2://postgres@localhost:5432/football_db"
    )

# ✅ Step 3: Add query asset if not exists
if "players" not in [asset.name for asset in postgres_ds.assets]:
    postgres_ds.add_query_asset(
        name="players",
        query="SELECT * FROM players"
    )

# ✅ Step 4: Expectation suite
suite_name = "players_suite"
suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)

# ✅ Step 5: Validator
validator = context.get_validator(
    datasource_name="postgres_db",
    data_asset_name="players",
    expectation_suite=suite
)

# ✅ Step 6: Define expectations
validator.expect_column_values_to_be_unique("id")
validator.expect_column_values_to_not_be_null("name")
validator.expect_column_values_to_be_between("age", min_value=15, max_value=45)

# ✅ Step 7: Save suite
validator.save_expectation_suite()

# ✅ Step 8: Run checkpoint (corrected)
checkpoint = Checkpoint(
    name="players_checkpoint",
    data_context=context,
    validations=[{
        "batch_request": validator.active_batch.batch_request,
        "expectation_suite_name": suite_name
    }],
    action_list=[
        {
            "name": "store_validation_result",
            "action": {
                "class_name": "StoreValidationResultAction"
            }
        },
        {
            "name": "store_evaluation_params",
            "action": {
                "class_name": "StoreEvaluationParametersAction"
            }
        },
        {
            "name": "update_data_docs",
            "action": {
                "class_name": "UpdateDataDocsAction"
            }
        }
    ]
)


results = checkpoint.run()

# ✅ Step 9: Show result
print("✅ Validation complete.")
print("📄 Result:", results.list_validation_result_identifiers()[0])
