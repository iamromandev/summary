from urllib.parse import urlparse


def get_base_url(url: str) -> str:
    """
    Extracts the base URL from a given URL.

    Parameters:
        url (str): The full URL.

    Returns:
        str: The base URL (scheme + domain).
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"