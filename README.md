# Wildcard DNS server

Experimental Docker image for a DNS server implementing ``xip.io`` style
DNS wildcards, more conventional glob style DNS wildcard mappings, as well
as pass through for all other lookups.

This could be done using a very lightweight Docker image, but I am using
the Twisted framework from Python as it more easily allows me to experiment
with intercepting DNS lookups for other purposes.

## Building the image

To build the image:

```
docker build -t wildcard-dns .
```

## Running the image

Use Docker to run the image. When doing this you should map ports for both
TCP and UDP ports of the DNS server.

```
docker run -e --rm -p 53:10053/tcp -p 53:10053/udp wildcard-dns
```

By default the IP wildcards will use the ``xip.io`` domain as the default.
To override the domain use the ``WILDCARD_DOMAIN`` environment variable.

```
docker run --rm -p 53:10053/tcp -p 53:10053/udp \
 -e WILDCARD_DOMAIN=wildcard.dev wildcard-dns-server
```

To test that the latter works, use the command:

```
dig @$(docker-machine ip default) myapp.10.2.2.2.wildcard.dev A +short
```

In this example, you should get the result ``10.2.2.2``. Also try with other
valid public addresses such as ``www.google.com`` and you should get back a
list of the IPs for that service.

By default Google DNS servers are used as fallback. If you wish to use
alternate name servers, you can specify them using the ``NAME_SERVERS``
environment variable when running the image. The value should be a comma
separate list of name server hosts. An optional port may be specified for
any host by including it after the host name, separated by a ':'.

To provide a mapping of explicit host names, or using glob style DNS
wildcard matches, you need to supply a JSON file defining the mappings.

```
{
    "*.foo.com": "127.0.0.1",
    "www.bar.com": "bar.com",
    "bar.com": "127.0.0.1",
    "search.com": "www.google.com"
}
```

The target of the match should be an IP address, or a host name. Where it
maps to a host name, that should be resolvable via subsequent applications
of the mapping table, or via a public DNS lookup.

To get the mapping table into the running image, you should use volume
mounting, as well as use the ``MAPPED_HOSTS`` environment variable to
specify the location of the JSON file.

```
docker run -e --rm -p 53:10053/tcp -p 53:10053/udp \
 -e MAPPED_HOSTS=/usr/src/app/etc/mappings.json \
 -v `pwd`/etc:/usr/src/app/etc wildcard-dns-server
```

## Using registry image

If you don't want to build the image yourself and are happy to trust an
automated build image from Docker Hub Registry, then you can pull it down
from there.

```
docker pull kubegd/wildcard-dns
```

The image uses the official Docker ``python:3.6`` image as the base
image. As per best practice security measures, the image is set up not to
run as root, using the default ``www-data`` user.

## Update your DNS settings

Once you are happy that the image is running okay, then update the DNS
settings of your system to point at the IP address of the Docker service
host. You can get the IP address of the Docker service host by running:

```
docker-machine ip default
```

Note that for some systems, eg., MacOS X, there is no DNS active at all
when you have no active WiFi or Ethernet connection. You cannot therefore
readily still use this to allow local offline development for ``xip.io``
style addresses. You would in this case still need to be connected to an
ethernet router, or need something like a physical ethernet loop back
dongle to trick the operating system into thinking you have an actual
connection.

## Debugging DNS lookups

To debug DNS lookups as they pass through the DNS server implemented by
the image, you can set the ``DEBUG`` environment variable.

```
docker run --rm -p 53:10053/tcp -p 53:10053/udp \
 -e DEBUG=True -e WILDCARD_DOMAIN=wildcard.dev wildcard-dns
```

At the highest level you can see wildcard DNS name matches, as well as pass
through requests.

```
2018-04-11 05:31:23,179     gd.kube.dns:033  INFO: nameservers [('8.8.8.8', 53), ('8.8.4.4', 53)]
2018-04-11 05:31:23,180     gd.kube.dns:044  INFO: wildcard .*\.(?P<ipaddr>\d+\.\d+\.\d+\.\d+)\.dns\.kube\.gd
2018-04-11 05:31:23,180     gd.kube.dns:067  INFO: mapping (?P<RULE1>.*\.kube\.gd)
2018-04-11 05:31:23,180     gd.kube.dns:068  INFO: results {'RULE1': '18.218.181.63'}
2018-04-11 05:31:41,831     gd.kube.dns:103 DEBUG: address dns.kube.gd
2018-04-11 05:31:41,831     gd.kube.dns:074 DEBUG: lookup dns.kube.gd
2018-04-11 05:31:41,831     gd.kube.dns:096 DEBUG: mapping dns.kube.gd --> 18.218.181.63
```
