# Russell GitLab Indexer

Indexer for a Russell project that crawl a GitLab repositories.

Docker image available as `jagiellonian/russell-gitlab-indexer`

## Docker environment variables

* `RMQ_HOST` - RabbitMQ host
* `RMQ_PORT` - RabbitMQ port (*optional - default 5672*)


* `DB_HOST` - PostgreSQL server host
* `DB_PORT` - PostgreSQL server host (*optional - default 5432*)
* `DB_DATABASE` - Database name
* `DB_USERNAME` - Database username
* `DB_PASSWORD` - Database password


* `GITLAB_PERSONAL_TOKEN` - GitLab personal access token
* `MIN_STARS` - Minimal number of stars that repository should have (*optional*)
* `MIN_FORKS` - Minimal number of forks that repository should have (*optional*)
* `MAX_INACTIVITY_IN_DAYS` - Maximal number of days of inactivity that repository should have to be crawled (*optional*)

When `MIN_STARS`, `MIN_FORKS` or `MAX_INACTIVITY_IN_DAYS` are not passed, then given criteria is not taken into consideration during a crawl.
