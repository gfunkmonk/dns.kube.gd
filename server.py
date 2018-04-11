
import os
import re
import json
import string
import logging

from twisted.internet import (
    reactor,
    defer,
)
from twisted.names import (
    client,
    dns,
    server,
)

log = logging.getLogger('gd.kube.dns')


class DynamicResolver(client.Resolver):
    """
    A resolver which implements xip.io style IP resolution based on name.
    as well as more conventional glob style DNS wildcard mapping. If no
    match will fallback to specified DNS server for lookup.

    """

    def __init__(self, servers, wildcard_domain, mapped_hosts=None):

        client.Resolver.__init__(self, servers=servers)

        log.info('nameservers %s' % servers)

        # Create regex pattern corresponding to xip.io style DNS
        # wilcard domain.

        pattern = (
            r'.*\.(?P<ipaddr>\d+\.\d+\.\d+\.\d+)\.{}'.format(
                re.escape(wildcard_domain)
            )
        )

        log.info('wildcard {}'.format(pattern))

        self._wildcard = re.compile(pattern)

        # Create regex pattern corresponding to conventional glob
        # style DNS wildcard mapping.

        self._mapping = None

        count = 1
        patterns = []
        results = {}

        if mapped_hosts:
            for inbound, outbound in mapped_hosts.items():
                label = 'RULE%s' % count
                inbound = re.escape(inbound).replace('\\*', '.*')
                patterns.append('(?P<%s>%s)' % (label, inbound))
                results[label] = outbound
                count += 1

            pattern = '|'.join(patterns)

            log.info('mapping {}'.format(pattern))
            log.info('results {}'.format(results))

            self._mapping = re.compile(pattern)
            self._mapping_results = results

    def _localLookup(self, name):
        log.debug('lookup {}'.format(name))

        # First try and map xip.io style DNS wildcard.

        match = self._wildcard.match(name)

        if match:
            ipaddr = match.group('ipaddr')
            log.debug('wildcard {} --> {}'.format(name, ipaddr))
            return ipaddr

        # Next try and map conventional glob style wildcard mapping.

        if self._mapping is None:
            return

        match = self._mapping.match(name)

        if match:
            label = [k for k, v in match.groupdict().items() if v].pop()
            result = self._mapping_results[label]

            log.debug('mapping {} --> {}'.format(name, result))

            return result

    def lookupAddress(self, name, timeout=None):
        name = name.decode()

        log.debug('address {}'.format(name))

        result = self._localLookup(name)

        # If doesn't look like an IP address, try and look it up again
        # locally. Do this as many times as need to. Note there is no
        # protection against loops here.

        while result and result[0] not in string.digits:
            mapped = self._localLookup(result)
            if mapped is not None:
                result = mapped
            else:
                break

        if result:
            # Check if looks like IP address. If still not treat it like
            # a CNAME and lookup name using normal DNS lookup.

            if result[0] not in string.digits:
                log.debug('cname {}'.format(result))
                return client.Resolver.lookupAddress(self, result, timeout)

            try:
                payload = dns.Record_A(address=result)
            except OSError as e:
                log.warn(str(e))
                return defer.succeed(([], [], []))

            answer = dns.RRHeader(name=name, payload=payload)

            answers = [answer]
            authority = []
            additional = []

            return defer.succeed((answers, authority, additional))

        else:
            log.debug('fallback {}'.format(name))
            return client.Resolver.lookupAddress(self, name, timeout)


def setup_logging(debug=False):
    logfmt = '%(asctime)s %(name)15s:%(lineno)03d %(levelname)5s: %(message)s'

    logging.basicConfig(
        level=logging.DEBUG,
        format=logfmt,
    )


def main(port=53, domain='xip.io', nameservers=None, mapped_hosts=None):

    server_list = []
    nameservers = nameservers or '8.8.8.8,8.8.4.4'

    for address in nameservers.split(','):
        parts = address.strip().split(':')
        if len(parts) > 1:
            server_list.append((parts[0], int(parts[1])))
        elif parts:
            server_list.append((parts[0], 53))

    factory = server.DNSServerFactory(
        clients=[
            DynamicResolver(
                servers=server_list,
                wildcard_domain=domain,
                mapped_hosts=mapped_hosts,
            )
        ]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()


if __name__ == '__main__':

    setup_logging(os.environ.get('DEBUG', False))

    mapping_json = os.environ.get('MAPPED_HOSTS')
    mapped_hosts = {}

    if mapping_json and os.path.exists(mapping_json):
        with open(mapping_json) as fp:
            mapped_hosts = json.load(fp)

    raise SystemExit(
        main(
            os.environ.get('PORT', 10053),
            os.environ.get('WILDCARD_DOMAIN'),
            os.environ.get('NAME_SERVERS'),
            mapped_hosts,
        )
    )
