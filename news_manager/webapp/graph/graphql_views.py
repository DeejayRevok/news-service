"""
GraphQL views module
"""
import asyncio

from aiohttp.web_app import Application
from aiohttp_graphql import GraphQLView
from graphene import Schema
from graphql.error import GraphQLLocatedError
from graphql.execution.executors.asyncio import AsyncioExecutor

from news_manager.log_config import get_logger
from news_manager.webapp.graph.queries import Query

LOGGER = get_logger()
schema = Schema(query=Query)

GRAPHIQL_JWT_TEMPLATE = """<!--
The request to this GraphQL server provided the header "Accept: text/html"
and as a result has been presented GraphiQL - an in-browser IDE for
exploring GraphQL.
If you wish to receive JSON, provide the header "Accept: application/json" or
add "&raw" to the end of the URL within a browser.
-->
<!DOCTYPE html>
<html>
<head>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      width: 100%;
    }
    #graphiql {
      height: 100vh;
    }
    .jwt-token {
      background: linear-gradient(#f7f7f7, #e2e2e2);
      border-bottom: 1px solid #d0d0d0;
      font-family: system, -apple-system, 'San Francisco', '.SFNSDisplay-Regular', 'Segoe UI', Segoe, 'Segoe WP', 'Helvetica Neue', helvetica, 'Lucida Grande', arial, sans-serif;
      padding: 7px 14px 6px;
      font-size: 14px;
    }
  </style>
  <meta name="referrer" content="no-referrer">
  <title>GraphiQL UI</title>
  <link rel="icon" href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.8/build/favicon.png" />
  <link href="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.css" rel="stylesheet" />
  <script src="//cdn.jsdelivr.net/gh/github/fetch@3.0.0/fetch.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react@16.12.0/umd/react.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react-dom@16.12.0/umd/react-dom.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/subscriptions-transport-ws@0.9.16/browser/client.js"></script>
  <script src="//cdn.jsdelivr.net//npm/graphiql-subscriptions-fetcher@0.0.2/browser/client.js"></script>
</head>
<body>
  <div class="jwt-token">JWT Token <input id="jwt-token" placeholder="JWT Token goes here"></div>
  <div id="graphiql">Loading...</div>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });

    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }

    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };

    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }

    var subscriptionsFetcher;
    if ('{{subscriptions}}') {
      const subscriptionsClient = new SubscriptionsTransportWs.SubscriptionClient(
        '{{ subscriptions }}',
        {reconnect: true}
      );

      subscriptionsFetcher = GraphiQLSubscriptionsFetcher.graphQLFetcher(
        subscriptionsClient,
        graphQLFetcher
      );
    }

    var fetchURL = locationQuery(otherParams);
    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams) {
      const jwtToken = document.getElementById('jwt-token').value;
      let headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };
      if (jwtToken) {
        headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-API-Key': jwtToken ? `Bearer ${jwtToken}` : null
        };
      }
      return fetch(fetchURL, {
        method: 'post',
        headers: headers,
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.text();
      }).then(function (responseBody) {
        try {
          return JSON.parse(responseBody);
        } catch (error) {
          return responseBody;
        }
      });
    }

    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }

    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }

    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }

    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }

    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: subscriptionsFetcher || graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditOperationName: onEditOperationName,
        query: {{query|tojson}},
        response: {{result|tojson}},
        variables: {{variables|tojson}},
        operationName: {{operation_name|tojson}},
      }),
      document.getElementById('graphiql')
    );
  </script>
</body>
</html>"""


def error_formatter(error: Exception) -> dict:
    """
    Error formatter for GraphQL queries

    Args:
        error: query error

    Returns: dictionary formatted error

    """
    if isinstance(error, GraphQLLocatedError):
        error = error.original_error
    LOGGER.error('Error in GraphQL query', exc_info=(type(error), error, error.__traceback__))
    return dict(error=error.__class__.__name__, detail=str(error))


def setup_routes(app: Application):
    """
    Add the graphql routes to the specified application

    Args:
        app: application to add routes

    """
    GraphQLView.attach(app,
                       schema=schema,
                       graphiql=True,
                       graphiql_template=GRAPHIQL_JWT_TEMPLATE,
                       route_path='/graphql',
                       executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
                       enable_async=True,
                       error_formatter=error_formatter)
