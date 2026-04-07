from flask import request, jsonify

from src.api.routes.game_controller import GameController


class GameRoutes:
    def __init__(self):
        self.controller = GameController()

    def get_supported_emojis(self):
        emojis_codes = self.controller.get_supported_emojis()
        return emojis_codes.to_json_dict()

    def create_daily_challenge(self):
        game_id = request.json.get("game_id", "default")
        result = self.controller.create_daily_challenge(game_id)
        return result.to_json_dict()

    def create_endless_game(self):
        game_id = request.json.get("game_id", "default")
        result = self.controller.create_endless_game(game_id)
        return result.to_json_dict()

    def make_guess(self):
        data = request.json
        game_id = data.get("game_id")
        guess = data.get("guess")
        if not game_id or not guess:
            return jsonify({"error": "Missing game_id or guess"}), 400
        result = self.controller.make_guess(game_id, guess)
        return result.to_json_dict()

    def get_game_status(self, game_id):
        result = self.controller.get_game_status(game_id)
        return result.to_json_dict()

    def end_game(self):
        game_id = request.json.get("game_id")
        if not game_id:
            return jsonify({"error": "Missing game_id"}), 400
        result = self.controller.end_game(game_id)
        return result.to_json_dict()
