# tests/test_apod_downloader.py
import pytest
import requests_mock
import os
from apod_downloader import download_apod_image, APOD_URL, OUTPUT_DIR

# Define a fixture for the API key (mocking the environment variable)
@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv("NASA_API_KEY", "MOCK_API_KEY")
    return os.getenv("NASA_API_KEY")

# Test case for a successful image download
def test_download_apod_image_success(requests_mock, mock_api_key, tmpdir):
    # Mock the API response for a successful image download
    mock_image_data = b"image_content_here"
    requests_mock.get(
        APOD_URL,
        json={
            "media_type": "image",
            "url": "https://example.com/apod.jpg",
            "hdurl": "https://example.com/apod_hd.jpg",
            "title": "A Great APOD",
            "date": "2025-08-13",
        },
        status_code=200,
    )
    requests_mock.get("https://example.com/apod_hd.jpg", content=mock_image_data, status_code=200)

    # Use tmpdir fixture for temporary directory creation
    output_dir = tmpdir.mkdir("test_apod_images")
    download_apod_image(mock_api_key, hd=True, output_dir=output_dir)

    # Verify that the image was downloaded
    expected_filepath = os.path.join(output_dir, "A_Great_APOD_2025-08-13.jpg")
    assert os.path.exists(expected_filepath)
    with open(expected_filepath, "rb") as f:
        assert f.read() == mock_image_data

# Test case for API error handling
def test_download_apod_api_error(requests_mock, mock_api_key, capsys):
    requests_mock.get(APOD_URL, status_code=500)  # Simulate an API error

    download_apod_image(mock_api_key)
    captured = capsys.readouterr()  # Capture print statements

    assert "Error fetching APOD" in captured.out

# Test case for when APOD is a video
def test_download_apod_video(requests_mock, mock_api_key, capsys):
    requests_mock.get(
        APOD_URL,
        json={
            "media_type": "video",
            "url": "https://example.com/apod.mp4",
            "title": "A Video APOD",
            "date": "2025-08-12",
        },
        status_code=200,
    )

    download_apod_image(mock_api_key)
    captured = capsys.readouterr()

    assert "APOD for today is a video." in captured.out
    assert "https://example.com/apod.mp4" in captured.out

# Test case for missing API key
def test_missing_api_key_env_var(capsys):
    # Temporarily remove the environment variable for this test
    old_env_var = os.environ.get("NASA_API_KEY")
    if old_env_var:
        del os.environ["NASA_API_KEY"]

    try:
        # We need to explicitly call the main block of the script for this test
        # as the env var check is in the __name__ == "__main__" block
        # A better approach would be to refactor this logic into a separate function
        # that can be tested independently.
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            from apod_downloader import download_apod_image
            download_apod_image(None)  # Pass None to simulate no API key
        
        captured = capsys.readouterr()
        assert "Error: NASA_API_KEY environment variable not set." in captured.out
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
