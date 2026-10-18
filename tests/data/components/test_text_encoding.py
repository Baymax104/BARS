import numpy as np
import pytest

from src.data.components.preprocessing import convert_to_dense_numpy_array, squeeze_tensor_in_place
from src.data.components.text_encoding import decode_utf8_features


@pytest.mark.parametrize("text", ["ASCII text", "Café © – 中文 🎮", ""])
def test_prepared_text_preserves_utf8_and_item_identity(text):
    ids = np.array([0], dtype=np.int64)
    row = convert_to_dense_numpy_array({"id": ids, "text": [text.encode("utf-8")]})
    row = squeeze_tensor_in_place(row, features_to_apply=["text"])
    decoded = decode_utf8_features(row, features_to_apply=["text"])
    assert decoded["text"].shape == (1,)
    assert decoded["text"].item() == text
    assert decoded["id"] is ids


@pytest.mark.parametrize("shape", [(2,), (1, 2)])
def test_decode_preserves_array_shape(shape):
    values = np.array(["中文".encode(), "Café".encode()]).reshape(shape)
    decoded = decode_utf8_features({"text": values})["text"]
    assert decoded.shape == shape
    assert decoded.reshape(-1).tolist() == ["中文", "Café"]


def test_decode_accepts_existing_unicode_and_empty_arrays():
    row = decode_utf8_features({"unicode": np.array("中文"), "empty": np.array([], dtype="S")})
    assert row["unicode"].item() == "中文"
    assert row["empty"].shape == (0,)


def test_invalid_encoding_and_nontext_fail_without_lossy_replacement():
    with pytest.raises(UnicodeDecodeError):
        decode_utf8_features({"text": np.array([b"\xff"])})
    with pytest.raises(TypeError, match="Expected text"):
        decode_utf8_features({"text": np.array([123])})
