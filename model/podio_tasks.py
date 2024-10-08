

class PodioTask:
    def __init__(self, task: dict, part_title: str):
        self.short_title = part_title
        self.task_id = task['task_id']
        self.task_text = task['text']
        self.shop_item_id = task['ref']['data']['item_id']
        self.partner_name = task['ref']['data']['title']
        self.partner_type = task['ref']['data']['app']['config']['name'].lower()
        self.link_to_shop = task['ref']['data']['link']
        self.task_requester = task['description']

    @classmethod
    def check_if_should_be_taken(self, current_task: dict, tasks_to_do: dict.keys) -> str | None:
        for task_short_title in tasks_to_do:
            if task_short_title in current_task['text']:
                return task_short_title
        return None