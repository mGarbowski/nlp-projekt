from agent.common.utils import cleanup_response_with_sql, extract_valid_table_names


def test_cleanup_response_with_sql_keeps_sql_from_first_select():
    query = cleanup_response_with_sql(
        "think The answer needs aggregation.\nSELECT COUNT(*) FROM driver;"
    )

    assert query == "SELECT COUNT(*) FROM driver;"


def test_cleanup_response_with_sql_prefers_query_after_dangling_think_end():
    query = cleanup_response_with_sql(
        "select the Name column from the club table and order it. "
        "</think> SELECT Name FROM club ORDER BY Name ASC;"
    )

    assert query == "SELECT Name FROM club ORDER BY Name ASC;"


def test_cleanup_response_with_sql_removes_visible_think_block():
    query = cleanup_response_with_sql(
        "<think>Use Products and Order_Items.</think> "
        "SELECT AVG(product_price) FROM Products;"
    )

    assert query == "SELECT AVG(product_price) FROM Products;"


def test_cleanup_response_with_sql_uses_final_sql_marker():
    query = cleanup_response_with_sql(
        "select Type from book where Chapters > 75. For the second part, use another query. "
        "The SQL would be: SELECT Type FROM book WHERE Chapters > 75 "
        "INTERSECT SELECT Type FROM book WHERE Chapters < 50;"
    )

    assert query == (
        "SELECT Type FROM book WHERE Chapters > 75 "
        "INTERSECT SELECT Type FROM book WHERE Chapters < 50;"
    )


def test_cleanup_response_with_sql_normalizes_table_aliases_and_backticks():
    query = cleanup_response_with_sql(
        "```sql\nSELECT c.`customer_id` FROM Customers c JOIN Orders o ON c.customer_id = o.customer_id;\n```"
    )

    assert query == (
        "SELECT c.customer_id FROM Customers AS c JOIN Orders AS o "
        "ON c.customer_id = o.customer_id;"
    )


def test_cleanup_response_with_sql_removes_output_aliases():
    query = cleanup_response_with_sql(
        "SELECT AVG(product_price) AS average_price FROM Products;"
    )

    assert query == "SELECT AVG(product_price) FROM Products;"


def test_cleanup_response_with_sql_removes_backtick_alias_with_spaces():
    query = cleanup_response_with_sql(
        "SELECT t1.`Type_of_powertrain` AS `Powertrain Type`, "
        "AVG(t2.Annual_fuel_cost) AS Average_Annual_Fuel_Cost "
        "FROM Vehicles t1 JOIN Renting_history t2 ON t1.id = t2.vehicles_id;"
    )

    assert query == (
        "SELECT t1.Type_of_powertrain, AVG(t2.Annual_fuel_cost) "
        "FROM Vehicles AS t1 JOIN Renting_history AS t2 "
        "ON t1.id = t2.vehicles_id;"
    )


def test_cleanup_response_with_sql_rewrites_order_by_output_alias():
    query = cleanup_response_with_sql(
        "SELECT COUNT(*) AS cnt FROM driver GROUP BY Engine ORDER BY cnt DESC LIMIT 1;"
    )

    assert query == (
        "SELECT COUNT(*) FROM driver GROUP BY Engine "
        "ORDER BY COUNT(*) DESC LIMIT 1;"
    )


def test_cleanup_response_with_sql_rewrites_having_output_alias():
    query = cleanup_response_with_sql(
        "SELECT Engine, COUNT(*) AS cnt FROM driver GROUP BY Engine HAVING cnt > 2;"
    )

    assert query == (
        "SELECT Engine, COUNT(*) FROM driver GROUP BY Engine HAVING COUNT(*) > 2;"
    )


def test_extract_valid_table_names_prefers_relevant_table_answer():
    selected = extract_valid_table_names(
        "Reasoning omitted.\nRelevant tables: Employee, Has_Clearance",
        ["Employee", "Planet", "Has_Clearance"],
    )

    assert selected == ["Employee", "Has_Clearance"]
