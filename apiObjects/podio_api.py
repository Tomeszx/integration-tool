import pandas as pd
import warnings
import re
import retry

from bs4 import MarkupResemblesLocatorWarning
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from multiprocessing import Pool
from apiObjects.google_sheet_api import send_data
from requests import request
from model.podio_item import PartnerFieldsPodio, PdfFile, Comments
from model.podio_tasks import PodioTask
from utilites.config_parser import get_config, get_podio_fields_ids


def get_access_token() -> list:
    tokens = []
    for client_id, client_secret in get_config('podio_tokens'):
        data = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': get_config('credentials', 'username_podio'),
            'password': get_config('credentials', 'password_podio')
        }

        oauth_token_url = get_config('podio_api_urls', 'oauth_token_url')
        response = request('post', oauth_token_url, data=data)
        if response.status_code != 200:
            raise ConnectionRefusedError(response.text)
        tokens.append(response.json()['access_token'])
    return tokens


class Podio:
    def __init__(self, access_tokens: list, credentials: dict):
        self.access_tokens = access_tokens
        self.credentials = credentials
        self.limit = None

    @retry.retry(tries=3)
    def _send_request(self, method: str, endpoint: str, data=None, params=None) -> dict:
        url = f"{get_config('podio_api_urls', 'main_url')}{endpoint}"
        headers = {'Authorization': f'Bearer {self.access_tokens[0]}'}
        response = request(method, url, headers=headers, json=data, params=params)

        self.limit = int(response.headers.get('X-Rate-Limit-Limit'))
        self.remaining = int(response.headers.get('X-Rate-Limit-Remaining'))

        if response.status_code in [200, 410]:
            return response.json()
        elif (self.limit - self.remaining) / self.limit >= 0.80:
            self.access_tokens.pop(0)
        raise ConnectionError(f'The {response.status_code=}\n{response.text=}')

    def _delete_task(self, task_id: str) -> None:
        self._send_request(method='delete', endpoint=f'/task/{task_id}')

    def _search_for_user(self, user_name: str) -> str:
        params = {'query': user_name, 'ref_type': 'profile', 'limit': 2}
        response = self._send_request('get', '/search/v2', params=params)

        for user in response['results']:
            if user_name == user['title']:
                return f"{user['link']}".split('/')[-1]
        return ""

    def _get_tasks(self, responsible_id: str = '6461478') -> list:
        tasks_summary = self._send_request('GET', '/task/total/')['own']
        print(f"{'':^60}", f" Tasks done yesterday -> {tasks_summary['completed_yesterday']}\n")

        with Pool() as pool:
            results = []
            for offset in range(0, tasks_summary['later'], 100):
                params = {'responsible': responsible_id, 'completed': False, 'offset': offset, 'limit': 100}
                result = pool.apply_async(self._send_request, ('GET', '/task/', None, params))
                results.append(result)

            flat_results = []
            for result in results:
                flat_results.extend(result.get())
            return flat_results

    def prepare_tasks(self, tasks_to_do: dict) -> list[PodioTask]:
        taken_tasks = {}
        all_tasks = self._get_tasks()
        for task in all_tasks:
            if not task:
                continue

            full_title = f"{task['ref']['data']['title']} {task['text']}"
            if full_title in taken_tasks:
                print('Deleting task:', full_title)
                self._delete_task(task['task_id'])
            elif task_short_title := PodioTask.check_if_should_be_taken(task, tasks_to_do.keys()):
                taken_tasks[full_title] = PodioTask(task, task_short_title)

        print(f'{"":_^110}\n\n', f"{'':^60}", f"Number of tasks in Podio -> {len(all_tasks)}")
        print(f"{'':^60}", " Tasks for the BOT ->", len(taken_tasks), f"\n{'':_^110}\n\n")
        return list(taken_tasks.values())

    def update_field(self, partner_type: str, partner_id: int, field_name: str, value: str) -> dict:
        field_id = get_podio_fields_ids(partner_type)[field_name]
        return self._send_request('put', f'/item/{partner_id}/value/{field_id}', data={"value": value})

    def get_partner_details(self, item_id: int) -> tuple[PartnerFieldsPodio, Comments, PdfFile]:
        warnings.simplefilter("ignore", MarkupResemblesLocatorWarning)

        response = self._send_request(method='get', endpoint=f'/item/{item_id}')
        fields = PartnerFieldsPodio(response['fields'], response['app']['name'])
        comments = Comments(response['comments'])
        has_pdf = PdfFile(response['files'])

        return fields, comments, has_pdf

    def complete_task(self, task_id: int, complete_action: bool = True) -> dict:
        return self._send_request(method='put', endpoint=f'/task/{task_id}', data={"completed": complete_action})

    def add_comment(self, value: str, task: PodioTask) -> str:
        user = ''
        if task.task_requester:
            user = f'(user:{self._search_for_user(task.task_requester)})'
        msg = f"@[{task.task_requester}]{user}\n\n{value}"

        array = [[task.partner_name, task.short_title, value, task.link_to_shop, datetime.now()]]
        pandas_array = pd.DataFrame(array)
        send_data(col=1, sheet_name="Bot msgs", data=pandas_array)

        return self._send_request(
            'post', f'/comment/item/{task.shop_item_id}/', data={"value": msg}
        )['rich_value']

    def add_error_comment(self, comment: str, task: PodioTask, comments: Comments, comment_frequency: int) -> str:
        comment_without_screen = "\n".join(line for line in comment.split('\n') if not line.startswith('Screenshot'))
        check = re.sub('[^a-zA-Z0-9]', '', comment_without_screen).lower()

        for podio_comment in comments.data[::-1]:
            comm_date = datetime.strptime(podio_comment.created_on.split()[0], "%Y-%m-%d").date()
            com_value = re.sub('[^a-zA-Z0-9]', '', "".join(podio_comment.value.split("\n")[1:])).lower()

            if (datetime.now().date() - comm_date).days > comment_frequency:
                continue
            elif check in com_value:
                return 'Comment not added. (Duplicate).'
            elif SequenceMatcher(None, check, com_value).ratio() > 0.9:
                return 'Comment not added. (Duplicate).'
        return self.add_comment(comment, task).replace("\n\n", "\n")
