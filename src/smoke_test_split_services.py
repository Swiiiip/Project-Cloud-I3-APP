import requests


def main() -> None:
    base_url = "http://localhost:8000"
    session = requests.Session()

    start_response = session.get(f"{base_url}/api/v1/daily/start", timeout=30)
    start_response.raise_for_status()
    print("start:", start_response.status_code)

    status_response = session.get(f"{base_url}/api/v1/daily/get_status", timeout=30)
    status_response.raise_for_status()
    print("status:", status_response.status_code)

    supported_response = session.get(f"{base_url}/api/v1/daily/supported_emojis", timeout=30)
    supported_response.raise_for_status()
    print("supported_emojis:", supported_response.status_code)

    render_response = session.get(f"{base_url}/api/v1/daily/render", timeout=30)
    render_response.raise_for_status()
    print("render:", render_response.status_code, "bytes=", len(render_response.content))


if __name__ == "__main__":
    main()

