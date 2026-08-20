<<<<<<< HEAD
"""Model loading, preprocessing, and response generation for the Streamlit app."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import tensorflow as tf

from preprocessing import clean_query

LOCAL_MODEL_DIR = Path(__file__).resolve().parent / "model_artifacts"
DEFAULT_MODEL_DIR = (
    LOCAL_MODEL_DIR
    if LOCAL_MODEL_DIR.exists()
    else Path(__file__).resolve().parent.parent / "Assgnment"
)
SUPPORT_TERMS = {
    "account", "billing", "bill", "invoice", "order", "delivery", "refund",
    "return", "payment", "subscription", "cancel", "cancellation", "shipping",
    "internet", "connectivity", "connection", "password", "login", "pin",
    "verification", "charge", "fee", "plan", "service", "purchase", "package",
}


def is_in_scope(text: str) -> bool:
    words = set(clean_query(text).split())
    words = {word.strip("'?$%.,!") for word in words}
    return bool(words & SUPPORT_TERMS)


class ResponseGenerator:
    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR) -> None:
        self.model_dir = Path(model_dir)
        with (self.model_dir / "m2_config.json").open(encoding="utf-8") as file:
            self.config: dict[str, Any] = json.load(file)
        with (self.model_dir / "tokenizer.pkl").open("rb") as file:
            self.tokenizer = pickle.load(file)
        self.index_to_word = {
            int(index): word for word, index in self.tokenizer.word_index.items()
        }
        self.index_to_word.update({0: "<pad>", 1: "<unk>"})
        self.max_query_len = int(self.config.get("max_query_len", 13))
        self.max_response_len = int(self.config.get("max_response_len", 213))
        self.sos_id = int(self.config.get("sos_token_id", 17))
        self.eos_id = int(self.config.get("eos_token_id", 18))
        self.encoder = self._load_first("inference_encoder.keras", "encoder_inf.keras")
        self.decoder = self._load_first("inference_decoder.keras", "decoder_inf.keras")

    def _load_first(self, *names: str) -> tf.keras.Model:
        for name in names:
            path = self.model_dir / name
            if path.exists():
                return tf.keras.models.load_model(path, compile=False)
        raise FileNotFoundError(
            f"Could not find any of {names} in {self.model_dir}"
        )

    def _encode(self, query: str) -> np.ndarray:
        cleaned = clean_query(query)
        ids = self.tokenizer.texts_to_sequences([cleaned])[0]
        ids = ids[: self.max_query_len]
        padded = np.zeros((1, self.max_query_len), dtype="int32")
        padded[0, : len(ids)] = ids
        return padded

    @staticmethod
    def _first_output(prediction: Any) -> np.ndarray:
        if isinstance(prediction, (list, tuple)):
            prediction = prediction[0]
        return np.asarray(prediction)

    def generate(self, query: str) -> str:
        if not query or not query.strip():
            return "Please enter a customer-support question."
        if not is_in_scope(query):
            return (
                "I can help with customer-support questions about orders, refunds, "
                "billing, connectivity, and account access."
            )

        encoder_prediction = self.encoder.predict(self._encode(query), verbose=0)
        if not isinstance(encoder_prediction, (list, tuple)) or len(encoder_prediction) < 2:
            raise RuntimeError("The encoder must return hidden and cell states.")
        hidden_state, cell_state = encoder_prediction[-2:]
        token_id = self.sos_id
        words: list[str] = []

        for _ in range(self.max_response_len):
            decoder_input = np.array([[token_id]], dtype="int32")
            prediction = self.decoder.predict(
                [decoder_input, hidden_state, cell_state], verbose=0
            )
            prediction_array = self._first_output(prediction)
            if prediction_array.ndim == 3:
                prediction_array = prediction_array[:, -1, :]
            token_id = int(np.argmax(prediction_array[0]))
            if token_id == self.eos_id or token_id == 0:
                break
            word = self.index_to_word.get(token_id, "<unk>")
            if word not in {"<sos>", "<pad>"}:
                words.append(word)

        response = " ".join(words).strip()
        return response or "I am unable to draft a response for that question. Please contact support."
=======
"""Model loading, preprocessing, and response generation for the Streamlit app."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import tensorflow as tf

from preprocessing import clean_query

LOCAL_MODEL_DIR = Path(__file__).resolve().parent / "model_artifacts"
DEFAULT_MODEL_DIR = (
    LOCAL_MODEL_DIR
    if LOCAL_MODEL_DIR.exists()
    else Path(__file__).resolve().parent.parent / "Assgnment"
)
SUPPORT_TERMS = {
    "account", "billing", "bill", "invoice", "order", "delivery", "refund",
    "return", "payment", "subscription", "cancel", "cancellation", "shipping",
    "internet", "connectivity", "connection", "password", "login", "pin",
    "verification", "charge", "fee", "plan", "service", "purchase", "package",
}


def is_in_scope(text: str) -> bool:
    words = set(clean_query(text).split())
    words = {word.strip("'?$%.,!") for word in words}
    return bool(words & SUPPORT_TERMS)


class ResponseGenerator:
    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR) -> None:
        self.model_dir = Path(model_dir)
        with (self.model_dir / "m2_config.json").open(encoding="utf-8") as file:
            self.config: dict[str, Any] = json.load(file)
        with (self.model_dir / "tokenizer.pkl").open("rb") as file:
            self.tokenizer = pickle.load(file)
        self.index_to_word = {
            int(index): word for word, index in self.tokenizer.word_index.items()
        }
        self.index_to_word.update({0: "<pad>", 1: "<unk>"})
        self.max_query_len = int(self.config.get("max_query_len", 13))
        self.max_response_len = int(self.config.get("max_response_len", 213))
        self.sos_id = int(self.config.get("sos_token_id", 17))
        self.eos_id = int(self.config.get("eos_token_id", 18))
        self.encoder = self._load_first("inference_encoder.keras", "encoder_inf.keras")
        self.decoder = self._load_first("inference_decoder.keras", "decoder_inf.keras")

    def _load_first(self, *names: str) -> tf.keras.Model:
        for name in names:
            path = self.model_dir / name
            if path.exists():
                return tf.keras.models.load_model(path, compile=False)
        raise FileNotFoundError(
            f"Could not find any of {names} in {self.model_dir}"
        )

    def _encode(self, query: str) -> np.ndarray:
        cleaned = clean_query(query)
        ids = self.tokenizer.texts_to_sequences([cleaned])[0]
        ids = ids[: self.max_query_len]
        padded = np.zeros((1, self.max_query_len), dtype="int32")
        padded[0, : len(ids)] = ids
        return padded

    @staticmethod
    def _first_output(prediction: Any) -> np.ndarray:
        if isinstance(prediction, (list, tuple)):
            prediction = prediction[0]
        return np.asarray(prediction)

    def generate(self, query: str) -> str:
        if not query or not query.strip():
            return "Please enter a customer-support question."
        if not is_in_scope(query):
            return (
                "I can help with customer-support questions about orders, refunds, "
                "billing, connectivity, and account access."
            )

        encoder_prediction = self.encoder.predict(self._encode(query), verbose=0)
        if not isinstance(encoder_prediction, (list, tuple)) or len(encoder_prediction) < 2:
            raise RuntimeError("The encoder must return hidden and cell states.")
        hidden_state, cell_state = encoder_prediction[-2:]
        token_id = self.sos_id
        words: list[str] = []

        for _ in range(self.max_response_len):
            decoder_input = np.array([[token_id]], dtype="int32")
            prediction = self.decoder.predict(
                [decoder_input, hidden_state, cell_state], verbose=0
            )
            prediction_array = self._first_output(prediction)
            if prediction_array.ndim == 3:
                prediction_array = prediction_array[:, -1, :]
            token_id = int(np.argmax(prediction_array[0]))
            if token_id == self.eos_id or token_id == 0:
                break
            word = self.index_to_word.get(token_id, "<unk>")
            if word not in {"<sos>", "<pad>"}:
                words.append(word)

        response = " ".join(words).strip()
        return response or "I am unable to draft a response for that question. Please contact support."
>>>>>>> d2d00eb93c1bfae679456e0d88680c0ac6f2a87b
