"""
Cron definitions:
    class: cron implementation class
    expression: cron expression
    source_adapters: adapters used to get items
    **key_params: parameters required by the cron functionality
"""
from adapters.xml_event_endpoint_adapter import XmlEventEndpointAdapter
from cron.implementations.fetch_events_implementation import FetchEventsImplementation

definitions = {
    'fetch_events': {
        'class': FetchEventsImplementation,
        'expression': '*/5 * * * *',
        'source_adapters': [XmlEventEndpointAdapter],
        'event_source_url':
            'https://gist.githubusercontent.com/miguelgf/2885fe812638bfb33f785a977f8b7e3c'
            '/raw/0bef14cee7d8beb07ec9dabd6b009499f65b85f0/response.xml'
    }
}
