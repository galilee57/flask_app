from app.blueprints import BLUEPRINT_REGISTRY


def test_blueprint_registry_is_explicit_and_matches_registered_prefixes(app):
    expected = {
        registration.blueprint.name: registration.url_prefix
        for registration in BLUEPRINT_REGISTRY
    }

    assert set(app.blueprints) == set(expected)
    for name, prefix in expected.items():
        rules = [
            rule.rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint.startswith(f"{name}.")
        ]
        assert rules
        assert all(rule.startswith(prefix) for rule in rules)


def test_project_catalogue_is_loaded_once_and_indexed_by_identifier(app):
    cartes = app.config["CARTES"]
    by_id = app.config["PROJECT_CARDS_BY_ID"]

    assert isinstance(cartes, list)
    assert by_id == {str(card["id"]): card for card in cartes}
    assert by_id["todolist"]["id"] == "todolist"


def test_project_context_preserves_resources_and_project_card(app):
    with app.test_request_context("/projects/todolist/"):
        context = {}
        app.update_template_context(context)

    assert context["project_card"]["id"] == "todolist"
    assert context["resources"] == app.config["PROJECT_CARDS_BY_ID"]["todolist"].get(
        "resources", []
    )


def test_non_project_context_only_exposes_empty_resources(app):
    with app.test_request_context("/"):
        context = {}
        app.update_template_context(context)

    assert context["resources"] == []
    assert "project_card" not in context
