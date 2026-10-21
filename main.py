import argparse
import logging
import sys
from threading import Thread

from sawtooth_client import SawtoothClient
from sawtooth_subscriber import SawtoothSubscriber
from lib.common import init_logger, SubscriberError
from docker_monitor import DockerMonitor
from docker_starter import DockerStarter

LOGGER = logging.getLogger(__name__)


def main():
    try:
        opts = parse_args(sys.argv[1:])
        init_logger(opts.verbose)

        LOGGER.info('Starting Service...')

        node_count = int(opts.node_count)
        node_template = opts.node_template
        boot_node = opts.boot_node
        docker_starter = DockerStarter(node_count, node_template, boot_node)

        docker_starter.generate_nodes()
        docker_starter.start_services()

        benchmark = opts.benchmark

        # An empty service list makes the monitor record every running container.
        monitor = DockerMonitor(benchmark=benchmark)
        monitor.start()

        publisher_url = opts.publisher_url
        server_node_url = opts.server_node_url
        load = int(opts.load)
        client = SawtoothClient(publisher_url, server_node_url, load, benchmark)

        # Subscribe before sending any load so that no event is missed.
        subscriber = SawtoothSubscriber(publisher_url, benchmark, load)
        subscriber.subscribe_to_event()
        subscriber_thread = Thread(target=subscriber.run, daemon=True)
        subscriber_thread.start()

        client.generate_load()
        client.start_load()

        LOGGER.info('Waiting up to {}s for events'.format(opts.event_timeout))
        subscriber_thread.join(timeout=float(opts.event_timeout))
        if subscriber_thread.is_alive():
            LOGGER.warning('Received {} of {} events before timeout'.format(subscriber.counter, load))
        monitor.stop()

    except (KeyboardInterrupt, SubscriberError):
        sys.exit(0)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase level of output sent to stderr')

    parser.add_argument('--node_count',
                        help='Number of nodes in the network',
                        default=4)

    parser.add_argument('--node_template',
                        help='Docker compose template of the standard nodes',
                        default='docker-compose-node.yaml')

    parser.add_argument('--boot_node',
                        help='Docker compose of the Boot if any',
                        default=None)

    parser.add_argument('--publisher_url',
                        help='Host of the validator to subscribe to events on (port 4004)',
                        default='localhost')

    parser.add_argument('--server_node_url',
                        help='Host of the REST API to send transactions to (port 8008)',
                        default='localhost')

    parser.add_argument('--load',
                        help='Number of transactions sent to the network',
                        default=0)

    parser.add_argument('--benchmark',
                        help='Name of the benchmark',
                        default='do-nothing')

    parser.add_argument('--event_timeout',
                        help='Seconds to wait for all events after the load was sent',
                        default=60)

    return parser.parse_args(args)


if __name__ == '__main__':
    main()
