from fastapi import APIRouter
from ..util import get_db, custom_logger
from ..app_models.EHR import TestResultInput

db = get_db()

router = APIRouter()

TEST_RESULT_API_KEY = "your_api_key_here"


@router.post(
    "/test_result",
    tags=["Test_Result"],
    summary="Posts a test result",
)
async def post_test_result(input_test_result: TestResultInput):
    custom_logger.info("post_test_result endpoint called")

    if input_test_result.api_key != TEST_RESULT_API_KEY:
        return {
            "success": False,
            "message": "API key is wrong",
        }

    if input_test_result.schema_name:
        schema = db.test_result_schema.find_one(
            filter={"name": input_test_result.schema_name}
        )["schema"]

        # SCHEMA VALIDATION
        is_invalid = False
        for data_entry in input_test_result.test_result.numeric_results:
            data_element = data_entry.data_element
            data_unit = data_entry.data_unit

            if data_element not in schema:
                is_invalid = True

            if schema[data_element] != data_unit:
                is_invalid = True

        if is_invalid or (
            len(input_test_result.test_result.numeric_results) != len(schema)
        ):
            return {
                "success": False,
                "message": "The test result doesn't follow the schema",
            }

    insert_result = db.test_result.insert_one(input_test_result.test_result.dict())

    if insert_result:
        return {
            "success": True,
            "insert_id": str(insert_result.inserted_id),
            "inserted_result": input_test_result.test_result,
            "message": "test_result was inserted successfully",
        }
    else:
        return {
            "success": False,
            "message": "test_result could not be inserted. potential db issue",
        }
