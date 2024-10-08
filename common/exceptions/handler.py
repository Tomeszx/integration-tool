import traceback

from io import BytesIO
from venv import logger
from result import Err
from apiObjects.google_sheet_api import upload_file


def extract_exception_text(e: Exception) -> str:
    return f'{e.__class__}: {str(e)}'.split('Stacktrace')[0]


def handle_exception(screen: BytesIO, e: Exception) -> Err:
    logger.debug(traceback.format_exc())
    print(traceback.format_exc())

    error_str = extract_exception_text(e)
    screen_url = upload_file(screen)
    return Err(f'There is an issue.\nScreenshot: {screen_url}\nMessage: {error_str}')
