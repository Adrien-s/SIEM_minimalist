from app.data.event_service import list_event_definitions, get_event_definition

def test_list_and_get_defs(db_conn):
    defs = list_event_definitions(db_conn)
    assert isinstance(defs, list)
    # prend le premier
    first = defs[0]
    got = get_event_definition(db_conn, first['event_id'])
    assert got['name'] == first['name']
    assert got['description'] == first['description']
