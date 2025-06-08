from app.config import settings

def test_model_path_exists():
    assert hasattr(settings, 'MODEL_PATH')
    assert isinstance(settings.MODEL_PATH, str)