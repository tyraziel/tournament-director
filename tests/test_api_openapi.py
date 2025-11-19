"""
OpenAPI schema validation tests.

Validates that the generated OpenAPI specification is complete and valid.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import pytest
from src.api.main import app


class TestOpenAPISchema:
    """Test OpenAPI schema generation and validation."""

    def test_openapi_schema_exists(self):
        """Test that OpenAPI schema can be generated."""
        schema = app.openapi()
        assert schema is not None

    def test_openapi_version(self):
        """Test that OpenAPI version is 3.x."""
        schema = app.openapi()
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.")

    def test_info_section(self):
        """Test that info section contains required fields."""
        schema = app.openapi()
        assert "info" in schema

        info = schema["info"]
        assert "title" in info
        assert info["title"] == "Tournament Director API"
        assert "version" in info
        assert info["version"] == "0.1.0"
        assert "description" in info
        assert len(info["description"]) > 0

    def test_contact_information(self):
        """Test that contact information is present."""
        schema = app.openapi()
        info = schema["info"]

        assert "contact" in info
        assert "name" in info["contact"]
        assert "email" in info["contact"]

    def test_license_information(self):
        """Test that license information is present."""
        schema = app.openapi()
        info = schema["info"]

        assert "license" in info
        assert "name" in info["license"]
        assert "MIT" in info["license"]["name"]

    def test_paths_exist(self):
        """Test that paths section exists and has endpoints."""
        schema = app.openapi()
        assert "paths" in schema

        paths = schema["paths"]
        assert len(paths) > 0

    def test_health_endpoints(self):
        """Test that health check endpoints are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        assert "/health" in paths
        assert "get" in paths["/health"]

        assert "/health/detailed" in paths
        assert "get" in paths["/health/detailed"]

    def test_player_endpoints(self):
        """Test that all player endpoints are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # List and create
        assert "/players/" in paths
        assert "get" in paths["/players/"]
        assert "post" in paths["/players/"]

        # Get, update, delete by ID
        assert "/players/{player_id}" in paths
        assert "get" in paths["/players/{player_id}"]
        assert "put" in paths["/players/{player_id}"]
        assert "delete" in paths["/players/{player_id}"]

        # Search endpoints
        assert "/players/search/by-name" in paths
        assert "/players/discord/{discord_id}" in paths

    def test_venue_endpoints(self):
        """Test that all venue endpoints are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # List and create
        assert "/venues/" in paths
        assert "get" in paths["/venues/"]
        assert "post" in paths["/venues/"]

        # Get, update, delete by ID
        assert "/venues/{venue_id}" in paths
        assert "get" in paths["/venues/{venue_id}"]
        assert "put" in paths["/venues/{venue_id}"]
        assert "delete" in paths["/venues/{venue_id}"]

    def test_format_endpoints(self):
        """Test that all format endpoints are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # List and create
        assert "/formats/" in paths
        assert "get" in paths["/formats/"]
        assert "post" in paths["/formats/"]

        # Get, update, delete by ID
        assert "/formats/{format_id}" in paths
        assert "get" in paths["/formats/{format_id}"]
        assert "put" in paths["/formats/{format_id}"]
        assert "delete" in paths["/formats/{format_id}"]

        # Filter by game system
        assert "/formats/game/{game_system}" in paths

    def test_schemas_section(self):
        """Test that schemas/components section contains models."""
        schema = app.openapi()

        # OpenAPI 3.x uses "components" instead of "definitions"
        assert "components" in schema
        assert "schemas" in schema["components"]

        schemas = schema["components"]["schemas"]

        # Check for key models
        assert "Player" in schemas
        assert "PlayerCreate" in schemas
        assert "PlayerUpdate" in schemas
        assert "Venue" in schemas
        assert "VenueCreate" in schemas
        assert "VenueUpdate" in schemas
        assert "Format" in schemas
        assert "FormatCreate" in schemas
        assert "FormatUpdate" in schemas

    def test_tags_section(self):
        """Test that tags are defined for organization."""
        schema = app.openapi()
        paths = schema["paths"]

        # Collect all tags used
        tags_used = set()
        for path_data in paths.values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "tags" in method_data:
                    tags_used.update(method_data["tags"])

        # Verify expected tags
        assert "Health" in tags_used
        assert "Players" in tags_used
        assert "Venues" in tags_used
        assert "Formats" in tags_used

    def test_response_models(self):
        """Test that endpoints have response models defined."""
        schema = app.openapi()
        paths = schema["paths"]

        # Test player creation endpoint
        player_post = paths["/players/"]["post"]
        assert "responses" in player_post
        assert "201" in player_post["responses"]

        # Test health check endpoint
        health_get = paths["/health"]["get"]
        assert "responses" in health_get
        assert "200" in health_get["responses"]

    def test_request_bodies(self):
        """Test that POST/PUT endpoints have request bodies."""
        schema = app.openapi()
        paths = schema["paths"]

        # Player creation should have request body
        player_post = paths["/players/"]["post"]
        assert "requestBody" in player_post
        assert "content" in player_post["requestBody"]

        # Player update should have request body
        player_put = paths["/players/{player_id}"]["put"]
        assert "requestBody" in player_put

    def test_parameter_definitions(self):
        """Test that path parameters are properly defined."""
        schema = app.openapi()
        paths = schema["paths"]

        # Player ID parameter
        player_get = paths["/players/{player_id}"]["get"]
        assert "parameters" in player_get

        params = player_get["parameters"]
        player_id_param = next((p for p in params if p["name"] == "player_id"), None)
        assert player_id_param is not None
        assert player_id_param["in"] == "path"
        assert player_id_param["required"] is True

    def test_pagination_parameters(self):
        """Test that pagination parameters are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # List players should have pagination
        players_get = paths["/players/"]["get"]
        assert "parameters" in players_get

        param_names = [p["name"] for p in players_get["parameters"]]
        assert "limit" in param_names
        assert "offset" in param_names

    def test_operation_summaries(self):
        """Test that all operations have summaries."""
        schema = app.openapi()
        paths = schema["paths"]

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    assert "summary" in operation, f"{method.upper()} {path} missing summary"
                    assert len(operation["summary"]) > 0

    def test_operation_descriptions(self):
        """Test that all operations have descriptions."""
        schema = app.openapi()
        paths = schema["paths"]

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    assert "description" in operation, f"{method.upper()} {path} missing description"
                    assert len(operation["description"]) > 0

    def test_http_status_codes(self):
        """Test that appropriate HTTP status codes are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # POST should return 201
        player_post = paths["/players/"]["post"]
        assert "201" in player_post["responses"]

        # GET should return 200
        players_get = paths["/players/"]["get"]
        assert "200" in players_get["responses"]

        # DELETE should return 204
        player_delete = paths["/players/{player_id}"]["delete"]
        assert "204" in player_delete["responses"]

    def test_model_properties(self):
        """Test that models have required properties defined."""
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        # Player model
        player = schemas["Player"]
        assert "properties" in player
        assert "id" in player["properties"]
        assert "name" in player["properties"]

        # PlayerCreate model
        player_create = schemas["PlayerCreate"]
        assert "properties" in player_create
        assert "name" in player_create["properties"]

    def test_enum_definitions(self):
        """Test that enums are properly defined in schemas."""
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        # GameSystem should be an enum
        assert "GameSystem" in schemas
        game_system = schemas["GameSystem"]
        assert "enum" in game_system

        # BaseFormat should be an enum
        assert "BaseFormat" in schemas
        base_format = schemas["BaseFormat"]
        assert "enum" in base_format

    def test_openapi_json_endpoint(self):
        """Test that /openapi.json endpoint is configured."""
        # FastAPI automatically creates this endpoint
        # Verify it's accessible in the app configuration
        assert app.openapi_url == "/openapi.json"

    def test_docs_endpoint(self):
        """Test that /docs endpoint is configured."""
        assert app.docs_url == "/docs"

    def test_redoc_endpoint(self):
        """Test that /redoc endpoint is configured."""
        assert app.redoc_url == "/redoc"

    def test_tournament_endpoints(self):
        """Test that all tournament endpoints are documented."""
        schema = app.openapi()
        paths = schema["paths"]

        # List and create
        assert "/tournaments/" in paths
        assert "get" in paths["/tournaments/"]
        assert "post" in paths["/tournaments/"]

        # Get, update, delete by ID
        assert "/tournaments/{tournament_id}" in paths
        assert "get" in paths["/tournaments/{tournament_id}"]
        assert "put" in paths["/tournaments/{tournament_id}"]
        assert "delete" in paths["/tournaments/{tournament_id}"]

        # Filter endpoints
        assert "/tournaments/status/{status}" in paths
        assert "/tournaments/venue/{venue_id}" in paths
        assert "/tournaments/format/{format_id}" in paths

        # Lifecycle endpoints
        assert "/tournaments/{tournament_id}/start" in paths
        assert "post" in paths["/tournaments/{tournament_id}/start"]

        assert "/tournaments/{tournament_id}/complete" in paths
        assert "post" in paths["/tournaments/{tournament_id}/complete"]

    def test_tournament_models(self):
        """Test that tournament models are in the schema."""
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        # Tournament models
        assert "Tournament" in schemas
        assert "TournamentCreate" in schemas
        assert "TournamentUpdate" in schemas
        assert "RegistrationControl" in schemas

        # Verify Tournament model properties
        tournament = schemas["Tournament"]
        assert "properties" in tournament
        assert "id" in tournament["properties"]
        assert "name" in tournament["properties"]
        assert "status" in tournament["properties"]
        assert "registration" in tournament["properties"]

        # Verify TournamentCreate model
        tournament_create = schemas["TournamentCreate"]
        assert "properties" in tournament_create
        assert "name" in tournament_create["properties"]
        assert "format_id" in tournament_create["properties"]
        assert "venue_id" in tournament_create["properties"]

    def test_tournament_status_enum(self):
        """Test that TournamentStatus enum is properly defined."""
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        assert "TournamentStatus" in schemas
        tournament_status = schemas["TournamentStatus"]
        assert "enum" in tournament_status

        # Check for expected status values
        status_values = tournament_status["enum"]
        assert "draft" in status_values
        assert "in_progress" in status_values
        assert "completed" in status_values

    def test_registration_endpoints(self):
        """Test that registration endpoints are documented.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        paths = schema["paths"]

        # POST /tournaments/{tournament_id}/register
        assert "/tournaments/{tournament_id}/register" in paths
        register_path = paths["/tournaments/{tournament_id}/register"]
        assert "post" in register_path
        assert register_path["post"]["tags"] == ["Registrations"]

        # GET /tournaments/{tournament_id}/registrations
        assert "/tournaments/{tournament_id}/registrations" in paths
        list_path = paths["/tournaments/{tournament_id}/registrations"]
        assert "get" in list_path
        assert list_path["get"]["tags"] == ["Registrations"]

        # DELETE /tournaments/{tournament_id}/registrations/{player_id}
        assert "/tournaments/{tournament_id}/registrations/{player_id}" in paths
        drop_path = paths["/tournaments/{tournament_id}/registrations/{player_id}"]
        assert "delete" in drop_path
        assert drop_path["delete"]["tags"] == ["Registrations"]

    def test_registration_models(self):
        """Test that registration models are defined in schema.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        # PlayerRegistrationCreate model
        assert "PlayerRegistrationCreate" in schemas
        reg_create = schemas["PlayerRegistrationCreate"]
        assert "properties" in reg_create
        assert "player_id" in reg_create["properties"]
        assert "password" in reg_create["properties"]  # Optional
        assert "notes" in reg_create["properties"]  # Optional

        # TournamentRegistration model (response)
        assert "TournamentRegistration" in schemas
        registration = schemas["TournamentRegistration"]
        assert "properties" in registration
        assert "id" in registration["properties"]
        assert "tournament_id" in registration["properties"]
        assert "player_id" in registration["properties"]
        assert "sequence_id" in registration["properties"]
        assert "status" in registration["properties"]
        assert "registration_time" in registration["properties"]

    def test_registration_response_codes(self):
        """Test that registration endpoints document proper response codes.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        paths = schema["paths"]

        # POST /tournaments/{tournament_id}/register - 201, 404, 409, 403, 400
        register = paths["/tournaments/{tournament_id}/register"]["post"]
        assert "responses" in register
        assert "201" in register["responses"]  # Created
        assert "422" in register["responses"]  # Validation error

        # GET /tournaments/{tournament_id}/registrations - 200, 404
        list_registrations = paths["/tournaments/{tournament_id}/registrations"]["get"]
        assert "responses" in list_registrations
        assert "200" in list_registrations["responses"]
        assert "422" in list_registrations["responses"]

        # DELETE /tournaments/{tournament_id}/registrations/{player_id} - 204, 404
        drop = paths["/tournaments/{tournament_id}/registrations/{player_id}"]["delete"]
        assert "responses" in drop
        assert "204" in drop["responses"]  # No content
        assert "422" in drop["responses"]

    def test_rounds_endpoints(self):
        """Test that rounds and pairings endpoints are documented.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        paths = schema["paths"]

        # POST /tournaments/{tournament_id}/rounds/{round_number}/pair
        assert "/tournaments/{tournament_id}/rounds/{round_number}/pair" in paths
        pair_path = paths["/tournaments/{tournament_id}/rounds/{round_number}/pair"]
        assert "post" in pair_path
        assert pair_path["post"]["tags"] == ["Rounds"]

        # GET /tournaments/{tournament_id}/rounds/{round_number}
        assert "/tournaments/{tournament_id}/rounds/{round_number}" in paths
        get_round_path = paths["/tournaments/{tournament_id}/rounds/{round_number}"]
        assert "get" in get_round_path
        assert get_round_path["get"]["tags"] == ["Rounds"]

        # POST /tournaments/{tournament_id}/rounds/{round_number}/complete
        assert "/tournaments/{tournament_id}/rounds/{round_number}/complete" in paths
        complete_path = paths["/tournaments/{tournament_id}/rounds/{round_number}/complete"]
        assert "post" in complete_path
        assert complete_path["post"]["tags"] == ["Rounds"]

        # GET /tournaments/{tournament_id}/standings
        assert "/tournaments/{tournament_id}/standings" in paths
        standings_path = paths["/tournaments/{tournament_id}/standings"]
        assert "get" in standings_path
        assert standings_path["get"]["tags"] == ["Rounds"]

    def test_matches_endpoints(self):
        """Test that match management endpoints are documented.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        paths = schema["paths"]

        # GET /tournaments/{tournament_id}/matches
        assert "/tournaments/{tournament_id}/matches" in paths
        list_matches_path = paths["/tournaments/{tournament_id}/matches"]
        assert "get" in list_matches_path
        assert list_matches_path["get"]["tags"] == ["Matches"]

        # GET /matches/{match_id}
        assert "/matches/{match_id}" in paths
        get_match_path = paths["/matches/{match_id}"]
        assert "get" in get_match_path
        assert get_match_path["get"]["tags"] == ["Matches"]

        # PUT /matches/{match_id}/result
        assert "/matches/{match_id}/result" in paths
        submit_result_path = paths["/matches/{match_id}/result"]
        assert "put" in submit_result_path
        assert submit_result_path["put"]["tags"] == ["Matches"]

    def test_rounds_and_matches_models(self):
        """Test that rounds and matches models are defined in schema.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        schemas = schema["components"]["schemas"]

        # Round model
        assert "Round" in schemas
        round_model = schemas["Round"]
        assert "properties" in round_model
        assert "id" in round_model["properties"]
        assert "tournament_id" in round_model["properties"]
        assert "round_number" in round_model["properties"]
        assert "status" in round_model["properties"]

        # Match model
        assert "Match" in schemas
        match_model = schemas["Match"]
        assert "properties" in match_model
        assert "id" in match_model["properties"]
        assert "tournament_id" in match_model["properties"]
        assert "round_id" in match_model["properties"]
        assert "player1_id" in match_model["properties"]
        assert "player2_id" in match_model["properties"]
        assert "player1_wins" in match_model["properties"]
        assert "player2_wins" in match_model["properties"]

        # MatchResultSubmit model (request body for submitting results)
        assert "MatchResultSubmit" in schemas
        result_model = schemas["MatchResultSubmit"]
        assert "properties" in result_model
        assert "winner_id" in result_model["properties"]
        assert "player1_wins" in result_model["properties"]
        assert "player2_wins" in result_model["properties"]
        assert "draws" in result_model["properties"]

        # StandingsEntry model (response for standings)
        assert "StandingsEntry" in schemas
        standings_model = schemas["StandingsEntry"]
        assert "properties" in standings_model
        assert "rank" in standings_model["properties"]
        assert "player_id" in standings_model["properties"]
        assert "player_name" in standings_model["properties"]
        assert "match_points" in standings_model["properties"]
        assert "match_win_percentage" in standings_model["properties"]
        assert "opponent_match_win_percentage" in standings_model["properties"]

    def test_rounds_and_matches_response_codes(self):
        """Test that rounds/matches endpoints document proper response codes.

        AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        """
        schema = app.openapi()
        paths = schema["paths"]

        # POST /tournaments/{tournament_id}/rounds/{round_number}/pair - 201, 404, 400, 409
        pair = paths["/tournaments/{tournament_id}/rounds/{round_number}/pair"]["post"]
        assert "responses" in pair
        assert "201" in pair["responses"]  # Created
        assert "422" in pair["responses"]  # Validation error

        # GET /tournaments/{tournament_id}/rounds/{round_number} - 200, 404
        get_round = paths["/tournaments/{tournament_id}/rounds/{round_number}"]["get"]
        assert "responses" in get_round
        assert "200" in get_round["responses"]
        assert "422" in get_round["responses"]

        # POST /tournaments/{tournament_id}/rounds/{round_number}/complete - 200, 404, 400
        complete_round = paths["/tournaments/{tournament_id}/rounds/{round_number}/complete"]["post"]
        assert "responses" in complete_round
        assert "200" in complete_round["responses"]
        assert "422" in complete_round["responses"]

        # GET /tournaments/{tournament_id}/standings - 200, 404
        standings = paths["/tournaments/{tournament_id}/standings"]["get"]
        assert "responses" in standings
        assert "200" in standings["responses"]
        assert "422" in standings["responses"]

        # GET /tournaments/{tournament_id}/matches - 200, 404
        list_matches = paths["/tournaments/{tournament_id}/matches"]["get"]
        assert "responses" in list_matches
        assert "200" in list_matches["responses"]
        assert "422" in list_matches["responses"]

        # GET /matches/{match_id} - 200, 404
        get_match = paths["/matches/{match_id}"]["get"]
        assert "responses" in get_match
        assert "200" in get_match["responses"]
        assert "422" in get_match["responses"]

        # PUT /matches/{match_id}/result - 200, 404, 400
        submit_result = paths["/matches/{match_id}/result"]["put"]
        assert "responses" in submit_result
        assert "200" in submit_result["responses"]
        assert "422" in submit_result["responses"]
