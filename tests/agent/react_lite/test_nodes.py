from agent.react_lite.nodes import _parse_react_response


def test_parse_react_response_with_sql_label():
    response = """Thought: Need Track and Genre joined by GenreId.
SQL: SELECT Genre.Name FROM Genre JOIN Track ON Genre.GenreId = Track.GenreId;"""

    thought, query = _parse_react_response(response)

    assert thought == "Need Track and Genre joined by GenreId."
    assert (
        query
        == "SELECT Genre.Name FROM Genre JOIN Track ON Genre.GenreId = Track.GenreId;"
    )


def test_parse_react_response_with_action_sql_label():
    response = """Thought: Previous observation says Album.Name is missing, use Title.
Action SQL: SELECT Title FROM Album;
Observation: should not be part of the SQL"""

    thought, query = _parse_react_response(response)

    assert thought == "Previous observation says Album.Name is missing, use Title."
    assert query == "SELECT Title FROM Album;"
