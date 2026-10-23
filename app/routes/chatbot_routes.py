"""
app/routes/chatbot_routes.py

Chat de atencion basica: recibe el mensaje del usuario y devuelve la
respuesta automatica en JSON. No guarda estado en el servidor; el historial
de la conversacion lo conserva el navegador (ver static/js/chatbot.js).
"""
from flask import Blueprint, jsonify, request

from app.services.chatbot_service import ChatbotService

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")


@chatbot_bp.route("/mensaje", methods=["POST"])
def mensaje():
    """Recibe {"mensaje": "..."} y responde {"ok": true, "respuesta": "...", "intencion": "..."}."""
    datos = request.get_json(silent=True) or {}
    texto = (datos.get("mensaje") or "").strip()
    if not texto:
        return jsonify({"ok": False, "mensaje": "Escribe una pregunta."}), 400

    resultado = ChatbotService.responder(texto)
    return jsonify({"ok": True, **resultado})
