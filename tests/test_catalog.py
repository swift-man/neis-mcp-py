from neis_mcp.api_catalog import API_DEFINITIONS


def test_catalog_contains_all_twelve_neis_apis() -> None:
    assert len(API_DEFINITIONS) == 12
    assert {api.api_res for api in API_DEFINITIONS.values()} == {
        "schoolInfo",
        "mealServiceDietInfo",
        "acaInsTiInfo",
        "hisTimetable",
        "SchoolSchedule",
        "misTimetable",
        "elsTimetable",
        "classInfo",
        "schoolMajorinfo",
        "schulAflcoinfo",
        "spsTimetable",
        "tiClrminfo",
    }


def test_every_api_has_tool_name_and_parameters() -> None:
    for tool_name, api in API_DEFINITIONS.items():
        assert api.tool_name == tool_name
        assert api.title
        assert api.parameters
