from typing import Optional
import requests
import datetime

from fregeindexerlib import Indexer, CrawlResult, RabbitMQConnectionParameters, IndexerType, \
    DatabaseConnectionParameters, IndexerError

from gitlab_indexer_parameters import GitLabIndexerParameters


class GitLabIndexer(Indexer):
    BASE_API_URL = 'https://gitlab.com/api/v4/projects'

    def __init__(self, indexer_type: IndexerType, rabbitmq_parameters: RabbitMQConnectionParameters,
                 database_parameters: DatabaseConnectionParameters, rejected_publish_delay: int,
                 gitlab_indexer_parameters: GitLabIndexerParameters):
        super().__init__(indexer_type, rabbitmq_parameters, database_parameters, rejected_publish_delay)
        self.gitlab_indexer_parameters = gitlab_indexer_parameters

    def crawl_next_repository(self, prev_repository_id: Optional[str]) -> Optional[CrawlResult]:
        token = self.gitlab_indexer_parameters.gitlab_personal_token
        min_stars = self.gitlab_indexer_parameters.min_stars
        min_forks = self.gitlab_indexer_parameters.min_forks
        max_inactivity = self.gitlab_indexer_parameters.max_inactivity_in_days
        get_parameters = {
            'private_token': token,
            'pagination': 'keyset',
            'order_by': 'id',
            'sort': 'asc',
            'per_page': 1,
            'id_after': 0 if prev_repository_id is None else int(prev_repository_id)
        }
        while True:
            self.log.debug('Start a new crawl')
            self.log.debug(f'Last crawl id: ' + str(prev_repository_id))
            self.log.debug(f"Last tested id: {get_parameters['id_after']}")

            response = requests.get(self.BASE_API_URL, params=get_parameters, timeout=3)
            if response.status_code != 200:
                raise IndexerError('Response code other than 200!', 'Response: ' + response.text)

            json_response = response.json()
            if len(json_response) < 1:
                return None

            repository_id = json_response[0]['id']
            web_url = json_response[0]['web_url']
            self.log.info(f'Tested repository id: {repository_id} ({web_url})')

            visibility = json_response[0]['visibility']
            self.log.debug(f'Tested repository visibility: {visibility}')

            if visibility != 'public':
                self.log.info('Repository rejected due to visibility other than public')
                get_parameters['id_after'] = repository_id
                continue

            stars = json_response[0]['star_count']
            self.log.debug(f'Tested repository stars: {stars}')

            if min_stars is not None and int(stars) < min_stars:
                self.log.info('Repository rejected due to too small number of stars')
                get_parameters['id_after'] = repository_id
                continue

            forks = json_response[0]['forks_count']
            self.log.debug(f'Tested repository forks: {forks}')

            if min_forks is not None and int(forks) < min_forks:
                self.log.info('Repository rejected due to too small number of forks')
                get_parameters['id_after'] = repository_id
                continue

            last_activity = json_response[0]['last_activity_at']
            inactivity_days = (datetime.datetime.now() -
                               datetime.datetime.strptime(last_activity, "%Y-%m-%dT%H:%M:%S.%fZ")).days
            self.log.debug(f'Tested repository last activity: {last_activity} (inactivity in days: {inactivity_days})')

            if max_inactivity is not None and inactivity_days > max_inactivity:
                self.log.info('Repository rejected due to too many days of inactivity')
                get_parameters['id_after'] = repository_id
                continue

            # languages are not get from API, because it returns only top 5 languages
            crawled_repository = CrawlResult(
                id=str(repository_id),
                repo_url=web_url,
                git_url=json_response[0]['http_url_to_repo'],
                languages=None
                )

            self.log.info(f'Repository accepted: {crawled_repository}')

            return crawled_repository
